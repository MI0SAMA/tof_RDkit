"""Dashboard API routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..services import get_dashboard_data

router = APIRouter(prefix="/api", tags=["dashboard"])


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    """Get dashboard summary data."""
    return get_dashboard_data(db)
