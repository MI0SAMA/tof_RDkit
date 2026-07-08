# Pattern-Level Diagnostic Report (v2.9.4)

## POM (Polyoxymethylene) Pattern

The POM backbone (-O-CH2-)n produces a characteristic series of
oxygenated fragments spaced by 30 Da (CH2O). Individual members
like C2H5O2+ are shared across O-containing materials, but the
CO-OCCURRENCE of 3+ series members is highly diagnostic for POM.

### Pattern Members

| Formula | IonMode | n_units | Label |
|---|---:|---:|
| CH3O | positive | 1 | POM_n1 |
| C2H5O | positive | 2 | POM_n2a |
| C2H5O2 | positive | 2 | POM_n2 |
| C3H7O2 | positive | 3 | POM_n3a |
| C3H7O3 | positive | 3 | POM_n3 |
| C4H9O3 | positive | 4 | POM_n4a |
| C4H9O4 | positive | 4 | POM_n4 |
| C5H11O4 | positive | 5 | POM_n5a |
| C5H11O5 | positive | 5 | POM_n5 |
| C2H3O2 | negative | 2 | POM_neg_n2 |
| C2H5O2 | negative | 2 | POM_neg_n2b |
| C3H5O3 | negative | 3 | POM_neg_n3 |
| C3H7O3 | negative | 3 | POM_neg_n3b |
| C4H7O4 | negative | 4 | POM_neg_n4 |

### Per-Material POM Pattern Scores

| Material | Score | Completeness | Members |
|---|---:|---:|---|
| POMH | **1.000** | 57.1% | POM_n1;POM_n2a;POM_n2;POM_n3a;POM_n3;POM_neg_n2;POM_neg_n2b;POM_neg_n3 |
| POMC | **1.000** | 57.1% | POM_n1;POM_n2a;POM_n2;POM_n3a;POM_n3;POM_neg_n2;POM_neg_n2b;POM_neg_n3 |
| PDMS | **0.156** | 35.7% | POM_n1;POM_n2a;POM_n2;POM_n3a;POM_neg_n2 |
| EVA | **0.130** | 35.7% | POM_n1;POM_n2a;POM_n2;POM_n3a;POM_neg_n2 |
| PEN | **0.126** | 100.0% | POM_n1;POM_n2a;POM_n2;POM_n3a;POM_n3;POM_n4a;POM_n4;POM_n5a;POM_n5;POM_neg_n2;POM_neg_n2b;POM_neg_n3;POM_neg_n3b;POM_neg_n4 |
| PET | **0.126** | 100.0% | POM_n1;POM_n2a;POM_n2;POM_n3a;POM_n3;POM_n4a;POM_n4;POM_n5a;POM_n5;POM_neg_n2;POM_neg_n2b;POM_neg_n3;POM_neg_n3b;POM_neg_n4 |
| PEEK | **0.101** | 35.7% | POM_n1;POM_n2a;POM_n2;POM_n3a;POM_neg_n2 |
| PEI | **0.048** | 35.7% | POM_n1;POM_n2a;POM_n2;POM_n3a;POM_neg_n2 |
| PI | **0.024** | 35.7% | POM_n1;POM_n2a;POM_n2;POM_n3a;POM_neg_n2 |
| Nomex | **0.024** | 35.7% | POM_n1;POM_n2a;POM_n2;POM_n3a;POM_neg_n2 |

### Diagnosis

Materials with POM pattern score >= 0.3 (strong POM evidence):
- **POMC**: score=1.000
- **POMH**: score=1.000