# Generation Gap Analysis — Missing Peak Categorization

Each missing peak (not matched by any network formula) is classified by m/z range:

- **small_fragment** (25-100 Da): small fragments, functional groups, hydrocarbons
- **medium_fragment** (100-300 Da): structural fragments, multi-bond break products
- **large_fragment** (300-500 Da): large oligomer-like fragments
- **high_mass_unknown** (>500 Da): dimers, large oligomers
- **low_mass_background** (<25 Da): background, already excluded in evaluation

## Per-Material Gap Breakdown

| Material | Missing | small | medium | large | highMass | Top-5 missing m/z |
|---|---:|---:|---:|---:|---:|---|
| COC      |   7 | 100.0% |  0.0% |  0.0% |  0.0% | 25.01, 39.02, 91.05, 79.05, 77.04 |
| ETFE     |  12 | 100.0% |  0.0% |  0.0% |  0.0% | 77.02, 57.01, 39.02, 75.00, 39.01 |
| EVA      |   5 | 100.0% |  0.0% |  0.0% |  0.0% | 25.01, 91.05, 67.05, 39.02, 49.00 |
| FEP      |  13 | 76.9% | 23.1% |  0.0% |  0.0% | 93.00, 74.00, 116.99, 38.00, 284.80 |
| Nomex    |  10 | 100.0% |  0.0% |  0.0% |  0.0% | 41.04, 26.01, 39.02, 27.02, 43.05 |
| PEEK     |  11 | 100.0% |  0.0% |  0.0% |  0.0% | 41.04, 25.01, 39.02, 43.05, 55.05 |
| PEI      |  11 | 100.0% |  0.0% |  0.0% |  0.0% | 55.06, 29.04, 27.02, 39.02, 25.01 |
| PEN      |   9 | 100.0% |  0.0% |  0.0% |  0.0% | 41.04, 25.01, 39.02, 43.05, 49.01 |
| PFA      |  11 | 63.6% | 36.4% |  0.0% |  0.0% | 93.00, 184.99, 74.00, 38.00, 118.99 |
| PI       |  14 | 85.7% |  7.1% |  7.1% |  0.0% | 26.01, 25.01, 50.00, 291.81, 49.01 |
| POMC     |  15 | 100.0% |  0.0% |  0.0% |  0.0% | 45.00, 44.03, 89.02, 73.03, 25.01 |
| POMH     |  15 | 86.7% | 13.3% |  0.0% |  0.0% | 44.03, 45.00, 89.02, 73.03, 29.00 |
| PPS      |  14 | 78.6% | 14.3% |  7.1% |  0.0% | 25.01, 139.98, 56.98, 49.01, 80.98 |
| PTFE     |   3 | 100.0% |  0.0% |  0.0% |  0.0% | 93.00, 38.00, 43.00 |
| PVDF     |  16 | 87.5% | 12.5% |  0.0% |  0.0% | 113.00, 133.01, 69.00, 95.01, 39.01 |

## Priority Materials — Detailed Missing Peaks

### PEI

- Total missing: 11
- Small fragments (25-100 Da): 11 (100%)
- Medium fragments (100-300 Da): 0 (0%)
- Large fragments (300-500 Da): 0 (0%)

| # | m/z | Intensity | Category |
|---|---:|---:|---|
| 1 | 55.0554 | 1491.1 | small_fragment |
| 2 | 29.0388 | 1468.5 | small_fragment |
| 3 | 27.0224 | 1325.1 | small_fragment |
| 4 | 39.0223 | 1274.4 | small_fragment |
| 5 | 25.0084 | 583.7 | small_fragment |
| 6 | 26.0048 | 427.7 | small_fragment |
| 7 | 53.0380 | 359.3 | small_fragment |
| 8 | 45.0334 | 329.8 | small_fragment |
| 9 | 42.0003 | 285.5 | small_fragment |
| 10 | 49.0085 | 159.8 | small_fragment |
| 11 | 51.0217 | 19.0 | small_fragment |

### PEEK

- Total missing: 11
- Small fragments (25-100 Da): 11 (100%)
- Medium fragments (100-300 Da): 0 (0%)
- Large fragments (300-500 Da): 0 (0%)

| # | m/z | Intensity | Category |
|---|---:|---:|---|
| 1 | 41.0385 | 1018.2 | small_fragment |
| 2 | 25.0085 | 639.6 | small_fragment |
| 3 | 39.0223 | 591.3 | small_fragment |
| 4 | 43.0547 | 588.7 | small_fragment |
| 5 | 55.0543 | 584.0 | small_fragment |
| 6 | 27.0225 | 422.7 | small_fragment |
| 7 | 29.0384 | 364.1 | small_fragment |
| 8 | 49.0086 | 245.2 | small_fragment |
| 9 | 51.0221 | 225.9 | small_fragment |
| 10 | 73.0084 | 102.9 | small_fragment |
| 11 | 71.0146 | 27.9 | small_fragment |

### PI

