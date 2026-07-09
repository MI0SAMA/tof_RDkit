"""Business logic for importing existing v3.0 results and serving data."""

import json
import math
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

from .models import (
    EvidenceReport,
    FormulaSummary,
    ImportLog,
    Material,
    NetworkEdge,
    NetworkNode,
)

# Data directories - configurable via env vars
DATA_DIR = Path(os.environ.get("DATA_DIR", Path(__file__).resolve().parent.parent.parent / "data"))
OUTPUTS_DIR = Path(os.environ.get("OUTPUTS_DIR", Path(__file__).resolve().parent.parent.parent / "outputs"))
NETWORKS_V2_DIR = OUTPUTS_DIR / "networks_v2"
SUMMARY_DIR = OUTPUTS_DIR / "summary"


def _safe_str(val, default="") -> str:
    """Convert value to string, handling NaN/None."""
    if val is None:
        return default
    try:
        if isinstance(val, float) and math.isnan(val):
            return default
    except TypeError:
        pass
    return str(val)


def _safe_float(val, default=0.0) -> float:
    """Convert value to float, handling NaN/None."""
    if val is None:
        return default
    try:
        f = float(val)
        if math.isnan(f):
            return default
        return f
    except (ValueError, TypeError):
        return default


def _safe_int(val, default=0) -> int:
    """Convert value to int, handling NaN/None."""
    if val is None:
        return default
    try:
        f = float(val)
        if math.isnan(f):
            return default
        return int(f)
    except (ValueError, TypeError):
        return default


def import_all(db: Session) -> dict:
    """Import all existing v3.0 results into web.sqlite."""
    results = {
        "materials": _import_materials(db),
        "formulas": _import_formulas(db),
        "networks": _import_networks(db),
        "evidence": _import_evidence(db),
    }
    db.commit()
    return results


def _import_materials(db: Session) -> dict:
    """Import materials from compounds.csv."""
    compounds_path = DATA_DIR / "compounds.csv"
    if not compounds_path.exists():
        return {"status": "skipped", "message": f"compounds.csv not found at {compounds_path}", "count": 0}

    df = pd.read_csv(compounds_path)
    count = 0
    for _, row in df.iterrows():
        compound_id = str(row.get("compound_id", ""))
        if not compound_id:
            continue
        existing = db.query(Material).filter(Material.compound_id == compound_id).first()
        if existing:
            existing.name = _safe_str(row.get("name"), existing.name)
            existing.smiles = _safe_str(row.get("smiles"), existing.smiles or "")
            # Clean formula: ignore 'nan' string from previous buggy import
            old_formula = existing.formula if (existing.formula and existing.formula != "nan") else ""
            existing.formula = _safe_str(row.get("formula"), old_formula)
            existing.group = _safe_str(row.get("group"), existing.group or "")
            existing.notes = _safe_str(row.get("notes"), existing.notes or "")
        else:
            material = Material(
                compound_id=compound_id,
                name=_safe_str(row.get("name"), ""),
                smiles=_safe_str(row.get("smiles"), ""),
                formula=_safe_str(row.get("formula"), ""),
                group=_safe_str(row.get("group"), ""),
                material_type="pure_polymer",
                notes=_safe_str(row.get("notes"), ""),
                has_manual_labels=compound_id in {"COC", "EVA", "PDMS", "PET", "POMC", "POMH"},
            )
            db.add(material)
        count += 1

    log = ImportLog(
        import_type="materials",
        file_path=str(compounds_path),
        status="completed",
        records_imported=count,
        message=f"Imported {count} materials",
    )
    db.add(log)
    return {"status": "completed", "count": count}


def _import_formulas(db: Session) -> dict:
    """Import formula summaries. Prefers specificity CSV, falls back to per-material CSVs."""
    specificity_path = SUMMARY_DIR / "formula_summary_with_specificity.csv"
    if specificity_path.exists():
        return _import_from_csv(db, specificity_path)
    # Fallback to per-material CSVs
    if not NETWORKS_V2_DIR.exists():
        return {"status": "skipped", "message": "networks_v2 dir not found", "count": 0}
    count = 0
    db.query(FormulaSummary).delete()
    for csv_path in sorted(NETWORKS_V2_DIR.glob("*_formula_summary.csv")):
        try:
            df = pd.read_csv(csv_path)
        except Exception:
            continue
        for _, row in df.iterrows():
            formula = _build_formula(row, default_tag="")
            db.add(formula)
            count += 1
    db.add(ImportLog(import_type="formulas", file_path=str(NETWORKS_V2_DIR), status="completed", records_imported=count,
                     message=f"Imported {count} formula summaries from per-material CSVs"))
    return {"status": "completed", "count": count}


