"""FastAPI application entry point for TOF-SIMS Formula Network Web."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .api import dashboard, evidence, export, formulas, import_data, match_peaks, materials, network, tasks
from .database import init_db

STATIC_DIR = Path(__file__).resolve().parent.parent / "frontend" / "dist"

app = FastAPI(
    title="TOF-SIMS Formula Network",
    version="0.3.0",
    description="Web interface for TOF-SIMS formula network analysis",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(dashboard.router)
app.include_router(materials.router)
app.include_router(formulas.router)
app.include_router(evidence.router)
app.include_router(network.router)
app.include_router(import_data.router)
app.include_router(match_peaks.router)
app.include_router(tasks.router)
app.include_router(export.router)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/api/health")
def health():
    return {"status": "ok"}


# Serve static frontend files (must be last)
if STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
