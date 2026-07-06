"""Formulas API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import FormulaSummary

router = APIRouter(prefix="/api", tags=["formulas"])


@router.get("/materials/{material_id}/formulas")
def list_formulas(
    material_id: str,
    evidence_tag: str | None = Query(None, description="Filter by diagnostic_tag"),
    ion_mode: str | None = Query(None, description="Filter by ion_mode"),
    min_score: float | None = Query(None, description="Minimum formula_score"),
    hide_struct_only: bool = Query(True, description="Hide structural_candidate_only"),
    hide_generic_hc: bool = Query(False, description="Hide generic_hydrocarbon_background"),
    search: str | None = Query(None, description="Search in formula text"),
    sort_by: str = Query("formula_score", description="Sort field"),
    sort_dir: str = Query("desc", description="Sort direction"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=500, description="Page size"),
    db: Session = Depends(get_db),
):
    """List formulas for a material with filtering and pagination."""
    query = db.query(FormulaSummary).filter(FormulaSummary.compound_id == material_id)

    if evidence_tag:
        query = query.filter(FormulaSummary.diagnostic_tag == evidence_tag)

    if ion_mode:
        query = query.filter(FormulaSummary.ion_mode == ion_mode)

    if min_score is not None:
        query = query.filter(FormulaSummary.formula_score >= min_score)

    if hide_struct_only:
        query = query.filter(FormulaSummary.is_hidden == False)  # noqa: E712

    if hide_generic_hc:
        query = query.filter(FormulaSummary.is_generic_hc == False)  # noqa: E712

    if search:
        query = query.filter(FormulaSummary.formula.ilike(f"%{search}%"))

    # Count total
    total = query.count()

    # Sort
    sort_column = getattr(FormulaSummary, sort_by, FormulaSummary.formula_score)
    if sort_dir == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    # Paginate
    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()

    # Evidence tag counts for this material
    tag_counts = {}
    all_tags = (
        db.query(FormulaSummary.diagnostic_tag, FormulaSummary.id)
        .filter(FormulaSummary.compound_id == material_id)
        .all()
    )
    for tag, _ in all_tags:
        tag = tag or "unknown"
        tag_counts[tag] = tag_counts.get(tag, 0) + 1

    return {
        "material_id": material_id,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, (total + page_size - 1) // page_size),
        "tag_counts": tag_counts,
        "items": [
            {
                "formula": f.formula,
                "ion_mode": f.ion_mode,
                "charge": f.charge,
                "exact_mass": f.exact_mass,
                "formula_score": f.formula_score,
                "best_path_score": f.best_path_score,
                "path_count": f.path_count,
                "mechanism_count": f.mechanism_count,
                "source_fragment_count": f.source_fragment_count,
                "generation_types": f.generation_types,
                "diagnostic_tag": f.diagnostic_tag,
                "material_diagnostic_score": f.material_diagnostic_score,
                "is_hidden": f.is_hidden,
                "is_generic_hc": f.is_generic_hc,
                "representative_path": f.representative_path,
            }
            for f in items
        ],
    }