def _import_from_csv(db: Session, csv_path: Path) -> dict:
    """Import from a single combined CSV."""
    df = pd.read_csv(csv_path)
    db.query(FormulaSummary).delete()
    count = 0
    for _, row in df.iterrows():
        formula = _build_formula(row, default_tag="structural_candidate_only")
        db.add(formula)
        count += 1
    db.add(ImportLog(import_type="formulas", file_path=str(csv_path), status="completed", records_imported=count,
                     message=f"Imported {count} formula summaries"))
    return {"status": "completed", "count": count}


def _build_formula(row, default_tag: str = "") -> FormulaSummary:
    """Build a FormulaSummary from a CSV row."""
    diagnostic_tag = _safe_str(row.get("diagnostic_tag"), default_tag)
    is_hidden = diagnostic_tag == "structural_candidate_only"
    is_generic_hc = diagnostic_tag == "generic_hydrocarbon_background"
    return FormulaSummary(
        compound_id=_safe_str(row.get("compound_id"), ""),
        source_name=_safe_str(row.get("source_name"), ""),
        formula=_safe_str(row.get("formula"), ""),
        ion_mode=_safe_str(row.get("ion_mode"), "neutral"),
        charge=_safe_int(row.get("charge"), 0),
        exact_mass=_safe_float(row.get("exact_mass"), 0.0),
        formula_score=_safe_float(row.get("formula_score"), 0.0),
        best_path_score=_safe_float(row.get("best_path_score"), 0.0),
        path_count=_safe_int(row.get("path_count"), 1),
        mechanism_count=_safe_int(row.get("mechanism_count"), 1),
        source_fragment_count=_safe_int(row.get("source_fragment_count"), 0),
        generation_types=_safe_str(row.get("generation_types"), ""),
        best_node_id=_safe_str(row.get("best_node_id"), ""),
        representative_path=_safe_str(row.get("representative_path"), ""),
        all_node_ids=_safe_str(row.get("all_node_ids"), ""),
        diagnostic_tag=diagnostic_tag,
        material_diagnostic_score=_safe_float(row.get("material_diagnostic_score"), 0.0),
        is_hidden=is_hidden,
        is_generic_hc=is_generic_hc,
    )


def _import_networks(db: Session) -> dict:
    """Import network nodes and edges from networks_v2 JSON files."""
    if not NETWORKS_V2_DIR.exists():
        return {"status": "skipped", "message": "networks_v2 dir not found", "count": 0}

    db.query(NetworkNode).delete()
    db.query(NetworkEdge).delete()

    node_count = 0
    edge_count = 0
    material_count = 0

    for json_file in sorted(NETWORKS_V2_DIR.glob("*.json")):
        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
            compound_id = data.get("compound_id", json_file.stem)

            for node_data in data.get("nodes", []):
                path_raw = node_data.get("path", [])
                if isinstance(path_raw, list):
                    path_str = " | ".join(path_raw)
                else:
                    path_str = str(path_raw)

                source_raw = node_data.get("source_nodes", [])
                if isinstance(source_raw, list):
                    source_str = ";".join(source_raw)
                else:
                    source_str = str(source_raw)

                node = NetworkNode(
                    compound_id=compound_id,
                    node_id=str(node_data.get("node_id", "")),
                    formula=str(node_data.get("formula", "")),
                    ion_mode=str(node_data.get("ion_mode", "neutral")),
                    charge=int(node_data.get("charge", 0)),
                    exact_mass=float(node_data.get("exact_mass", 0.0)),
                    generation_type=str(node_data.get("generation_type", "")),
                    operation=str(node_data.get("operation", "")),
                    rule_pack=str(node_data.get("rule_pack", "")),
                    trigger_feature=str(node_data.get("trigger_feature", "")),
                    evidence=str(node_data.get("evidence", "")),
                    path_score=float(node_data.get("path_score", 0.0)),
                    formula_score=float(node_data.get("formula_score", 0.0)),
                    structure_score=float(node_data.get("structure_score", 0.0)),
                    ionization_score=float(node_data.get("ionization_score", 0.0)),
                    broken_bonds=int(node_data.get("broken_bonds", 0)),
                    h_shift=int(node_data.get("h_shift", 0)),
                    path=path_str,
                    source_nodes=source_str,
                )
                db.add(node)
                node_count += 1

            for edge_data in data.get("edges", []):
                edge = NetworkEdge(
                    compound_id=compound_id,
                    edge_id=str(edge_data.get("edge_id", "")),
                    source_node=str(edge_data.get("source_node", "")),
                    target_node=str(edge_data.get("target_node", "")),
                    operation=str(edge_data.get("operation", "")),
                    operation_type=str(edge_data.get("operation_type", "")),
                    weight=float(edge_data.get("weight", 1.0)),
                )
                db.add(edge)
                edge_count += 1

            material_count += 1
        except Exception as exc:
            log = ImportLog(
                import_type="network_error",
                file_path=str(json_file),
                status="error",
                message=str(exc),
            )
            db.add(log)

    log = ImportLog(
        import_type="networks",
        file_path=str(NETWORKS_V2_DIR),
        status="completed",
        records_imported=node_count + edge_count,
        message=f"Imported {node_count} nodes + {edge_count} edges for {material_count} materials",
    )
    db.add(log)
    return {"status": "completed", "nodes": node_count, "edges": edge_count, "materials": material_count}


