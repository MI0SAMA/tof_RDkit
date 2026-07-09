# v3.0 Material Evidence Integration Report

Combines formula-level diagnostics, pattern-level evidence,
and background filtering into a unified material identification framework.

## 1. Material Evidence Summary

| Material | ValDiag | ValGen | FeatSupp | GenHC | StructOnly | FormulaEv | PatternEv | BgLevel | **Final Evidence** |
|---|---:|---:|---:|---:|---:|---|---|---|---|
| COC | 7 | 10 | 2 | 15 | 112 | moderate | none (0.000) | medium | **mixed** |
| ETFE | 0 | 0 | 24 | 15 | 337 | feature_only | none (0.000) | low | **mixed** |
| EVA | 4 | 22 | 14 | 15 | 331 | weak | weak (0.130) | low | **mixed** |
| FEP | 0 | 0 | 16 | 15 | 25 | feature_only | none (0.000) | high | **mixed** |
| Nomex | 0 | 0 | 51 | 15 | 566 | feature_only | weak (0.024) | low | **mixed** |
| PDMS | 21 | 2 | 20 | 15 | 38 | strong | weak (0.156) | high | **formula-driven** |
| PEEK | 0 | 0 | 38 | 15 | 442 | feature_only | weak (0.101) | low | **mixed** |
| PEI | 0 | 0 | 38 | 15 | 992 | feature_only | weak (0.048) | low | **mixed** |
| PEN | 0 | 0 | 38 | 15 | 1061 | feature_only | weak (0.126) | low | **mixed** |
| PET | 60 | 22 | 21 | 15 | 994 | moderate | weak (0.126) | low | **mixed** |
| PFA | 0 | 0 | 16 | 15 | 25 | feature_only | none (0.000) | high | **mixed** |
| PI | 0 | 0 | 54 | 15 | 557 | feature_only | weak (0.024) | low | **mixed** |
| POMC | 0 | 21 | 5 | 4 | 8 | validated_generic_only | strong (1.000) | medium | **pattern-driven** |
| POMH | 0 | 21 | 4 | 4 | 9 | validated_generic_only | strong (1.000) | medium | **pattern-driven** |
| PPS | 0 | 0 | 24 | 15 | 26 | feature_only | none (0.000) | high | **mixed** |
| PTFE | 0 | 0 | 24 | 4 | 69 | feature_only | none (0.000) | low | **mixed** |
| PVDF | 0 | 0 | 24 | 4 | 70 | feature_only | none (0.000) | low | **mixed** |

### Evidence Strategy Legend

| Strategy | Meaning | Example Materials |
|---|---|---|
| **formula-driven** | Individual formulas carry strong diagnostic weight | PET, PDMS |
| **pattern-driven** | Material identified by fragment co-occurrence pattern | POMC, POMH |
| **formula + pattern-driven** | Both formula and pattern evidence converge | — |
| **mixed** | Moderate evidence from multiple sources | COC |
| **insufficient** | Neither formula nor pattern provide enough diagnostic power | FEP, PFA, PVDF... |
| **insufficient (background-dominated)** | Most matched formulas are generic HC background | EVA |

## 2. Validated Diagnostic Formulas

Formulas that: (a) match 0510 annotations, (b) appear in <=3 materials.

### COC (7 validated diagnostic)

| Formula | IonMode | fScore | dScore |
|---|---:|---:|
| C7H11 | positive | 0.990 | 0.80 |
| C7H9 | positive | 0.930 | 0.80 |
| C8H13 | positive | 0.834 | 0.80 |
| C3H3 | negative | 0.790 | 0.80 |
| C4H3 | negative | 0.790 | 0.80 |
| C5H5 | negative | 0.790 | 0.80 |
| C8H11 | positive | 0.642 | 0.80 |

### PDMS (21 validated diagnostic)

