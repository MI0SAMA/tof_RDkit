"""Background task worker for network generation."""

import json
import os
import traceback
from datetime import datetime
from pathlib import Path

from .database import SessionLocal
from .models import FormulaSummary, ImportLog, Material, NetworkEdge, NetworkNode, Task


def _task_paths() -> Path:
    """Get writable directory for task outputs."""
    d = Path(os.environ.get("TASK_OUTPUT_DIR", "/app/web_data/tasks"))
    d.mkdir(parents=True, exist_ok=True)
    return d


def run_generate_network(task_id: str, compound_id: str, smiles: str, formula: str, config_overrides: dict | None = None):
    """Generate formula network for a given SMILES in the background."""
    db = SessionLocal()
    try:
        # 1. Update task status to running
        task = db.query(Task).filter(Task.task_id == task_id).first()
        if not task:
            return
        task.status = "running"
        task.current_step = "Loading config and molecule"
        task.progress = 5
        db.commit()

        # 2. Import project modules (requires RDKit)
        import yaml

        from tofsims_formula_network.molecule_io import get_formula_from_mol, mol_from_smiles
        from tofsims_formula_network.network_v2 import generate_formula_network_v2

        # Load config
        config_path = Path(os.environ.get("CONFIG_DIR", "/app/config")) / "default.yaml"
        with open(config_path) as f:
            config = yaml.safe_load(f)

        if config_overrides:
            _deep_update(config, config_overrides)

        task.current_step = "Parsing SMILES with RDKit"
        task.progress = 15
        db.commit()

        # 3. Parse molecule
        mol = mol_from_smiles(smiles)
        if not formula:
            formula = get_formula_from_mol(mol)

        task.current_step = "Generating fragment nodes"
        task.progress = 30
        db.commit()

        # 4. Generate network
        compound_row = {
            "compound_id": compound_id,
            "name": compound_id,
            "smiles": smiles,
            "formula": formula,
        }

        task.current_step = "Running fragmentation + feature rules"
        task.progress = 50
        db.commit()

        nodes, edges, summaries = generate_formula_network_v2(compound_row, config)

        task.current_step = f"Storing {len(nodes)} nodes + {len(edges)} edges"
        task.progress = 85
        db.commit()

        # 5. Store in database
        # Clear previous data for this compound
        db.query(NetworkNode).filter(NetworkNode.compound_id == compound_id).delete()
        db.query(NetworkEdge).filter(NetworkEdge.compound_id == compound_id).delete()
        db.query(FormulaSummary).filter(FormulaSummary.compound_id == compound_id).delete()

        # Store nodes
        for node in nodes:
            path_raw = node.path
            path_str = " | ".join(path_raw) if isinstance(path_raw, list) else str(path_raw)
            source_raw = node.source_nodes
            source_str = ";".join(source_raw) if isinstance(source_raw, list) else str(source_raw)

            db_node = NetworkNode(
                compound_id=compound_id,
                node_id=node.node_id,
                formula=node.formula,
                ion_mode=node.ion_mode,
                charge=node.charge,
                exact_mass=node.exact_mass,
                generation_type=node.generation_type,
                operation=node.operation,
                rule_pack=node.rule_pack,
                trigger_feature=node.trigger_feature,
                evidence=node.evidence,
                path_score=node.path_score,
                formula_score=node.formula_score,
                structure_score=node.structure_score,
                ionization_score=node.ionization_score,
                broken_bonds=node.broken_bonds,
                h_shift=node.h_shift,
                path=path_str,
                source_nodes=source_str,
            )
            db.add(db_node)

        # Store edges
        for edge in edges:
            db_edge = NetworkEdge(
                compound_id=compound_id,
                edge_id=edge.edge_id,
                source_node=edge.source_node,
                target_node=edge.target_node,
                operation=edge.operation,
                operation_type=edge.operation_type,
                weight=edge.weight,
            )
            db.add(db_edge)

        # Store formula summaries
        for summary in summaries:
            fs = FormulaSummary(
                compound_id=compound_id,
                source_name=compound_id,
                formula=summary.formula,
                ion_mode=summary.ion_mode,
                charge=summary.charge,
                exact_mass=summary.exact_mass,
                formula_score=summary.formula_score,
                best_path_score=summary.best_path_score,
                path_count=summary.path_count,
                mechanism_count=summary.mechanism_count,
                source_fragment_count=summary.source_fragment_count,
                generation_types=summary.generation_types,
                best_node_id=summary.best_node_id,
                representative_path=summary.representative_path,
                all_node_ids=summary.all_node_ids,
                diagnostic_tag="structural_candidate_only",
                material_diagnostic_score=0.1,
                is_hidden=True,
                is_generic_hc=False,
            )
            db.add(fs)

        db.commit()

        # 6. Update material record
        mat = db.query(Material).filter(Material.compound_id == compound_id).first()
        if not mat:
            mat = Material(
                compound_id=compound_id,
                name=compound_id,
                smiles=smiles,
                formula=formula,
                group="custom",
                material_type="custom",
                notes="Generated via web UI",
                has_manual_labels=False,
            )
            db.add(mat)

        # 7. Mark task complete
        task.status = "completed"
        task.progress = 100
        task.current_step = f"Done: {len(nodes)} nodes, {len(edges)} edges, {len(summaries)} formulas"
        task.finished_at = datetime.utcnow()
        db.commit()

        # 8. Write JSON output to task directory
        from tofsims_formula_network.network_v2 import write_network_v2
        task_output_dir = _task_paths() / task_id
        write_network_v2(nodes, edges, summaries, task_output_dir, compound_row)
        task.log_path = str(task_output_dir)
        db.commit()

    except Exception as e:
        db.rollback()
        task = db.query(Task).filter(Task.task_id == task_id).first()
        if task:
            task.status = "failed"
            task.error_message = f"{type(e).__name__}: {e}"
            task.current_step = "Failed"
            task.finished_at = datetime.utcnow()
            task.log_path = traceback.format_exc()
            db.commit()
    finally:
        db.close()


def _deep_update(base: dict, overrides: dict):
    """Recursively update nested dict."""
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            _deep_update(base[key], value)
        else:
            base[key] = value
