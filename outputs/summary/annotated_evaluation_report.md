# TOF-SIMS Formula Network — 100-Aware Annotated Evaluation

## Four Core Metrics

| # | Metric | Definition | Question Answered |
|---|---|---|---|
| 1 | **Overall Recall** | annotated formulas found anywhere in network | Is the rule library complete? |
| 2 | **Recall@100** | annotated formulas in top-100 by score | Is scoring useful? |
| 3 | **Intensity-weighted Recall@100** | intensity of top-100 matches / total intensity | Are strong peaks prioritized? |
| 4 | **Enrichment@100** | Recall@100 / Overall Recall | Does scoring pull candidates forward? |

## Aggregate Summary (all materials)

| Metric | Value |
|---|---:|
| Total annotations (raw) | 1409 |
| Filtered annotations (evaluated) | 1199 |
| **Overall Recall** | **27.9%** |
| **Recall@100** | **18.9%** |
| **Intensity-weighted Recall@100** | **50.4%** |
| **Enrichment@100** | **0.680** |

## Per-Material Breakdown

| Material | Pol | Ann | Filt | NetSize | OverallRec | Rec@100 | IW-Rec@100 | Enrich@100 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| COC      | neg |  60 |  60 |   76 | **18.3% ** | **18.3% ** | **67.2% ** | **1.000** |
| COC      | pos |  69 |  69 |   79 | **32.4% ** | **32.4% ** | **62.5% ** | **1.000** |
| EVA      | neg |  48 |  48 |  194 | **31.2% ** | **31.2% ** | **53.7% ** | **1.000** |
| EVA      | pos |  69 |  69 |  192 | **42.0% ** | **29.0% ** | **53.0% ** | **0.690** |
| PDMS     | neg |  92 |  92 |   67 | **20.0% ** | **20.0% ** | **51.8% ** | **1.000** |
| PDMS     | pos |  96 |  96 |   77 | **19.8% ** | **19.8% ** | **56.8% ** | **1.000** |
| PET      | neg | 254 | 254 |  556 | **31.5% ** | **15.4% ** | **21.3% ** | **0.488** |
| PET      | pos | 298 | 298 |  556 | **34.2% ** | **14.9% ** | **29.9% ** | **0.436** |
| POMC     | neg |  54 |  54 |   15 | **11.3% ** | **11.3% ** | **42.3% ** | **1.000** |
| POMC     | pos |  54 |  54 |   23 | **28.3% ** | **28.3% ** | **60.7% ** | **1.000** |
| POMH     | neg |  52 |  52 |   15 | **13.5% ** | **13.5% ** | **55.9% ** | **1.000** |
| POMH     | pos |  53 |  53 |   23 | **27.5% ** | **27.5% ** | **65.0% ** | **1.000** |

## Per-Material Averages (both polarities)

| Material | OverallRec | Rec@100 | IW-Rec@100 | Enrich@100 |
|---|---:|---:|---:|---:|
| COC      | 25.3%  | 25.3%  | 64.9%  | 1.000 |
| EVA      | 36.6%  | 30.1%  | 53.4%  | 0.845 |
| PDMS     | 19.9%  | 19.9%  | 54.3%  | 1.000 |
| PET      | 32.9%  | 15.1%  | 25.6%  | 0.462 |
| POMC     | 19.8%  | 19.8%  | 51.5%  | 1.000 |
| POMH     | 20.5%  | 20.5%  | 60.4%  | 1.000 |

## Diagnostic Table

Shows whether the bottleneck is *generation* or *ranking*:

| OverallRec | Rec@100 | Enrich@100 | Diagnosis |
|---|---:|---:|---|
| High (>50%) | Low (<20%) | < 0.40 | Rules generate well, but scoring fails to rank |
| Low (<30%) | Moderate | > 0.80 | Rules incomplete, but what exists is well-ranked |
| High (>50%) | High (>40%) | > 0.70 | Both generation and ranking are good |
| Low (<30%) | Low (<20%) | < 0.60 | Both generation and ranking need work |

## Per-Material Detail

### COC (neg)

