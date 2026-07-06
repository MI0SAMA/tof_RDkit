"""Export API routes."""

import csv
import io
import json

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import EvidenceReport, FormulaSummary, NetworkEdge, NetworkNode

router = APIRouter(prefix="/api/export", tags=["export"])


@router.get("/formulas")
def export_formulas(
    material_id: str = Query(None),
    format: str = Query("csv"),
    hide_struct_only: bool = Query(True),
    db: Session = Depends(get_db),
):
    """Export formulas as CSV or JSON."""
    query = db.query(FormulaSummary)
    if material_id:
        query = query.filter(FormulaSummary.compound_id == material_id)
    if hide_struct_only:
        query = query.filter(FormulaSummary.is_hidden == False)  # noqa: E712

    items = query.order_by(FormulaSummary.formula_score.desc()).all()

    if format == "json":
        data = [
            {
                "compound_id": f.compound_id,
                "formula": f.formula,
                "ion_mode": f.ion_mode,
                "charge": f.charge,
                "exact_mass": f.exact_mass,
                "formula_score": f.formula_score,
                "diagnostic_tag": f.diagnostic_tag,
                "generation_types": f.generation_types,
                "representative_path": f.representative_path,
            }
            for f in items
        ]
        return StreamingResponse(
            io.BytesIO(json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=formulas.json"},
        )

    # CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "compound_id", "formula", "ion_mode", "charge", "exact_mass",
        "formula_score", "diagnostic_tag", "generation_types", "representative_path",
    ])
    for f in items:
        writer.writerow([
            f.compound_id, f.formula, f.ion_mode, f.charge, f.exact_mass,
            f.formula_score, f.diagnostic_tag, f.generation_types, f.representative_path,
        ])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=formulas.csv"},
    )


@router.get("/evidence")
def export_evidence(format: str = Query("markdown"), db: Session = Depends(get_db)):
    """Export evidence report as Markdown or JSON."""
    reports = db.query(EvidenceReport).order_by(EvidenceReport.compound_id).all()

    if format == "json":
        data = [
            {
                "compound_id": r.compound_id,
                "total_formulas": r.total_formulas,
                "val_diag": r.val_diag,
                "val_gen": r.val_gen,
                "feat_supp": r.feat_supp,
                "gen_hc": r.gen_hc,
                "struct_only": r.struct_only,
                "formula_evidence": r.formula_evidence,
                "pattern_evidence": r.pattern_evidence,
                "final_evidence": r.final_evidence,
            }
            for r in reports
        ]
        return StreamingResponse(
            io.BytesIO(json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=evidence_report.json"},
        )

    # Markdown
    md = io.StringIO()
    md.write("# TOF-SIMS Formula Network — Evidence Report\n\n")
    md.write("| Material | Total | ValDiag | ValGen | FeatSupp | GenHC | StructOnly | FormulaEv | PatternEv | Final Strategy |\n")
    md.write("|---|---:|---:|---:|---:|---:|---:|---|---|---|\n")
    for r in reports:
        md.write(f"| {r.compound_id} | {r.total_formulas} | {r.val_diag} | {r.val_gen} | {r.feat_supp} | {r.gen_hc} | {r.struct_only} | {r.formula_evidence} | {r.pattern_evidence} | {r.final_evidence} |\n")

    md.seek(0)
    return StreamingResponse(
        iter([md.getvalue()]),
        media_type="text/markdown",
        headers={"Content-Disposition": "attachment; filename=evidence_report.md"},
    )


@router.get("/network")
def export_network(
    material_id: str = Query(...),
    format: str = Query("json"),
    db: Session = Depends(get_db),
):
    """Export network as JSON."""
    nodes = (
        db.query(NetworkNode)
        .filter(NetworkNode.compound_id == material_id)
        .all()
    )
    edges = (
        db.query(NetworkEdge)
        .filter(NetworkEdge.compound_id == material_id)
        .all()
    )

    data = {
        "compound_id": material_id,
        "nodes": [
            {
                "node_id": n.node_id,
                "formula": n.formula,
                "ion_mode": n.ion_mode,
                "generation_type": n.generation_type,
                "operation": n.operation,
                "rule_pack": n.rule_pack,
                "path_score": n.path_score,
            }
            for n in nodes
        ],
        "edges": [
            {
                "edge_id": e.edge_id,
                "source_node": e.source_node,
                "target_node": e.target_node,
                "operation": e.operation,
                "operation_type": e.operation_type,
            }
            for e in edges
        ],
    }

    return StreamingResponse(
        io.BytesIO(json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={material_id}_network.json"},
    )
