import unittest

from tofsims_formula_network.network_v2 import NetworkNode, generate_formula_network_v2, summarize_formula_nodes
from tofsims_formula_network.utils import default_config


class NetworkV2Tests(unittest.TestCase):
    def test_v2_builds_single_compound_lineage_without_external_adducts_or_dimers(self):
        cfg = default_config()
        row = {
            "compound_id": "STD_V2",
            "name": "Diethyl ether",
            "smiles": "CCOCC",
            "formula": "",
            "group": "small_organic",
            "notes": "",
        }
        nodes, edges, summaries = generate_formula_network_v2(row, cfg)
        formulas = {summary.formula for summary in summaries}
        generation_types = {node.generation_type for node in nodes}
        edge_types = {edge.operation_type for edge in edges}

        self.assertTrue(nodes)
        self.assertTrue(edges)
        self.assertTrue(summaries)
        self.assertIn("fragment", generation_types)
        self.assertIn("fragment_h_shift", generation_types)
        self.assertIn("recombination", generation_types)
        self.assertIn("fragmentation", edge_types)
        self.assertIn("h_shift", edge_types)
        self.assertIn("ionization", edge_types)
        self.assertIn("recombination", edge_types)
        self.assertFalse(any("Na" in formula or "K" in formula or "Cl" in formula for formula in formulas))
        self.assertFalse(any(node.generation_type == "dimer" for node in nodes))
        self.assertTrue(any(node.source_nodes for node in nodes if node.generation_type != "parent"))
        self.assertTrue(any(node.h_shift in {-1, 1} for node in nodes if node.generation_type == "fragment_h_shift"))
        self.assertTrue(any(node.operation in {"dehydrogenative_coupling", "single_dehydrogenative_recombination", "h_transfer_recombination"} for node in nodes))

    def test_formula_score_uses_multiple_path_support(self):
        cfg = default_config()
        common = {
            "compound_id": "STD_V2",
            "source_name": "Synthetic",
            "formula": "C2H5",
            "counts": {"C": 2, "H": 5},
            "exact_mass": 29.039125,
            "ion_mode": "positive",
            "charge": 1,
            "operation": "protonation",
            "h_shift": 1,
            "ionization_score": 0.72,
            "formula_score": 0.0,
        }
        nodes = [
            NetworkNode(
                node_id="node_0001",
                generation_type="fragment",
                path=["M", "break 1 bond(s)", "protonation"],
                source_nodes=["frag_a"],
                fragment_atom_indices=[0, 1],
                broken_bonds=1,
                structure_score=0.64,
                path_score=0.64,
                **common,
            ),
            NetworkNode(
                node_id="node_0002",
                generation_type="fragment",
                path=["M", "break 2 bond(s)", "protonation"],
                source_nodes=["frag_b"],
                fragment_atom_indices=[2, 3],
                broken_bonds=2,
                structure_score=0.56,
                path_score=0.56,
                **common,
            ),
        ]
        summaries = summarize_formula_nodes(nodes, cfg)

        self.assertEqual(len(summaries), 1)
        self.assertEqual(summaries[0].path_count, 2)
        self.assertEqual(summaries[0].source_fragment_count, 2)
        self.assertGreater(summaries[0].formula_score, summaries[0].best_path_score)
        self.assertEqual(nodes[0].formula_score, summaries[0].formula_score)


if __name__ == "__main__":
    unittest.main()
