"""SQLAlchemy models for web.sqlite."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Material(Base):
    __tablename__ = "materials"

    compound_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    smiles: Mapped[str] = mapped_column(Text, nullable=True, default="")
    formula: Mapped[str] = mapped_column(String(100), nullable=True, default="")
    group: Mapped[str] = mapped_column(String(100), nullable=True, default="")
    material_type: Mapped[str] = mapped_column(String(100), nullable=True, default="")
    notes: Mapped[str] = mapped_column(Text, nullable=True, default="")
    has_manual_labels: Mapped[bool] = mapped_column(Boolean, default=False)


class FormulaSummary(Base):
    __tablename__ = "formula_summaries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    compound_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    source_name: Mapped[str] = mapped_column(String(200), nullable=True, default="")
    formula: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    ion_mode: Mapped[str] = mapped_column(String(20), nullable=False, default="neutral")
    charge: Mapped[int] = mapped_column(Integer, default=0)
    exact_mass: Mapped[float] = mapped_column(Float, default=0.0)
    formula_score: Mapped[float] = mapped_column(Float, default=0.0)
    best_path_score: Mapped[float] = mapped_column(Float, default=0.0)
    path_count: Mapped[int] = mapped_column(Integer, default=1)
    mechanism_count: Mapped[int] = mapped_column(Integer, default=1)
    source_fragment_count: Mapped[int] = mapped_column(Integer, default=0)
    generation_types: Mapped[str] = mapped_column(Text, nullable=True, default="")
    best_node_id: Mapped[str] = mapped_column(String(50), nullable=True, default="")
    representative_path: Mapped[str] = mapped_column(Text, nullable=True, default="")
    all_node_ids: Mapped[str] = mapped_column(Text, nullable=True, default="")
    diagnostic_tag: Mapped[str] = mapped_column(String(50), nullable=True, default="", index=True)
    material_diagnostic_score: Mapped[float] = mapped_column(Float, default=0.0)
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False)
    is_generic_hc: Mapped[bool] = mapped_column(Boolean, default=False)


class NetworkNode(Base):
    __tablename__ = "network_nodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    compound_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    node_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    formula: Mapped[str] = mapped_column(String(100), nullable=False)
    ion_mode: Mapped[str] = mapped_column(String(20), nullable=False, default="neutral")
    charge: Mapped[int] = mapped_column(Integer, default=0)
    exact_mass: Mapped[float] = mapped_column(Float, default=0.0)
    generation_type: Mapped[str] = mapped_column(String(50), nullable=True, default="")
    operation: Mapped[str] = mapped_column(String(100), nullable=True, default="")
    rule_pack: Mapped[str] = mapped_column(String(100), nullable=True, default="")
    trigger_feature: Mapped[str] = mapped_column(String(200), nullable=True, default="")
    evidence: Mapped[str] = mapped_column(Text, nullable=True, default="")
    path_score: Mapped[float] = mapped_column(Float, default=0.0)
    formula_score: Mapped[float] = mapped_column(Float, default=0.0)
    structure_score: Mapped[float] = mapped_column(Float, default=0.0)
    ionization_score: Mapped[float] = mapped_column(Float, default=0.0)
    broken_bonds: Mapped[int] = mapped_column(Integer, default=0)
    h_shift: Mapped[int] = mapped_column(Integer, default=0)
    path: Mapped[str] = mapped_column(Text, nullable=True, default="")
    source_nodes: Mapped[str] = mapped_column(Text, nullable=True, default="")


class NetworkEdge(Base):
    __tablename__ = "network_edges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    compound_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    edge_id: Mapped[str] = mapped_column(String(50), nullable=False)
    source_node: Mapped[str] = mapped_column(String(50), nullable=False)
    target_node: Mapped[str] = mapped_column(String(50), nullable=False)
    operation: Mapped[str] = mapped_column(String(100), nullable=True, default="")
    operation_type: Mapped[str] = mapped_column(String(50), nullable=True, default="")
    weight: Mapped[float] = mapped_column(Float, default=1.0)


class EvidenceReport(Base):
    __tablename__ = "evidence_reports"

    compound_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    total_formulas: Mapped[int] = mapped_column(Integer, default=0)
    val_diag: Mapped[int] = mapped_column(Integer, default=0)
    val_gen: Mapped[int] = mapped_column(Integer, default=0)
    feat_supp: Mapped[int] = mapped_column(Integer, default=0)
    gen_hc: Mapped[int] = mapped_column(Integer, default=0)
    struct_only: Mapped[int] = mapped_column(Integer, default=0)
    formula_evidence: Mapped[str] = mapped_column(String(50), nullable=True, default="")
    pattern_evidence: Mapped[str] = mapped_column(String(50), nullable=True, default="")
    pom_pattern_score: Mapped[float] = mapped_column(Float, default=0.0)
    background_level: Mapped[str] = mapped_column(String(20), nullable=True, default="")
    final_evidence: Mapped[str] = mapped_column(String(50), nullable=True, default="")


class ImportLog(Base):
    __tablename__ = "import_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    import_type: Mapped[str] = mapped_column(String(50), nullable=False)
    file_path: Mapped[str] = mapped_column(Text, nullable=True, default="")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    records_imported: Mapped[int] = mapped_column(Integer, default=0)
    message: Mapped[str] = mapped_column(Text, nullable=True, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Task(Base):
    __tablename__ = "tasks"

    task_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    task_type: Mapped[str] = mapped_column(String(50), nullable=False)
    material_id: Mapped[str] = mapped_column(String(50), nullable=True, default="")
    version: Mapped[str] = mapped_column(String(20), nullable=True, default="v3.0")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    progress: Mapped[int] = mapped_column(Integer, default=0)
    current_step: Mapped[str] = mapped_column(String(200), nullable=True, default="")
    log_path: Mapped[str] = mapped_column(Text, nullable=True, default="")
    error_message: Mapped[str] = mapped_column(Text, nullable=True, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, default=None)
