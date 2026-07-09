"""Import API routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..services import import_all

router = APIRouter(prefix="/api", tags=["import"])


@router.post("/import")
def import_data(db: Session = Depends(get_db)):
    """Import all existing v3.0 results into the database."""
    results = import_all(db)
    return {"status": "completed", "details": results}
