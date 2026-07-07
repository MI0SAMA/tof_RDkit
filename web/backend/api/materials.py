"""Materials API routes."""

import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import FormulaSummary, Material, Task

router = APIRouter(prefix="/api", tags=["materials"])


class GenerateRequest(BaseModel):
    compound_id: str
    smiles: str
    formula: str = ""
    version: str = "v3.0"
    config_overrides: dict | None = None


class GenerateResponse(BaseModel):
    task_id: str
    status: str
    message: str


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


@router.post("/materials/{material_id}/generate", response_model=GenerateResponse)
def generate_network(
    material_id: str,
    request: GenerateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Trigger network generation for a custom SMILES input."""
    # Validate SMILES is provided
    if not request.smiles.strip():
        raise HTTPException(status_code=400, detail="SMILES is required")

    compound_id = request.compound_id.strip() or material_id
    if not compound_id:
        raise HTTPException(status_code=400, detail="compound_id is required")

    # Check if there's already a running task for this material
    existing = (
        db.query(Task)
        .filter(
            Task.material_id == compound_id,
            Task.status.in_(["pending", "running"]),
        )
        .first()
    )
    if existing:
        return GenerateResponse(
            task_id=existing.task_id,
            status=existing.status,
            message=f"Task already {existing.status}",
        )

    # Create task record
    task_id = f"task_{uuid.uuid4().hex[:12]}"
    task = Task(
        task_id=task_id,
        task_type="generate_network",
        material_id=compound_id,
        version=request.version,
        status="pending",
        progress=0,
        current_step="Queued",
    )
    db.add(task)
    db.commit()

    # Enqueue background task
    from ..worker import run_generate_network

    background_tasks.add_task(
        run_generate_network,
        task_id=task_id,
        compound_id=compound_id,
        smiles=request.smiles.strip(),
        formula=request.formula.strip(),
        config_overrides=request.config_overrides,
    )

    return GenerateResponse(
        task_id=task_id,
        status="pending",
        message="Network generation queued",
    )
