# TOF-SIMS Formula Network

`ver1` is a first-stage engineering prototype for TOF-SIMS formula-network analysis. `v2` is now being developed in parallel as a cleaner pure-material, lineage-aware network generator.

The project parses real TOF-SIMS peak-list files, builds rule-based candidate formula networks from SMILES using RDKit, performs AI-generated formula intersection and m/z-assisted matching, and writes CSV/Markdown outputs for inspection.

## Project Goal

The project is designed to support a larger workflow:

```text
TOF-SIMS spectrum m/z peaks
  -> AI-generated candidate formulas
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
  TOF-SIMS_formula_network_algorithm_rules.md
  TOF-SIMS_formula_network_algorithm_roadmap_2026-06-24.md
  TOF-SIMS_formula_network_algorithm_roadmap_canvas_2026-06-24.canvas
  TOF-SIMS_formula_network_lab_collaboration_canvas_2026-06-24.canvas
  TOF-SIMS_formula_network_lab_collaboration_mindmap_2026-06-23.md
  TOF-SIMS_formula_network_RF_output_network_comparison_2026-06-16.md
  TOF-SIMS_formula_network_v1_archive_2026-06-24.md
  TOF-SIMS_formula_network_v2_development_2026-06-24.md
  TOF-SIMS_formula_network_v2_1_update_2026-06-25.md
  TOF-SIMS_formula_network_v2_2_feature_rules_2026-06-25.md
  TOF-SIMS_formula_network_optimization_plan.md
scripts/
  compare_rf_network.py                Compare RF_output formulas with networks
outputs/
  parsed_spectra/                      Standardized peak-list CSVs
  networks/                            Generated formula networks
  networks_v2/                         v2 lineage-aware nodes/edges/formula summaries
  matches/                             AI-generated formula and m/z match outputs
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
python -m tofsims_formula_network.cli build-network-v2 --config config/default.yaml
python -m tofsims_formula_network.cli evaluate-network-v2 --config config/default.yaml
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

## Current Algorithm Rules

The current network generator has been split into explicit rule modules:

- `fragmentation.py` for structure-derived fragment formulas
- `ion_rules.py` for H-shift, adduct, neutral-loss and dimer rules
- `rule_packs.py` for low-score recall-oriented formula families
- `network.py` for orchestration, oligomer extension, scoring and deduplication

See [docs/TOF-SIMS_formula_network_algorithm_rules.md](docs/TOF-SIMS_formula_network_algorithm_rules.md) for the detailed rule definitions, scoring model, 0510 verification method and current material-level recall results.

The v1 state is archived in [docs/TOF-SIMS_formula_network_v1_archive_2026-06-24.md](docs/TOF-SIMS_formula_network_v1_archive_2026-06-24.md). The v2 implementation notes, scoring model, output files and current build summary are in [docs/TOF-SIMS_formula_network_v2_development_2026-06-24.md](docs/TOF-SIMS_formula_network_v2_development_2026-06-24.md). The v2.1 H-shift/recombination/evaluation update is recorded in [docs/TOF-SIMS_formula_network_v2_1_update_2026-06-25.md](docs/TOF-SIMS_formula_network_v2_1_update_2026-06-25.md). The v2.2 structure-feature-triggered rule update is recorded in [docs/TOF-SIMS_formula_network_v2_2_feature_rules_2026-06-25.md](docs/TOF-SIMS_formula_network_v2_2_feature_rules_2026-06-25.md).

For a lab-facing route map of the current formula generation pipeline, open [docs/TOF-SIMS_formula_network_algorithm_roadmap_canvas_2026-06-24.canvas](docs/TOF-SIMS_formula_network_algorithm_roadmap_canvas_2026-06-24.canvas). A Markdown version is available at [docs/TOF-SIMS_formula_network_algorithm_roadmap_2026-06-24.md](docs/TOF-SIMS_formula_network_algorithm_roadmap_2026-06-24.md).

For the before/after comparison of the baseline network and the current recall-rule-pack network, see [docs/TOF-SIMS_formula_network_comparison_2026-06-11.md](docs/TOF-SIMS_formula_network_comparison_2026-06-11.md).

For the comparison between `data/SMILES更新版.xlsx` and `data/compounds.csv`, plus the POMC/POMH full-spectrum overlay analysis, see [docs/TOF-SIMS_formula_network_SMILES_update_comparison_2026-06-11.md](docs/TOF-SIMS_formula_network_SMILES_update_comparison_2026-06-11.md).

For the comparison and screening between `RF_output/` blind-analysis formulas and the current formula networks, see [docs/TOF-SIMS_formula_network_RF_output_network_comparison_2026-06-16.md](docs/TOF-SIMS_formula_network_RF_output_network_comparison_2026-06-16.md). In current documentation, `RF_output` refers to the lab-provided AI-generated annotation output folder, not Random Forest. The reproducible script is [scripts/compare_rf_network.py](scripts/compare_rf_network.py).

For a lab-facing Canvas of where experimental expertise is needed in fragmentation rules, ion rules and scoring, open [docs/TOF-SIMS_formula_network_lab_collaboration_canvas_2026-06-24.canvas](docs/TOF-SIMS_formula_network_lab_collaboration_canvas_2026-06-24.canvas). A Markdown fallback is available at [docs/TOF-SIMS_formula_network_lab_collaboration_mindmap_2026-06-23.md](docs/TOF-SIMS_formula_network_lab_collaboration_mindmap_2026-06-23.md).

## Known Limitations In ver1

- m/z matching is currently broad and can produce many false-positive candidates.
- AI-generated formula matching is wired in, but `rf_formula_matches.csv` is empty unless a real candidate file is supplied.
- Positive/negative ion mode filtering needs to be tightened.
- Neutral and low-specificity formulas can appear in mass-only results.
- Recall rule packs improve formula coverage, but they are broad low-score heuristics and are not final chemical assignments.
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
