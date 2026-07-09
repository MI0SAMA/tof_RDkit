"""Tasks API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Task

router = APIRouter(prefix="/api", tags=["tasks"])


@router.get("/tasks")
def list_tasks(
    status: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """List tasks with optional status filter."""
    query = db.query(Task).order_by(Task.created_at.desc())
    if status:
        query = query.filter(Task.status == status)
    tasks = query.limit(limit).all()
    return [
        {
            "task_id": t.task_id,
            "task_type": t.task_type,
            "material_id": t.material_id,
            "version": t.version,
            "status": t.status,
            "progress": t.progress,
            "current_step": t.current_step,
            "error_message": t.error_message,
            "created_at": t.created_at.isoformat() if t.created_at else None,
            "finished_at": t.finished_at.isoformat() if t.finished_at else None,
        }
        for t in tasks
    ]


@router.get("/tasks/{task_id}")
def get_task(task_id: str, db: Session = Depends(get_db)):
    """Get task status and details."""
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {
        "task_id": task.task_id,
        "task_type": task.task_type,
        "material_id": task.material_id,
        "version": task.version,
        "status": task.status,
        "progress": task.progress,
        "current_step": task.current_step,
        "log_path": task.log_path,
        "error_message": task.error_message,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "finished_at": task.finished_at.isoformat() if task.finished_at else None,
    }
