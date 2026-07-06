"""Network API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..services import get_material_network

router = APIRouter(prefix="/api", tags=["network"])


@router.get("/materials/{material_id}/network")
def get_network(
    material_id: str,
    hide_struct_only: bool = Query(True),
    db: Session = Depends(get_db),
):
    """Get network graph data for Cytoscape.js."""
    try:
        return get_material_network(material_id, db, hide_struct_only=hide_struct_only)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
