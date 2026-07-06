"""Materials API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Material

router = APIRouter(prefix="/api", tags=["materials"])


@router.get("/materials")
def list_materials(db: Session = Depends(get_db)):
    """List all materials."""
    materials = db.query(Material).order_by(Material.compound_id).all()
    return [
        {
            "compound_id": m.compound_id,
            "name": m.name,
            "smiles": m.smiles,
            "formula": m.formula,
            "group": m.group,
            "material_type": m.material_type,
            "notes": m.notes,
            "has_manual_labels": m.has_manual_labels,
        }
        for m in materials
    ]


@router.get("/materials/{material_id}")
def get_material(material_id: str, db: Session = Depends(get_db)):
    """Get material details."""
    material = db.query(Material).filter(Material.compound_id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    return {
        "compound_id": material.compound_id,
        "name": material.name,
        "smiles": material.smiles,
        "formula": material.formula,
        "group": material.group,
        "material_type": material.material_type,
        "notes": material.notes,
        "has_manual_labels": material.has_manual_labels,
    }
