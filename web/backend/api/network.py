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


@router.get("/materials/{material_id}/network-sankey")
def get_network_sankey(material_id: str, db: Session = Depends(get_db)):
    """Get Sankey diagram data: generation_type → ion_mode → evidence_tag."""

    # Get all ionized formula summaries for this material
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

    # Layer 1: generation_type groups (from generation_types semicolon-separated list)
    # Layer 2: ion_mode
    # Layer 3: evidence_tag

    # Build Sankey nodes and links by counting unique formulas
    gen_types = {}      # "fragment" → count
    gen_to_ion = {}     # ("fragment", "positive") → count
    ion_to_tag = {}     # ("positive", "validated_diagnostic") → count
    tag_counts = {}     # "validated_diagnostic" → count

    for f in formulas:
        ion = f.ion_mode
        tag = f.diagnostic_tag or "unlabeled"

        # Parse generation types (e.g., "fragment;feature_rule" or "fragment_h_shift;recombination")
        types = [t.strip() for t in f.generation_types.split(";") if t.strip()]

        for gt in types:
            # Layer 1 count
            gen_types[gt] = gen_types.get(gt, 0) + 1

            # Layer 1 → Layer 2
            key_g2i = (gt, ion)
            gen_to_ion[key_g2i] = gen_to_ion.get(key_g2i, 0) + 1

        # Layer 2 → Layer 3
        key_i2t = (ion, tag)
        ion_to_tag[key_i2t] = ion_to_tag.get(key_i2t, 0) + 1

        # Layer 3 count
        tag_counts[tag] = tag_counts.get(tag, 0) + 1

    # Build ECharts Sankey format
    nodes = []
    links = []

    # Layer 1 nodes: generation types (short display names)
    GEN_LABELS = {
        "parent": "Parent",
        "fragment": "Fragment",
        "fragment_h_shift": "H-Shift",
        "feature_rule": "Feature Rule",
        "recombination": "Recombination",
    }

    for gt, count in sorted(gen_types.items()):
        nodes.append({"name": f"gen:{gt}", "itemStyle": {"color": "#60a5fa"}})

    # Layer 2 nodes: ion modes
    for ion in ["positive", "negative"]:
        if any(k[0] == ion for k in ion_to_tag):
            color = "#2563eb" if ion == "positive" else "#dc2626"
            nodes.append({"name": f"ion:{ion}", "itemStyle": {"color": color}})

    # Layer 3 nodes: evidence tags
    TAG_COLORS = {
        "validated_diagnostic": "#22c55e",
        "validated_generic": "#3b82f6",
        "feature_supported_candidate": "#f59e0b",
        "generic_hydrocarbon_background": "#ef4444",
        "structural_candidate_only": "#9ca3af",
        "unlabeled": "#d1d5db",
    }
    for tag, count in sorted(tag_counts.items(), key=lambda x: -x[1]):
        nodes.append({"name": f"tag:{tag}", "itemStyle": {"color": TAG_COLORS.get(tag, "#9ca3af")}})

    # Links Layer 1 → Layer 2
    for (gt, ion), count in gen_to_ion.items():
        links.append({"source": f"gen:{gt}", "target": f"ion:{ion}", "value": count})

    # Links Layer 2 → Layer 3
    for (ion, tag), count in ion_to_tag.items():
        links.append({"source": f"ion:{ion}", "target": f"tag:{tag}", "value": count})

    # Format node labels for display
    for n in nodes:
        name = n["name"]
        if name.startswith("gen:"):
            n["label"] = GEN_LABELS.get(name[4:], name[4:])
        elif name.startswith("ion:"):
            n["label"] = name[4:] == "positive" and "Positive (+)" or "Negative (−)"
        elif name.startswith("tag:"):
            n["label"] = name[4:].replace("_", " ").title()

    return {
        "compound_id": material_id,
        "total_formulas": len(formulas),
        "nodes": nodes,
        "links": links,
    }