def _import_evidence(db: Session) -> dict:
    """Import evidence report data."""
    evidence_path = SUMMARY_DIR / "evidence_report.csv"
    if not evidence_path.exists():
        return {"status": "skipped", "message": "evidence_report.csv not found", "count": 0}

    df = pd.read_csv(evidence_path)
    db.query(EvidenceReport).delete()

    count = 0
    for _, row in df.iterrows():
        report = EvidenceReport(
            compound_id=_safe_str(row.get("material"), ""),
            total_formulas=_safe_int(row.get("total_formulas"), 0),
            val_diag=_safe_int(row.get("val_diag"), 0),
            val_gen=_safe_int(row.get("val_gen"), 0),
            feat_supp=_safe_int(row.get("feat_supp"), 0),
            gen_hc=_safe_int(row.get("gen_hc"), 0),
            struct_only=_safe_int(row.get("struct_only"), 0),
            formula_evidence=_safe_str(row.get("formula_evidence"), ""),
            pattern_evidence=_safe_str(row.get("pattern_evidence"), ""),
            pom_pattern_score=_safe_float(row.get("pom_pattern_score"), 0.0),
            background_level=_safe_str(row.get("background_level"), ""),
            final_evidence=_safe_str(row.get("final_evidence"), ""),
        )
        db.add(report)
        count += 1

    log = ImportLog(
        import_type="evidence",
        file_path=str(evidence_path),
        status="completed",
        records_imported=count,
        message=f"Imported {count} evidence reports",
    )
    db.add(log)
    return {"status": "completed", "count": count}


def get_dashboard_data(db: Session) -> dict:
    """Aggregate dashboard statistics."""
    evidence_reports = db.query(EvidenceReport).all()
    materials = db.query(Material).all()

    # Load evaluation match rates from CSV
    match_rates = _load_match_rates()

    total_formulas = sum(r.total_formulas for r in evidence_reports)
    total_val_diag = sum(r.val_diag for r in evidence_reports)
    total_val_gen = sum(r.val_gen for r in evidence_reports)
    total_struct_only = sum(r.struct_only for r in evidence_reports)
    total_gen_hc = sum(r.gen_hc for r in evidence_reports)
    hidden_ratio = total_struct_only / max(total_formulas, 1)

    strategies = {}
    for r in evidence_reports:
        strategies[r.final_evidence] = strategies.get(r.final_evidence, 0) + 1

    material_cards = []
    for r in evidence_reports:
        mat = next((m for m in materials if m.compound_id == r.compound_id), None)
        mr = match_rates.get(r.compound_id, {})
        material_cards.append({
            "compound_id": r.compound_id,
            "name": mat.name if mat else r.compound_id,
            "group": mat.group if mat else "",
            "total_formulas": r.total_formulas,
            "val_diag": r.val_diag,
            "val_gen": r.val_gen,
            "feat_supp": r.feat_supp,
            "gen_hc": r.gen_hc,
            "struct_only": r.struct_only,
            "val_diag_pct": round(r.val_diag / max(r.total_formulas, 1) * 100, 1),
            "match_rate": mr.get("avg", 0),
            "match_rate_pos": mr.get("positive"),
            "match_rate_neg": mr.get("negative"),
            "formula_evidence": r.formula_evidence,
            "pattern_evidence": r.pattern_evidence,
            "final_evidence": r.final_evidence,
            "pom_pattern_score": r.pom_pattern_score,
            "background_level": r.background_level,
        })

    return {
        "global": {
            "total_materials": len(materials),
            "total_formulas": total_formulas,
            "total_val_diag": total_val_diag,
            "total_val_gen": total_val_gen,
            "total_struct_only": total_struct_only,
            "total_gen_hc": total_gen_hc,
            "hidden_ratio": round(hidden_ratio * 100, 1),
            "strategy_distribution": strategies,
        },
        "materials": sorted(material_cards, key=lambda x: -x["match_rate"]),
    }


