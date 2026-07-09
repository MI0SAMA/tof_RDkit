"""Evidence API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import EvidenceReport, FormulaSummary, Material

router = APIRouter(prefix="/api", tags=["evidence"])


@router.get("/materials/{material_id}/evidence")
def get_evidence(material_id: str, db: Session = Depends(get_db)):
    """Get evidence report for a material."""
    report = db.query(EvidenceReport).filter(EvidenceReport.compound_id == material_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Evidence report not found")

    material = db.query(Material).filter(Material.compound_id == material_id).first()

    # Get validated diagnostic formulas
    val_diag_formulas = (
        db.query(FormulaSummary)
        .filter(
            FormulaSummary.compound_id == material_id,
            FormulaSummary.diagnostic_tag == "validated_diagnostic",
        )
        .order_by(FormulaSummary.formula_score.desc())
        .limit(50)
        .all()
    )

    # Get validated generic formulas
    val_gen_formulas = (
        db.query(FormulaSummary)
        .filter(
            FormulaSummary.compound_id == material_id,
            FormulaSummary.diagnostic_tag == "validated_generic",
        )
        .order_by(FormulaSummary.formula_score.desc())
        .limit(50)
        .all()
    )

    # Get generic HC formulas
    gen_hc_formulas = (
        db.query(FormulaSummary)
        .filter(
            FormulaSummary.compound_id == material_id,
            FormulaSummary.diagnostic_tag == "generic_hydrocarbon_background",
        )
        .order_by(FormulaSummary.formula_score.desc())
        .all()
    )

    # Get feature supported formulas
    feat_supp_formulas = (
        db.query(FormulaSummary)
        .filter(
            FormulaSummary.compound_id == material_id,
            FormulaSummary.diagnostic_tag == "feature_supported_candidate",
        )
        .order_by(FormulaSummary.formula_score.desc())
        .limit(50)
        .all()
    )

    def fmt_formula(f):
        return {
            "formula": f.formula,
            "ion_mode": f.ion_mode,
            "charge": f.charge,
            "exact_mass": f.exact_mass,
            "formula_score": f.formula_score,
            "generation_types": f.generation_types,
            "diagnostic_tag": f.diagnostic_tag,
            "representative_path": f.representative_path,
        }

    return {
        "compound_id": material_id,
        "name": material.name if material else material_id,
        "summary": {
            "total_formulas": report.total_formulas,
            "val_diag": report.val_diag,
            "val_gen": report.val_gen,
            "feat_supp": report.feat_supp,
            "gen_hc": report.gen_hc,
            "struct_only": report.struct_only,
            "formula_evidence": report.formula_evidence,
            "pattern_evidence": report.pattern_evidence,
            "pom_pattern_score": report.pom_pattern_score,
            "background_level": report.background_level,
            "final_evidence": report.final_evidence,
        },
        "validated_diagnostic": [fmt_formula(f) for f in val_diag_formulas],
        "validated_generic": [fmt_formula(f) for f in val_gen_formulas],
        "feature_supported": [fmt_formula(f) for f in feat_supp_formulas],
        "generic_hydrocarbon": [fmt_formula(f) for f in gen_hc_formulas],
    }
