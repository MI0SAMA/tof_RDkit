import unittest

from tofsims_formula_network.formula import format_formula
from tofsims_formula_network.fragmentation import breakable_bond_indices, generate_fragments
from tofsims_formula_network.molecule_io import mol_from_smiles
from tofsims_formula_network.utils import default_config


class FragmentationTests(unittest.TestCase):
    def test_toluene_fragmentation_uses_heavy_single_non_ring_bonds(self):
        cfg = default_config()
        mol = mol_from_smiles("Cc1ccccc1")

        self.assertEqual(breakable_bond_indices(mol, cfg), [0])

        fragments = generate_fragments(mol, cfg)
        self.assertEqual(len(fragments), 1)
        self.assertEqual(format_formula(fragments[0].counts), "C6H5")
        self.assertEqual(fragments[0].broken_bonds, 1)


if __name__ == "__main__":
    unittest.main()