def _load_match_rates() -> dict[str, dict[str, float]]:
    """Load per-material, per-polarity match rates from evaluation summary CSV.

    Returns {material_id: {"positive": rate, "negative": rate, "avg": rate}}
    """
    csv_path = SUMMARY_DIR / "network_v2_evaluation_summary.csv"
    if not csv_path.exists():
        return {}
    try:
        df = pd.read_csv(csv_path)
        rates = {}
        for material in df["material"].unique():
            mat_df = df[df["material"] == material]
            pos = mat_df[mat_df["ion_mode"] == "positive"]["network_recall"]
            neg = mat_df[mat_df["ion_mode"] == "negative"]["network_recall"]
            pos_val = round(float(pos.iloc[0]) * 100, 1) if len(pos) > 0 else None
            neg_val = round(float(neg.iloc[0]) * 100, 1) if len(neg) > 0 else None
            avg_val = round(mat_df["network_recall"].mean() * 100, 1)
            rates[material] = {"positive": pos_val, "negative": neg_val, "avg": avg_val}
        return rates
    except Exception:
        return {}


def get_material_network(compound_id: str, db: Session, hide_struct_only: bool = True) -> dict:
    """Get network data for visualization."""
    hidden_nodes: set[str] = set()
    if hide_struct_only:
        hidden_formulas = (
            db.query(FormulaSummary)
            .filter(
                FormulaSummary.compound_id == compound_id,
                FormulaSummary.is_hidden == True,  # noqa: E712
            )
            .all()
        )
        for fs in hidden_formulas:
            if fs.all_node_ids:
                for nid in fs.all_node_ids.split(";"):
                    hidden_nodes.add(nid.strip())

    nodes = (
        db.query(NetworkNode)
        .filter(NetworkNode.compound_id == compound_id)
        .all()
    )

    edges = (
        db.query(NetworkEdge)
        .filter(NetworkEdge.compound_id == compound_id)
        .all()
    )

    formula_map = {}
    for fs in db.query(FormulaSummary).filter(FormulaSummary.compound_id == compound_id).all():
        key = (fs.formula, fs.ion_mode, fs.charge)
        formula_map[key] = {
            "diagnostic_tag": fs.diagnostic_tag,
            "formula_score": fs.formula_score,
            "is_hidden": fs.is_hidden,
            "is_generic_hc": fs.is_generic_hc,
        }

    visible_nodes = []
    for n in nodes:
        if hide_struct_only and n.node_id in hidden_nodes:
            continue
        key = (n.formula, n.ion_mode, n.charge)
        info = formula_map.get(key, {})
        visible_nodes.append({
            "node_id": n.node_id,
            "formula": n.formula,
            "ion_mode": n.ion_mode,
            "charge": n.charge,
            "exact_mass": n.exact_mass,
            "generation_type": n.generation_type,
            "operation": n.operation,
            "rule_pack": n.rule_pack,
            "trigger_feature": n.trigger_feature,
            "path_score": n.path_score,
            "formula_score": n.formula_score,
            "structure_score": n.structure_score,
            "path": n.path,
            "diagnostic_tag": info.get("diagnostic_tag", ""),
            "is_generic_hc": info.get("is_generic_hc", False),
        })

    visible_node_ids = {n["node_id"] for n in visible_nodes}
    visible_edges = []
    for e in edges:
        if e.source_node in visible_node_ids and e.target_node in visible_node_ids:
            visible_edges.append({
                "edge_id": e.edge_id,
                "source_node": e.source_node,
                "target_node": e.target_node,
                "operation": e.operation,
                "operation_type": e.operation_type,
                "weight": e.weight,
            })

    return {
        "compound_id": compound_id,
        "nodes": visible_nodes,
        "edges": visible_edges,
        "node_count": len(visible_nodes),
        "edge_count": len(visible_edges),
    }
