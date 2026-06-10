# TOF-SIMS Formula Network

First-stage prototype for parsing TOF-SIMS peak lists, generating formula candidates from SMILES with RDKit, matching RF formula candidates, and writing CSV/Markdown outputs.

Run in the WSL RDKit environment:

```bash
/home/yao/PROGRAM/miniforge3/envs/rdkit/bin/python -m tofsims_formula_network.cli run-all --config config/default.yaml
```

If `data/compounds.csv` is missing, the CLI creates a small demo SMILES input so the network stage can run without modifying raw spectra.
