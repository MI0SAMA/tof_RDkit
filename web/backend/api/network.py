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


def _parse_path_signature(path_str: str) -> str:
    """Extract a human-readable path signature from a representative_path string.

    Examples:
      "M | fragment C,H,O from C-O bond break(s)" -> "C-O Bond Break"
      "M | carbonyl | carbonyl_fragmentation | carbonyl_CO" -> "Carbonyl → CO"
      "M | aromatic_ring | aromatic_stable_fragments | aromatic_C6H5" -> "Aromatic → C6H5"
      "M | fragment ... | h_shift_-1" -> "Bond Break + H-Shift"
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
            # Find the last part which is usually the formula fragment name
            last = parts[-1] if len(parts) > 1 else ""
            if "_" in last:
                formula_hint = last.split("_")[-1] if "_" in last else ""
                if formula_hint:
                    return f"{label} → {formula_hint}"
            return label

    # Bond break signatures
    if "bond break" in path_str.lower():
        has_h_shift = "h_shift" in path_str.lower()
        bond_info = ""
        for part in parts:
            if "from" in part.lower():
                bond_type = part.split("from")[-1].strip().rstrip(")")
                # Remove all text after the bond type names
                bond_type = bond_type.split(" bond break")[0].strip().rstrip("(").strip()
                # Clean up: "C-O+C-O" -> "C-O + C-O"
                bond_info = " + ".join(bond_type.split("+"))
        label = bond_info if bond_info else "RDKit Bond Break"
        if has_h_shift:
            label += " → H-Shift"
        return label

    # Recombination
    if "recombination" in path_str.lower() or ("node_" in parts[0] and "+" in parts[0]):
        return "Fragment Recombination"

    # Parent
    if path_str.strip() == "M":
        return "Parent Molecule"

    return "Other"


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

    # Layer structure: path_signature → ion_mode → evidence_tag
    path_counts = {}       # "Carbonyl → CO" → count
    path_to_ion = {}       # ("Carbonyl → CO", "positive") → count
    ion_to_tag = {}        # ("positive", "validated_diagnostic") → count
    tag_counts = {}        # "validated_diagnostic" → count

    for f in formulas:
        ion = f.ion_mode
        tag = f.diagnostic_tag or "unlabeled"

        path_sig = _parse_path_signature(f.representative_path)

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