- Overall Recall: 18.3% (11/60 annotated formulas found in network)
- Recall@100: 18.3% (11/60 annotated formulas in top-100)
- IW-Recall@100: 67.2% (intensity 1518645.4 / 2258622.5)
- Enrichment@100: 1.000
- Network size: 76 formulas for this material+polarity
- Top-100 matched: C3, C3H, C3H3, C4, C4H, C4H3, C5, C5H, C5H5, C6, C6H
- Unmatched (49): C10, C10H, C10H2, C10H3, C10H5, C11, C11H, C11H2, C11H3, C11H5...

### COC (pos)

- Overall Recall: 32.4% (22/69 annotated formulas found in network)
- Recall@100: 32.4% (22/69 annotated formulas in top-100)
- IW-Recall@100: 62.5% (intensity 6316128.3 / 10102260.5)
- Enrichment@100: 1.000
- Network size: 79 formulas for this material+polarity
- Top-100 matched: C10H11, C10H9, C3H3, C3H5, C3H7, C4H3, C4H5, C4H7, C4H9, C5H5, C5H7, C5H9, C6H5, C6H7, C6H9...
- Unmatched (46): C10H7, C10H8, C10H8Cl, C11H10, C11H7, C11H9, C12H11, C12H8, C12H9, C13H9...

### EVA (neg)

- Overall Recall: 31.2% (15/48 annotated formulas found in network)
- Recall@100: 31.2% (15/48 annotated formulas in top-100)
- IW-Recall@100: 53.7% (intensity 5313722.0 / 9894181.4)
- Enrichment@100: 1.000
- Network size: 194 formulas for this material+polarity
- Top-100 matched: C2H2O2, C2H3O, C2H3O2, C2HO, C2O, C3, C3H, C4, C4H, C4H5O2, C5, C5H, C6, C6H, CHO2
- Unmatched (33): C10H, C12H, C15H23O6, C15H25O6, C2KO, C3H2, C3H3, C3H5O3, C3NO, C4H2...

### EVA (pos)

- Overall Recall: 42.0% (29/69 annotated formulas found in network)
- Recall@100: 29.0% (20/69 annotated formulas in top-100)
- IW-Recall@100: 53.0% (intensity 6650514.0 / 12546639.0)
- Enrichment@100: 0.690
- Network size: 192 formulas for this material+polarity
- Top-100 matched: C2H3O, C2HO, C3H3, C3H3O, C3H5, C3H6, C3H7, C4H3, C4H5, C4H7, C4H8, C4H9, C5H11, C5H5, C5H7...
- Unmatched (40): C10H10O3, C10H11, C10H11O3, C10H13, C11H11, C11H11O3, C11H13, C11H9O3, C12H10O3, C13H17...

### PDMS (neg)

- Overall Recall: 20.0% (17/92 annotated formulas found in network)
- Recall@100: 20.0% (17/92 annotated formulas in top-100)
- IW-Recall@100: 51.8% (intensity 2304021.1 / 4447595.3)
- Enrichment@100: 1.000
- Network size: 67 formulas for this material+polarity
- Top-100 matched: C2H3O, C2H5OSi, C2H5Si, C2H7O2Si, C2H7OSi, C2H8OSi, C2HO, C3, C3H, C3H7OSi, C3H7Si, C4, C4H, CH2O2Si, CH3O2Si...
- Unmatched (68): C2H2Si, C2H3OSi2, C2H3Si, C2H4Si, C2H5O4Si3, C2H5OSi2, C2HSi, C2Si, C3H10O2Si3, C3H2...

### PDMS (pos)

- Overall Recall: 19.8% (17/96 annotated formulas found in network)
- Recall@100: 19.8% (17/96 annotated formulas in top-100)
- IW-Recall@100: 56.8% (intensity 5161823.6 / 9088076.9)
- Enrichment@100: 1.000
- Network size: 77 formulas for this material+polarity
- Top-100 matched: C2H5Si, C2H6Si, C2H7OSi, C2H7OSi2, C2H7Si, C3H5, C3H7Si, C3H9O2Si2, C3H9OSi, C3H9Si, C4H11OSi2, C4H12Si2, C4H5, CH3OSi, CH4OSi...
- Unmatched (69): C2H11Si3, C2H12Si3, C2H3Si, C2H4Si, C2H5O3Si3, C2H6O3Si2, C2H6OSi2, C2H6Si3, C2H7Si3, C2H8Si3...

### PET (neg)