| Formula | IonMode | fScore | dScore |
|---|---:|---:|
| C2H5Si | negative | 0.894 | 0.80 |
| C2H7Si | positive | 0.894 | 0.80 |
| CH3OSi | negative | 0.894 | 0.80 |
| CH5OSi | positive | 0.894 | 0.80 |
| C2H7OSi | positive | 0.854 | 0.80 |
| C2H7OSi | negative | 0.854 | 0.80 |
| CH3OSi | positive | 0.842 | 0.80 |
| CH5OSi | negative | 0.842 | 0.80 |
| C2H5Si | positive | 0.822 | 0.80 |
| CH4OSi | positive | 0.776 | 0.80 |

### PET (60 validated diagnostic)

| Formula | IonMode | fScore | dScore |
|---|---:|---:|
| C10H10O4 | positive | 0.942 | 0.80 |
| C10H8O4 | negative | 0.942 | 0.80 |
| C9H8O3 | negative | 0.942 | 0.80 |
| C2H4O | negative | 0.912 | 0.80 |
| C10H9O4 | positive | 0.904 | 0.80 |
| C10H9O4 | negative | 0.904 | 0.80 |
| C10H7O3 | negative | 0.894 | 0.80 |
| C10H7O4 | negative | 0.894 | 0.80 |
| C2HO2 | negative | 0.894 | 0.80 |
| C3H3O2 | negative | 0.894 | 0.80 |

## 3. Pattern-Level Evidence

### POM (Polyoxymethylene) Pattern

| Material | POM Score | Diagnosis |
|---|---:|---|
| POMH | **1.000** | Strong POM evidence — pattern sufficient for identification |
| POMC | **1.000** | Strong POM evidence — pattern sufficient for identification |
| PDMS | **0.156** | Weak — incidental pattern match, likely false positive |
| EVA | **0.130** | Weak — incidental pattern match, likely false positive |
| PET | **0.126** | Weak — incidental pattern match, likely false positive |
| PEN | **0.126** | Weak — incidental pattern match, likely false positive |
| PEEK | **0.101** | Weak — incidental pattern match, likely false positive |
| PEI | **0.048** | Weak — incidental pattern match, likely false positive |
| Nomex | **0.024** | Weak — incidental pattern match, likely false positive |
| PI | **0.024** | Weak — incidental pattern match, likely false positive |

## 4. Generic Background Fragments

15 universal hydrocarbon fragments appearing in 13+ materials.
These explain spectra but provide no material-specific diagnostic value.

| Material | GenHC | Pct of Total |
|---|---:|---:|
| COC | 15 | 10.3% |
| ETFE | 15 | 4.0% |
| EVA | 15 | 3.9% |
| FEP | 15 | 26.8% |
| Nomex | 15 | 2.4% |
| PDMS | 15 | 15.6% |
| PEEK | 15 | 3.0% |
| PEI | 15 | 1.4% |
| PEN | 15 | 1.3% |
| PET | 15 | 1.3% |
| PFA | 15 | 26.8% |
| PI | 15 | 2.4% |
| PPS | 15 | 23.1% |
| POMC | 4 | 10.5% |
| POMH | 4 | 10.5% |
| PTFE | 4 | 4.1% |
| PVDF | 4 | 4.1% |

## 5. Hidden Structural Candidates

| Material | StructOnly | Pct Hidden |
|---|---:|---:|
| PEN | 1061 | 95.2% |
| PET | 994 | 89.4% |
| PEI | 992 | 94.9% |
| Nomex | 566 | 89.6% |
| PI | 557 | 89.0% |
| PEEK | 442 | 89.3% |
| ETFE | 337 | 89.6% |
| EVA | 331 | 85.8% |
| COC | 112 | 76.7% |
| PVDF | 70 | 71.4% |
| PTFE | 69 | 71.1% |
| PDMS | 38 | 39.6% |
| PPS | 26 | 40.0% |
| FEP | 25 | 44.6% |
| PFA | 25 | 44.6% |
| POMH | 9 | 23.7% |
| POMC | 8 | 21.1% |

*These are excluded from diagnostic reports by default (v2.9.2 filter).*