- Total missing: 14
- Small fragments (25-100 Da): 12 (86%)
- Medium fragments (100-300 Da): 1 (7%)
- Large fragments (300-500 Da): 1 (7%)

| # | m/z | Intensity | Category |
|---|---:|---:|---|
| 1 | 26.0063 | 1977.8 | small_fragment |
| 2 | 25.0080 | 527.9 | small_fragment |
| 3 | 50.0039 | 432.5 | small_fragment |
| 4 | 291.8137 | 251.3 | medium_fragment |
| 5 | 49.0080 | 239.6 | small_fragment |
| 6 | 73.0073 | 160.4 | small_fragment |
| 7 | 74.0027 | 110.3 | small_fragment |
| 8 | 307.8076 | 109.7 | large_fragment |
| 9 | 41.0387 | 95.5 | small_fragment |
| 10 | 43.0550 | 69.7 | small_fragment |
| 11 | 29.0387 | 49.3 | small_fragment |
| 12 | 55.0545 | 39.3 | small_fragment |
| 13 | 39.0221 | 33.5 | small_fragment |
| 14 | 57.0708 | 8.9 | small_fragment |

### Nomex

- Total missing: 10
- Small fragments (25-100 Da): 10 (100%)
- Medium fragments (100-300 Da): 0 (0%)
- Large fragments (300-500 Da): 0 (0%)

| # | m/z | Intensity | Category |
|---|---:|---:|---|
| 1 | 41.0385 | 3485.3 | small_fragment |
| 2 | 26.0067 | 2026.8 | small_fragment |
| 3 | 39.0220 | 1663.0 | small_fragment |
| 4 | 27.0223 | 1475.4 | small_fragment |
| 5 | 43.0543 | 1341.2 | small_fragment |
| 6 | 55.0541 | 1211.2 | small_fragment |
| 7 | 29.0384 | 1167.3 | small_fragment |
| 8 | 25.0077 | 610.5 | small_fragment |
| 9 | 79.9531 | 433.4 | small_fragment |
| 10 | 49.9996 | 85.9 | small_fragment |

### PEN

- Total missing: 9
- Small fragments (25-100 Da): 9 (100%)
- Medium fragments (100-300 Da): 0 (0%)
- Large fragments (300-500 Da): 0 (0%)

| # | m/z | Intensity | Category |
|---|---:|---:|---|
| 1 | 41.0386 | 1331.4 | small_fragment |
| 2 | 25.0091 | 1313.3 | small_fragment |
| 3 | 39.0224 | 836.8 | small_fragment |
| 4 | 43.0548 | 729.7 | small_fragment |
| 5 | 49.0092 | 601.9 | small_fragment |
| 6 | 51.0223 | 383.0 | small_fragment |
| 7 | 97.0079 | 151.3 | small_fragment |
| 8 | 48.0005 | 121.0 | small_fragment |
| 9 | 36.0005 | 5.7 | small_fragment |

### PPS

- Total missing: 14
- Small fragments (25-100 Da): 11 (79%)
- Medium fragments (100-300 Da): 2 (14%)
- Large fragments (300-500 Da): 1 (7%)

| # | m/z | Intensity | Category |
|---|---:|---:|---|
| 1 | 25.0085 | 1032.9 | small_fragment |
| 2 | 139.9786 | 967.5 | medium_fragment |
| 3 | 56.9805 | 436.3 | small_fragment |
| 4 | 49.0083 | 435.9 | small_fragment |
| 5 | 80.9797 | 325.0 | small_fragment |
| 6 | 73.0075 | 204.7 | small_fragment |
| 7 | 104.9784 | 150.3 | medium_fragment |
| 8 | 41.0384 | 59.8 | small_fragment |
| 9 | 300.7684 | 56.8 | large_fragment |
| 10 | 39.0221 | 48.6 | small_fragment |
| 11 | 27.0224 | 40.4 | small_fragment |
| 12 | 68.9777 | 12.1 | small_fragment |
| 13 | 44.9786 | 12.0 | small_fragment |
| 14 | 29.0384 | 9.2 | small_fragment |

## Interpretation Guide

### If small_fragment dominates (>50%):
- Need more small diagnostic fragments (functional group rules)
- Example: carbonyl → CO+, C2H3O+; imide → CNO-, CHN+

### If medium_fragment dominates (>50%):
- Need structural break rules (specific bond cleavage patterns)
- RDKit fragmentation with max 2 bond breaks may not reach these masses
- Consider: oligomer extension, recombination, or 3-bond breaks for specific motifs

### If large_fragment dominates (>30%):
- Need oligomer extension or dimer rules
- These are likely repeat-unit multiples or parent-fragment clusters

### Specific material notes:
- PPS: S-containing fragments not well modeled by RDKit (C-S bond not breakable by default)
- PI/PEI: imide ring fragments need explicit N-containing break patterns
- Nomex: amide C-N cleavage not captured
- COC: norbornane ring opening not captured by RDKit (ring bond break = false)
- PEEK: ether-ketone specific breaks need aromatic ether cleavage rules