- Overall Recall: 31.5% (80/254 annotated formulas found in network)
- Recall@100: 15.4% (39/254 annotated formulas in top-100)
- IW-Recall@100: 21.3% (intensity 2858577.1 / 13422159.3)
- Enrichment@100: 0.488
- Network size: 556 formulas for this material+polarity
- Top-100 matched: C10H7O3, C10H7O4, C10H8O3, C10H8O4, C10H9O4, C12H12O4, C2H2O2, C2H3O, C2H3O2, C2H4O, C2HO, C2HO2, C2O, C3H3O2, C6H3...
- Unmatched (174): C10, C10H, C10H2, C10H2O3, C10H2O4, C10H3, C10H3O, C10H3O3, C10H4, C10H4O...

### PET (pos)

- Overall Recall: 34.2% (101/298 annotated formulas found in network)
- Recall@100: 14.9% (44/298 annotated formulas in top-100)
- IW-Recall@100: 29.9% (intensity 4535391.6 / 15151013.3)
- Enrichment@100: 0.436
- Network size: 556 formulas for this material+polarity
- Top-100 matched: C10H10O4, C10H7O4, C10H8O3, C10H8O4, C10H9O4, C2H3O, C2H3O2, C2H4O, C2H4O2, C2H5O, C2H6O, C3H3O, C3H3O2, C3H5O, C3H5O2...
- Unmatched (194): C10H10, C10H10O6, C10H11, C10H11O6, C10H2, C10H2O3, C10H2O4, C10H3, C10H3O3, C10H3O4...

### POMC (neg)

- Overall Recall: 11.3% (6/54 annotated formulas found in network)
- Recall@100: 11.3% (6/54 annotated formulas in top-100)
- IW-Recall@100: 42.3% (intensity 10271161.2 / 24302652.8)
- Enrichment@100: 1.000
- Network size: 15 formulas for this material+polarity
- Top-100 matched: C2H3O, C2H3O2, C2H5O, C2H5O2, C3H5O2, C3H5O3
- Unmatched (47): C11H9O8, C2H4O, C3H3, C3H3O, C3H5, C3H5O, C3H6, C3H6O, C3H6O2, C3H6O3...

### POMC (pos)

- Overall Recall: 28.3% (15/54 annotated formulas found in network)
- Recall@100: 28.3% (15/54 annotated formulas in top-100)
- IW-Recall@100: 60.7% (intensity 10081269.8 / 16613441.1)
- Enrichment@100: 1.000
- Network size: 23 formulas for this material+polarity
- Top-100 matched: C2H3O, C2H3O2, C2H4O, C2H5O, C2H5O2, C3H3O, C3H5O, C3H5O2, C3H5O3, C3H6O, C3H6O2, C3H6O3, C3H7O, C3H7O2, C3H7O3
- Unmatched (38): C11H9O8, C3H3, C3H5, C3H6, C3H7, C4H5, C4H7, C4H7O, C4H7O2, C4H7O3...

### POMH (neg)

- Overall Recall: 13.5% (7/52 annotated formulas found in network)
- Recall@100: 13.5% (7/52 annotated formulas in top-100)
- IW-Recall@100: 55.9% (intensity 9881808.8 / 17675845.3)
- Enrichment@100: 1.000
- Network size: 15 formulas for this material+polarity
- Top-100 matched: C2H3O, C2H3O2, C2H5O2, C2HO, C3H5O2, C3H5O3, CHO2
- Unmatched (45): C2H2O, C2H2O2, C2H3O3, C2H3O4, C2H4O3, C2H5O3, C2HO2, C2HO3, C2O, C3...

### POMH (pos)

- Overall Recall: 27.5% (14/53 annotated formulas found in network)
- Recall@100: 27.5% (14/53 annotated formulas in top-100)
- IW-Recall@100: 65.0% (intensity 15256959.6 / 23485842.4)
- Enrichment@100: 1.000
- Network size: 23 formulas for this material+polarity
- Top-100 matched: C2H3O, C2H4O, C2H5O, C2H5O2, C3H3O, C3H5O, C3H5O2, C3H5O3, C3H6O, C3H6O2, C3H6O3, C3H7O, C3H7O2, C3H7O3
- Unmatched (37): C11H9O8, C13H15O8, C2H2O, C2H5O3, C3H3, C3H5, C3H7, C4H7, C4H7O2, C4H7O3...
