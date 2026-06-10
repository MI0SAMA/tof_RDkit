# TOF-SIMS Formula Network

`ver1` is a first-stage engineering prototype for TOF-SIMS formula-network analysis.

The project parses real TOF-SIMS peak-list files, builds rule-based candidate formula networks from SMILES using RDKit, performs RF formula intersection and m/z-assisted matching, and writes CSV/Markdown outputs for inspection.

## Project Goal

The project is designed to support a larger workflow:

```text
TOF-SIMS spectrum m/z peaks
  -> random-forest candidate formulas
  -> structure-derived formula network
  -> calibrated and ranked candidate formulas
```

This repository does not attempt DFT, MD, AIMD, ion-impact simulation, or peak-intensity prediction. The current goal is a reproducible, inspectable prototype for formula plausibility filtering.

## Repository Layout

```text
config/
  default.yaml                         Default parsing, network, matching config
data/
  compounds.csv                        SMILES/formula table for known materials
  0510/                                Manually annotated validation spectra
  <material>/                          Raw TOF-SIMS txt/TXT files
  tof_db.sqlite                        Large database file tracked with Git LFS
docs/
  TOF-SIMS_formula_network_optimization_plan.md
outputs/
  parsed_spectra/                      Standardized peak-list CSVs
  networks/                            Generated formula networks
  matches/                             RF and m/z match outputs
  reports/                             Per-spectrum Markdown reports
  summary/                             Parse/build/match/verification summaries
tests/
  Unit tests for formula parsing, spectrum parsing, network, matching, reporting
tofsims_formula_network/
  Python package source
```

## Main Commands

The current tested environment is the local WSL RDKit conda environment:

```bash
/home/yao/PROGRAM/miniforge3/envs/rdkit/bin/python -m tofsims_formula_network.cli run-all --config config/default.yaml
```

Individual stages:

```bash
python -m tofsims_formula_network.cli parse-spectra --config config/default.yaml
python -m tofsims_formula_network.cli build-network --config config/default.yaml
python -m tofsims_formula_network.cli match-rf --config config/default.yaml
python -m tofsims_formula_network.cli match-spectrum --config config/default.yaml
python -m tofsims_formula_network.cli report --config config/default.yaml
```

Manual-annotation verification for the `data/0510/` subset:

```bash
python verify_0510.py
```

## Data And Git LFS

The repository includes raw spectra, generated outputs, and a large SQLite database.

`data/tof_db.sqlite` is larger than GitHub's normal single-file limit, so it is tracked with Git LFS. After cloning, install Git LFS and pull large files:

```bash
git lfs install
git lfs pull
```

## Current ver1 Outputs

The committed `outputs/` directory contains a complete run of the current prototype:

- parsed spectra summaries
- generated network CSV/JSON files
- mass-match outputs
- Markdown reports
- 0510 manual-annotation verification summary

These outputs are useful as a reproducible baseline, but they should not be treated as final chemically validated assignments.

## Known Limitations In ver1

- m/z matching is currently broad and can produce many false-positive candidates.
- RF matching is wired in, but `rf_formula_matches.csv` is empty unless a real RF candidate file is supplied.
- Positive/negative ion mode filtering needs to be tightened.
- Neutral and low-specificity formulas can appear in mass-only results.
- `fragmentation.py` and `ion_rules.py` are not yet split out; most rules currently live in `network.py`.
- Reports need stronger compound-level support and unmatched-peak summaries.

See [docs/TOF-SIMS_formula_network_optimization_plan.md](docs/TOF-SIMS_formula_network_optimization_plan.md) for the proposed optimization roadmap.

## Tests

The available standard-library test suite can be run with:

```bash
python -m unittest discover -s tests
```

The intended full test command is:

```bash
python -m pytest
```

If `pytest` is missing, install project dependencies from `requirements.txt` first.

