"""Network API routes — graph data + Sankey diagram."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import FormulaSummary, NetworkEdge, NetworkNode
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


def _parse_path_signature(path_str: str, all_node_ids: str = "", node_paths: dict[str, str] | None = None) -> str:
    """Extract a human-readable path signature from a representative_path string.

    For recombination formulas, looks up source fragment node paths to extract
    the original bond break information.
    """
    if not path_str:
        return "Unknown"

    parts = [p.strip() for p in path_str.split("|")]

    # Feature rule signatures
    triggers = {
        "carbonyl": "Carbonyl",
        "aromatic_ring": "Aromatic",
        "sulfur_aromatic": "S-Aromatic",
        "acetal_or_ether": "Acetal/Ether",
        "universal_hydrocarbon": "Small HC",
        "fluorocarbon_motif": "Fluorocarbon",
        "siloxane": "Siloxane",
        "imide": "Imide",
        "amide": "Amide",
        "cyclic_aliphatic": "Cyclic Aliphatic",
    }

    for trigger, label in triggers.items():
        if trigger in path_str:
            last = parts[-1] if len(parts) > 1 else ""
            if "_" in last:
                formula_hint = last.split("_")[-1] if "_" in last else ""
                if formula_hint:
                    return f"{label} → {formula_hint}"
            return label

    # Bond break signatures
    if "bond break" in path_str.lower():
        has_h_shift = "h_shift" in path_str.lower()
        bond_info = _extract_bond_info(parts)
        label = bond_info if bond_info else "RDKit Bond Break"
        if has_h_shift:
            label += " → H-Shift"
        return label

    # Recombination — look up source fragment nodes for bond break info
    if "recombination" in path_str.lower() or ("node_" in parts[0] and "+" in parts[0]):
        bond_info = _lookup_recomb_source(parts[0], all_node_ids, node_paths or {})
        if bond_info:
            return f"{bond_info} → Recombination"
        return "Fragment Recombination"

    # Parent
    if path_str.strip() == "M":
        return "Parent Molecule"

    return "Other"


def _extract_bond_info(parts: list[str]) -> str:
    """Extract bond type from path parts, e.g. 'C-O + C-C'"""
    for part in parts:
        if "from" in part.lower():
            bond_type = part.split("from")[-1].strip().rstrip(")")
            bond_type = bond_type.split(" bond break")[0].strip().rstrip("(").strip()
            return " + ".join(bond_type.split("+"))
    return ""


def _lookup_recomb_source(first_part: str, all_node_ids: str, node_paths: dict[str, str]) -> str:
    """Look up source fragment nodes for a recombination formula and extract bond info."""
    # first_part looks like "node_0002 + node_0061"
    # Try to extract node IDs
    node_ids = []
    if "+" in first_part:
        for token in first_part.split("+"):
            token = token.strip()
            if token.startswith("node_"):
                node_ids.append(token)

    # Also try all_node_ids (semicolon-separated)
    if not node_ids and all_node_ids:
        ids = [nid.strip() for nid in all_node_ids.split(";") if nid.strip().startswith("node_")]
        # Take the first 2 fragment-level nodes
        node_ids = ids[:2]

    # Look up each source node's path for bond break info
    all_bonds = []
    for nid in node_ids:
        node_path = node_paths.get(nid, "")
        if node_path and "bond break" in node_path.lower():
            parts = [p.strip() for p in node_path.split("|")]
            bi = _extract_bond_info(parts)
            if bi:
                # Split compound bonds like "C-O + C-C" into individual bonds
                for b in bi.split(" + "):
                    all_bonds.append(b.strip())

    if all_bonds:
        # Deduplicate and sort for consistent labels
        unique = sorted(set(all_bonds))
        return " + ".join(unique)
    return ""


@router.get("/materials/{material_id}/network-sankey")
def get_network_sankey(material_id: str, db: Session = Depends(get_db)):
    """Get Sankey diagram: parent → actual path → ion_mode → evidence_tag."""

    formulas = (
        db.query(FormulaSummary)
        .filter(
            FormulaSummary.compound_id == material_id,
            FormulaSummary.ion_mode != "neutral",
        )
        .all()
    )

    if not formulas:
        return {"nodes": [], "links": []}

    # Pre-load node paths for recombination lookup
    node_paths = {}
    nodes = db.query(NetworkNode).filter(NetworkNode.compound_id == material_id).all()
    for n in nodes:
        node_paths[n.node_id] = n.path or ""

    # Layer structure: path_signature → ion_mode → evidence_tag
    path_counts = {}       # "Carbonyl → CO" → count
    path_to_ion = {}       # ("Carbonyl → CO", "positive") → count
    ion_to_tag = {}        # ("positive", "validated_diagnostic") → count
    tag_counts = {}        # "validated_diagnostic" → count

    for f in formulas:
        ion = f.ion_mode
        tag = f.diagnostic_tag or "unlabeled"

        path_sig = _parse_path_signature(f.representative_path, f.all_node_ids, node_paths)

        path_counts[path_sig] = path_counts.get(path_sig, 0) + 1
        key_p2i = (path_sig, ion)
        path_to_ion[key_p2i] = path_to_ion.get(key_p2i, 0) + 1
        key_i2t = (ion, tag)
        ion_to_tag[key_i2t] = ion_to_tag.get(key_i2t, 0) + 1
        tag_counts[tag] = tag_counts.get(tag, 0) + 1

    # Build nodes and links
    nodes = []
    links = []

    # Color palette for path signatures
    PATH_COLORS = [
        "#60a5fa", "#34d399", "#fbbf24", "#f87171", "#a78bfa",
        "#fb923c", "#4ade80", "#f472b6", "#2dd4bf", "#eab308",
    ]
    color_idx = 0

    # Layer 1: Path signatures (sorted by count desc)
    for path_sig, _ in sorted(path_counts.items(), key=lambda x: -x[1]):
        color = PATH_COLORS[color_idx % len(PATH_COLORS)]
        color_idx += 1
        nodes.append({"name": f"path:{path_sig}", "label": path_sig, "itemStyle": {"color": color}})

    # Layer 2: Ion modes
    for ion in ["positive", "negative"]:
        if any(k[0] == ion for k in ion_to_tag):
            color = "#2563eb" if ion == "positive" else "#dc2626"
            nodes.append({"name": f"ion:{ion}", "label": "Positive (+)" if ion == "positive" else "Negative (−)", "itemStyle": {"color": color}})

    # Layer 3: Evidence tags
    TAG_COLORS = {
        "validated_diagnostic": "#22c55e",
        "validated_generic": "#3b82f6",
        "feature_supported_candidate": "#f59e0b",
        "generic_hydrocarbon_background": "#ef4444",
        "structural_candidate_only": "#d1d5db",
        "unlabeled": "#9ca3af",
    }
    for tag, _ in sorted(tag_counts.items(), key=lambda x: -x[1]):
        nodes.append({"name": f"tag:{tag}", "label": tag.replace("_", " ").title(), "itemStyle": {"color": TAG_COLORS.get(tag, "#9ca3af")}})

    # Links: Path → Ion
    for (path_sig, ion), count in path_to_ion.items():
        links.append({"source": f"path:{path_sig}", "target": f"ion:{ion}", "value": count})

    # Links: Ion → Tag
    for (ion, tag), count in ion_to_tag.items():
        links.append({"source": f"ion:{ion}", "target": f"tag:{tag}", "value": count})

    return {
        "compound_id": material_id,
        "total_formulas": len(formulas),
        "nodes": nodes,
        "links": links,
    }
