# 0510 Manual Annotation vs Algorithm Network — Verification Report

> Generated: 2026-06-10 11:30
> Filter: atomic/diatomic ions (≤2 heavy atoms) excluded (210 peaks removed)

---

## 1. Overall Summary

| Metric | Value |
|---|---:|
| Total manual annotations | 1409 |
| Excluded (atomic/diatomic ions ≤2 heavy atoms) | 210 |
| Annotations evaluated | 1199 |
| Matched by algorithm | **520** |
| Unmatched | 679 |
| **Overall hit rate** | **43.4%** |
| **Intensity coverage** | **65.5%** |

---

## 2. Per-Material Breakdown

| Material | Pol | Total | Excluded | Evaluated | Matched | Hit% | IntCov% | NetSize |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| COC | neg | 74 | 14 | 60 | **2** | **3.3%** | 0.2% | 442 |
| COC | pos | 81 | 12 | 69 | **9** | **13.0%** | 25.3% | 442 |
| EVA | neg | 60 | 12 | 48 | **13** | **27.1%** | 37.3% | 5820 |
| EVA | pos | 74 | 5 | 69 | **25** | **36.2%** | 47.4% | 5820 |
| PDMS | neg | 123 | 31 | 92 | **28** | **30.4%** | 62.1% | 3140 |
| PDMS | pos | 128 | 32 | 96 | **30** | **31.2%** | 25.6% | 3140 |
| PET | neg | 275 | 21 | 254 | **120** | **47.2%** | 59.6% | 7290 |
| PET | pos | 336 | 38 | 298 | **147** | **49.3%** | 58.9% | 7290 |
| POMC | neg | 65 | 11 | 54 | **35** | **64.8%** | 81.2% | 863 |
| POMC | pos | 65 | 11 | 54 | **35** | **64.8%** | 81.5% | 863 |
| POMH | neg | 65 | 13 | 52 | **38** | **73.1%** | 88.8% | 863 |
| POMH | pos | 63 | 10 | 53 | **38** | **71.7%** | 89.0% | 863 |

### Material Ratings

| Material | Rating | Hit% | Key Issue |
|---|---:|---:|---|
| COC | ⭐ Critical | 8.2% | SMILES (norbornene) does not represent true COC copolymer structure |
| EVA | ⭐⭐ Poor | 31.7% | Copolymer with variable VA content; single-repeat approximation limited |
| PDMS | ⭐⭐ Poor | 30.8% | Complex Si-containing fragments; need longer oligomer or Si-specific rules |
| PET | ⭐⭐⭐ Fair | 48.2% | Some fragments not captured; may need structural refinement |
| POMC | ⭐⭐⭐⭐⭐ Excellent | 64.8% | Remaining unmatched are mostly external adducts (Na+, K+, Cs+) |
| POMH | ⭐⭐⭐⭐⭐ Excellent | 72.4% | Remaining unmatched are mostly external adducts (Na+, K+, Cs+) |

---

## 3. Unmatched Peaks Analysis

Top 10 unmatched peaks per material (by intensity), after excluding atomic/diatomic ions:

### COC_neg (58 unmatched)

| # | Formula | Raw | m/z | Intensity | Heavy Atoms |
|---|---:|---:|---:|---:|
| 1 | C4H | C_4H- | 49.0086 | 527570.15 | 4 |
| 2 | C6H | C_6H- | 73.0084 | 218623.26 | 6 |
| 3 | C4 | C_4- | 48.0003 | 197248.35 | 4 |
| 4 | C3 | C_3- | 36.0004 | 188927.89 | 3 |
| 5 | C3H | C_3H- | 37.0082 | 111667.77 | 3 |
| 6 | C8H | C_8H- | 97.0085 | 91448.12 | 8 |
| 7 | C6 | C_6- | 72.0002 | 78881.65 | 6 |
| 8 | C3H2 | C_3H_2- | 38.0162 | 77555.84 | 3 |
| 9 | C5 | C_5- | 60.0005 | 71296.29 | 5 |
| 10 | C5H2 | C_5H_2- | 62.0162 | 59444.44 | 5 |

### COC_pos (60 unmatched)

| # | Formula | Raw | m/z | Intensity | Heavy Atoms |
|---|---:|---:|---:|---:|
| 1 | C5H7 | C_5H_7+ | 67.0569 | 1029446.55 | 5 |
| 2 | C3H5 | C_3H_5+ | 41.0400 | 1006435.87 | 3 |
| 3 | C3H3 | C_3H_3+ | 39.0231 | 535167.53 | 3 |
| 4 | C4H7 | C_4H_7+ | 55.0567 | 473036.22 | 4 |
| 5 | C4H5 | C_4H_5+ | 53.0392 | 365674.95 | 4 |
| 6 | C5H5 | C_5H_5+ | 65.0384 | 271793.82 | 5 |
| 7 | C9H7 | C_9H_7+ | 115.0494 | 244811.27 | 9 |
| 8 | C4H3 | C_4H_3+ | 51.0227 | 240804.92 | 4 |
| 9 | C10H8 | C_10H_8+ | 128.0550 | 180336.70 | 10 |
| 10 | C8H9 | C_8H_9+ | 105.0713 | 173541.38 | 8 |

### EVA_neg (35 unmatched)

| # | Formula | Raw | m/z | Intensity | Heavy Atoms |
|---|---:|---:|---:|---:|
| 1 | C4H | C_4H- | 49.0097 | 1271828.64 | 4 |
| 2 | C6H | C_6H- | 73.0081 | 565340.58 | 6 |
| 3 | C2KO | C_2OK- | 78.9564 | 535510.34 | 4 |
| 4 | C3H | C_3H- | 37.0090 | 358830.43 | 3 |
| 5 | C4H2 | C_4H_2- | 50.0105 | 246181.38 | 4 |
| 6 | C3 | C_3- | 36.0007 | 225914.31 | 3 |
| 7 | C8H | C_8H- | 97.0092 | 219375.45 | 8 |
| 8 | C5H2 | C_5H_2- | 62.0159 | 207390.12 | 5 |
| 9 | C4 | C_4- | 48.0004 | 205918.36 | 4 |
| 10 | C4H3 | C_4H_3- | 51.0247 | 188239.71 | 4 |

### EVA_pos (44 unmatched)

| # | Formula | Raw | m/z | Intensity | Heavy Atoms |
|---|---:|---:|---:|---:|
| 1 | C7H7 | C_7H_7+ | 91.0528 | 521260.00 | 7 |
| 2 | C5H9 | C_5H_9+ | 69.0727 | 520246.00 | 5 |
| 3 | C5H7 | C_5H_7+ | 67.0551 | 482917.00 | 5 |
| 4 | C6H9 | C_6H_9+ | 81.0721 | 395112.00 | 6 |
| 5 | C6H7 | C_6H_7+ | 79.0521 | 292590.00 | 6 |
| 6 | C6H5 | C_6H_5+ | 77.0354 | 282485.00 | 6 |
| 7 | C7H11 | C_7H_11+ | 95.0896 | 261251.00 | 7 |
| 8 | C9H7 | C_9H_7+ | 115.0472 | 258712.00 | 9 |
| 9 | C8H9 | C_8H_9+ | 105.0684 | 223361.00 | 8 |
| 10 | C6H11 | C_6H_11+ | 83.0908 | 221312.00 | 6 |

### PDMS_neg (64 unmatched)

| # | Formula | Raw | m/z | Intensity | Heavy Atoms |
|---|---:|---:|---:|---:|
| 1 | O2Si | SiO_2- | 59.9685 | 379935.42 | 3 |
| 2 | HO2Si | SiHO_2- | 60.9775 | 272335.33 | 3 |
| 3 | C3H9OSi | SiC_3H_9O- | 89.0520 | 168049.92 | 5 |
| 4 | C4HSi | SiC_4H- | 76.9877 | 89689.24 | 5 |
| 5 | C6H3O2Si | SiC_6H_3O_2- | 134.9967 | 74121.02 | 9 |
| 6 | CHO2Si2 | Si_2CHO_2- | 100.9548 | 63189.41 | 5 |
| 7 | C2HO | C_2HO- | 41.0052 | 44767.32 | 3 |
| 8 | C8H7OSi | SiC_8H_7O- | 147.0359 | 44694.72 | 10 |
| 9 | C3H3 | C_3H_3- | 39.0301 | 32231.09 | 3 |
| 10 | C4H11O4Si3 | Si_3C_4H_11O_4- | 207.0028 | 31308.03 | 11 |

### PDMS_pos (66 unmatched)

| # | Formula | Raw | m/z | Intensity | Heavy Atoms |
|---|---:|---:|---:|---:|
| 1 | C3H9Si | SiC_3H_9+ | 73.0590 | 3416958.36 | 4 |
| 2 | C5H15OSi2 | Si_2C_5H_15O+ | 147.0633 | 935941.47 | 8 |
| 3 | C3H10Si | SiC_3H_10+ | 74.0523 | 434463.48 | 4 |
| 4 | C3H9Si | ^30SiC_3H_9+ | 75.0453 | 258267.97 | 4 |
| 5 | C5H15OSi2 | Si^29SiC_5H_15O+ | 148.0642 | 198831.37 | 8 |
| 6 | C4H9O3Si | SiC_4H_9O_3+ | 133.0379 | 186135.91 | 8 |
| 7 | C7H21O2Si3 | Si_3C_7H_21O_2+ | 221.1089 | 141683.85 | 12 |
| 8 | C5H15OSi2 | Si^30SiC_5H_15O+ | 149.0566 | 106845.32 | 8 |
| 9 | C8H5O4Si | SiC_8H_5O_4+ | 192.9906 | 78318.79 | 13 |
| 10 | C6H17O6Si5 | Si_5C_6H_17O_6+ | 324.9255 | 70112.92 | 17 |

### PET_neg (134 unmatched)

| # | Formula | Raw | m/z | Intensity | Heavy Atoms |
|---|---:|---:|---:|---:|
| 1 | C4H | C_4H- | 49.0094 | 1384351.58 | 4 |
| 2 | C8H | C_8H- | 97.0080 | 382118.85 | 8 |
| 3 | C4 | C_4- | 48.0005 | 340211.47 | 4 |
| 4 | C4HO | C_4HO- | 65.0039 | 281714.23 | 5 |
| 5 | C3 | C_3- | 36.0007 | 228961.11 | 3 |
| 6 | C3H | C_3H- | 37.0086 | 189878.09 | 3 |
| 7 | C10H | C_10H- | 121.0050 | 146711.47 | 10 |
| 8 | C8 | C_8- | 95.9994 | 118505.34 | 8 |
| 9 | C4H2 | C_4H_2- | 50.0131 | 104558.49 | 4 |
| 10 | C3H2 | C_3H_2- | 38.0162 | 100439.08 | 3 |

### PET_pos (151 unmatched)

| # | Formula | Raw | m/z | Intensity | Heavy Atoms |
|---|---:|---:|---:|---:|
| 1 | C3H5 | C_3H_5+ | 41.0384 | 617423.46 | 3 |
| 2 | C4H3 | C_4H_3+ | 51.0218 | 509538.12 | 4 |
| 3 | C3H3 | C_3H_3+ | 39.0218 | 411672.00 | 3 |
| 4 | C5H5 | C_5H_5+ | 65.0379 | 376053.28 | 5 |
| 5 | C4H7 | C_4H_7+ | 55.0540 | 285139.42 | 4 |
| 6 | C4H5 | C_4H_5+ | 53.0374 | 253182.44 | 4 |
| 7 | C9H7 | C_9H_7+ | 115.0495 | 218183.94 | 9 |
| 8 | C4H2 | C_4H_2+ | 50.0133 | 194702.41 | 4 |
| 9 | C3H7 | C_3H_7+ | 43.0542 | 185804.64 | 3 |
| 10 | C4H4 | C_4H_4+ | 52.0285 | 129186.45 | 4 |

### POMC_neg (19 unmatched)

| # | Formula | Raw | m/z | Intensity | Heavy Atoms |
|---|---:|---:|---:|---:|
| 1 | C3H5 | C_3H_5+ | 41.0380 | 733211.35 | 3 |
| 2 | C4H7 | C_4H_7+ | 55.0526 | 724649.26 | 4 |
| 3 | C3H7 | C_3H_7+ | 43.0534 | 413726.72 | 3 |
| 4 | C3H3 | C_3H_3+ | 39.0213 | 340400.31 | 3 |
| 5 | C4H7O | C_4H_7O+ | 71.0453 | 295923.35 | 5 |
| 6 | C4H9 | C_4H_9+ | 57.0676 | 241179.82 | 4 |
| 7 | C3H3O | C_3H_3O+ | 55.0154 | 204047.20 | 4 |
| 8 | C4H9O | C_4H_9O+ | 73.0590 | 181469.52 | 5 |
| 9 | C4H5 | C_4H_5+ | 53.0354 | 176173.96 | 4 |
| 10 | C5H7 | C_5H_7+ | 67.0505 | 152258.01 | 5 |

### POMC_pos (19 unmatched)

| # | Formula | Raw | m/z | Intensity | Heavy Atoms |
|---|---:|---:|---:|---:|
| 1 | C4H7 | C_4H_7+ | 55.0511 | 479920.68 | 4 |
| 2 | C3H5 | C_3H_5+ | 41.0372 | 474074.59 | 3 |
| 3 | C3H7 | C_3H_7+ | 43.0526 | 282499.48 | 3 |
| 4 | C3H3 | C_3H_3+ | 39.0207 | 223259.66 | 3 |
| 5 | C4H7O | C_4H_7O+ | 71.0433 | 203677.17 | 5 |
| 6 | C4H9 | C_4H_9+ | 57.0663 | 168405.32 | 4 |
| 7 | C3H3O | C_3H_3O+ | 55.0142 | 131441.83 | 4 |
| 8 | C4H9O | C_4H_9O+ | 73.0552 | 130492.24 | 5 |
| 9 | C4H5 | C_4H_5+ | 53.0342 | 110417.62 | 4 |
| 10 | HNa2O | Na_2OH+ | 62.9766 | 102148.88 | 3 |

### POMH_neg (14 unmatched)

| # | Formula | Raw | m/z | Intensity | Heavy Atoms |
|---|---:|---:|---:|---:|
| 1 | C2H3O4 | C_2H_3O_4- | 91.0040 | 458577.47 | 6 |
| 2 | C2HO3 | C_2HO_3- | 72.9937 | 359988.00 | 5 |
| 3 | C3HO2 | C_3HO_2- | 68.9978 | 201255.38 | 5 |
| 4 | C2O | C_2O- | 39.9951 | 163545.98 | 3 |
| 5 | C4H | C_4H- | 49.0072 | 157196.81 | 4 |
| 6 | CHO3 | CHO_3- | 60.9929 | 123618.18 | 4 |
| 7 | C3HO | C_3HO- | 53.0024 | 108810.61 | 4 |
| 8 | C3H | C_3H- | 37.0081 | 80533.78 | 3 |
| 9 | C4HO | C_4HO- | 65.0024 | 70642.37 | 5 |
| 10 | C3 | C_3- | 36.0002 | 63423.65 | 3 |

### POMH_pos (15 unmatched)

| # | Formula | Raw | m/z | Intensity | Heavy Atoms |
|---|---:|---:|---:|---:|
| 1 | C3H5 | C_3H_5+ | 41.0373 | 375292.73 | 3 |
| 2 | C4H7 | C_4H_7+ | 55.0518 | 258098.25 | 4 |
| 3 | C3H7 | C_3H_7+ | 43.0532 | 257623.01 | 3 |
| 4 | C6H9O8 | C_6H_9O_8+ | 209.0409 | 246106.92 | 14 |
| 5 | C3H3 | C_3H_3+ | 39.0209 | 193894.53 | 3 |
| 6 | C7H11O9 | C_7H_11O_9+ | 239.0468 | 177686.61 | 16 |
| 7 | C7H13O9 | C_7H_13O_9+ | 241.0636 | 152662.16 | 16 |
| 8 | C9H9O4 | C_9H_9O_4+ | 181.0496 | 145779.86 | 13 |
| 9 | C3H3O | C_3H_3O+ | 55.0143 | 144034.79 | 4 |
| 10 | C11H9O8 | C_11H_9O_8+ | 269.0532 | 142343.33 | 19 |

---

## 4. Matched Examples (Top 5 by network score per material)

### COC_neg

| Formula | Raw | m/z | Intensity | NetScore | GenType | Path |
|---|---:|---:|---:|---:|---|
| C7H7 | C_7H_7- | 91.0565 | 2029.25 | 0.650 | adduct | M | H shift -2 | -H |
| C6H5 | C_6H_5- | 77.0405 | 3277.43 | 0.550 | neutral_loss | M | H shift -2 | -CH3 |

### COC_pos

| Formula | Raw | m/z | Intensity | NetScore | GenType | Path |
|---|---:|---:|---:|---:|---|
| C7H9 | C_7H_9+ | 93.0735 | 190308.76 | 0.750 | adduct | M | -H |
| C7H11 | C_7H_11+ | 95.0926 | 140101.76 | 0.750 | adduct | M | H |
| C7H8 | C_7H_8+ | 92.0595 | 89918.93 | 0.700 | adduct | M | H shift -1 | -H |
| C6H7 | C_6H_7+ | 79.0555 | 537055.55 | 0.650 | neutral_loss | M | -CH3 |
| C7H7 | C_7H_7+ | 91.0536 | 593814.10 | 0.650 | adduct | M | H shift -2 | -H |

### EVA_neg

| Formula | Raw | m/z | Intensity | NetScore | GenType | Path |
|---|---:|---:|---:|---:|---|
| C2H3O | C_2H_3O- | 43.0201 | 63833.37 | 0.600 | fragment | break 1 bond(s) | ; | break 2 bond(s) | ; | break 2 bond(s) | ; | break 2 bond(s |
| C2H2O2 | C_2H_2O_2- | 58.0052 | 130054.55 | 0.600 | adduct | break 1 bond(s) | -H | ; | break 1 bond(s) | H shift -2 | OH | ; | break 1 bond( |
| C2H3O2 | C_2H_3O_2- | 59.0168 | 1180077.62 | 0.600 | fragment | break 1 bond(s) | ; | break 2 bond(s) | ; | break 2 bond(s) | ; | break 2 bond(s |
| C2HO | C_2HO- | 41.0059 | 515804.11 | 0.550 | adduct | break 1 bond(s) | H shift -1 | -H | ; | break 2 bond(s) | H shift -1 | -H | ; |  |
| C4H5O2 | C_4H_5O_2- | 85.0210 | 161612.85 | 0.550 | adduct | break 1 bond(s) | H shift -1 | -H | ; | break 2 bond(s) | H shift -1 | -H | ; |  |

### EVA_pos

| Formula | Raw | m/z | Intensity | NetScore | GenType | Path |
|---|---:|---:|---:|---:|---|
| C2H3O | C_2H_3O+ | 43.0179 | 383772.00 | 0.600 | fragment | break 1 bond(s) | ; | break 2 bond(s) | ; | break 2 bond(s) | ; | break 2 bond(s |
| C4H8 | C_4H_8+ | 56.0599 | 138652.00 | 0.600 | adduct | break 1 bond(s) | -H | ; | break 2 bond(s) | -H | ; | break 2 bond(s) | -H |
| C4H9 | C_4H_9+ | 57.0726 | 464255.00 | 0.600 | fragment | break 1 bond(s) | ; | break 2 bond(s) | ; | break 2 bond(s) |
| C5H11 | C_5H_11+ | 71.0903 | 172256.00 | 0.600 | neutral_loss | M | H shift -1 | -CO2 |
| C5H10 | C_5H_10+ | 70.0767 | 64908.00 | 0.550 | neutral_loss | M | H shift -2 | -CO2 |

### PDMS_neg

| Formula | Raw | m/z | Intensity | NetScore | GenType | Path |
|---|---:|---:|---:|---:|---|
| C2H7OSi | SiC_2H_7O- | 75.0303 | 190562.54 | 0.600 | fragment | break 1 bond(s) | ; | break 1 bond(s) | ; | break 2 bond(s) | ; | break 2 bond(s |
| C2H8OSi | SiC_2H_8O- | 76.0323 | 15780.12 | 0.600 | adduct | break 1 bond(s) | H | ; | break 1 bond(s) | H | ; | break 2 bond(s) | H | ; | br |
| C4H13O3Si2 | Si_2C_4H_13O_3- | 165.0523 | 28631.63 | 0.580 | adduct | M | H shift -1 | O | ; | break 1 bond(s) + 1×repeat | H shift -1 | OH | ; | brea |
| C6H17O3Si3 | Si_3C_6H_17O_3- | 221.0553 | 33371.88 | 0.570 | adduct | M + 1×repeat | H shift -2 | -H | ; | break 1 bond(s) + 1×repeat | H shift -2 | O |
| C2H5OSi | SiC_2H_5O- | 73.0157 | 322307.46 | 0.550 | adduct | break 1 bond(s) | H shift -1 | -H | ; | break 1 bond(s) | H shift -1 | -H | ; |  |

### PDMS_pos

| Formula | Raw | m/z | Intensity | NetScore | GenType | Path |
|---|---:|---:|---:|---:|---|
| C2H7OSi | SiC_2H_7O+ | 75.0216 | 244168.80 | 0.600 | fragment | break 1 bond(s) | ; | break 1 bond(s) | ; | break 2 bond(s) | ; | break 2 bond(s |
| C2H7OSi | ^29SiC_2H_7O+ | 76.0220 | 21628.50 | 0.600 | fragment | break 1 bond(s) | ; | break 1 bond(s) | ; | break 2 bond(s) | ; | break 2 bond(s |
| C2H7OSi | ^30SiC_2H_7O+ | 77.0191 | 11665.13 | 0.600 | fragment | break 1 bond(s) | ; | break 1 bond(s) | ; | break 2 bond(s) | ; | break 2 bond(s |
| C4H11OSi2 | Si_2C_4H_11O+ | 131.0206 | 110184.00 | 0.600 | neutral_loss | M | H shift -1 | -H2O | ; | break 1 bond(s) | -H2 | ; | break 1 bond(s) | -H2 |
| C3H9O2Si2 | Si_2C_3H_9O_2+ | 132.9970 | 151622.87 | 0.550 | neutral_loss | M | H shift -2 | -CH3 | ; | break 1 bond(s) | -H2 | ; | break 1 bond(s) | -H2 |

### PET_neg

| Formula | Raw | m/z | Intensity | NetScore | GenType | Path |
|---|---:|---:|---:|---:|---|
| C2H4O | C_2H_4O- | 44.0230 | 9000.02 | 0.600 | adduct | break 1 bond(s) | -H | ; | break 1 bond(s) | -H | ; | break 2 bond(s) | -H | ; | |
| C9H8O3 | C_9H_8O_3- | 164.0476 | 8573.90 | 0.600 | adduct | break 1 bond(s) | -H | ; | break 1 bond(s) | -H | ; | break 2 bond(s) | -H | ; | |
| C9H9O3 | C_9H_9O_3- | 165.0602 | 26700.71 | 0.600 | fragment | break 1 bond(s) | ; | break 1 bond(s) | ; | break 2 bond(s) | ; | break 2 bond(s |
| C10H8O4 | C_10H_8O_4- | 192.0514 | 5783.11 | 0.600 | adduct | break 1 bond(s) | -H | ; | break 1 bond(s) | -H | ; | break 2 bond(s) | -H | ; | |
| C10H9O4 | C_10H_9O_4- | 193.0554 | 9627.22 | 0.600 | fragment | break 1 bond(s) | ; | break 1 bond(s) | ; | break 2 bond(s) | ; | break 2 bond(s |

### PET_pos

| Formula | Raw | m/z | Intensity | NetScore | GenType | Path |
|---|---:|---:|---:|---:|---|
| C12H12O6 | C_12H_12O_6+ | 252.0621 | 20914.70 | 0.700 | adduct | M | H shift -1 | -H | ; | break 1 bond(s) | H shift -2 | OH | ; | break 1 bond(s |
| C11H11O6 | C_11H_11O_6+ | 239.0606 | 37759.06 | 0.650 | neutral_loss | M | -CH3 | ; | break 1 bond(s) + 1×repeat | H shift +1 | -CH3 | ; | break 1 bond |
| C2H4O | C_2H_4O+ | 44.0230 | 14438.87 | 0.600 | adduct | break 1 bond(s) | -H | ; | break 1 bond(s) | -H | ; | break 2 bond(s) | -H | ; | |
| C2H5O | C_2H_5O+ | 45.0330 | 145048.76 | 0.600 | fragment | break 1 bond(s) | ; | break 1 bond(s) | ; | break 2 bond(s) | ; | break 2 bond(s |
| C2H6O | C_2H_6O+ | 46.0358 | 3756.99 | 0.600 | adduct | break 1 bond(s) | H | ; | break 1 bond(s) | H | ; | break 2 bond(s) | H | ; | br |

### POMC_neg

| Formula | Raw | m/z | Intensity | NetScore | GenType | Path |
|---|---:|---:|---:|---:|---|
| C2H5O | C_2H_5O+ | 45.0353 | 3528735.71 | 0.750 | adduct | M | -H |
| C2H5O | C^13CH_5O+ | 46.0342 | 100692.56 | 0.750 | adduct | M | -H |
| C2H4O | C_2H_4O+ | 44.0263 | 2145159.27 | 0.700 | adduct | M | H shift -1 | -H |
| C3H7O2 | C_3H_7O_2+ | 75.0401 | 895490.07 | 0.670 | adduct | M + 1×repeat | -H |
| C2H3O | C_2H_3O+ | 43.0168 | 515815.66 | 0.650 | adduct | M | H shift -2 | -H |

### POMC_pos

| Formula | Raw | m/z | Intensity | NetScore | GenType | Path |
|---|---:|---:|---:|---:|---|
| C2H5O | C_2H_5O+ | 45.0343 | 2369190.43 | 0.750 | adduct | M | -H |
| C2H5O | C^13CH_5O+ | 46.0334 | 67170.33 | 0.750 | adduct | M | -H |
| C2H4O | C_2H_4O+ | 44.0252 | 1411135.43 | 0.700 | adduct | M | H shift -1 | -H |
| C3H7O2 | C_3H_7O_2+ | 75.0348 | 616682.68 | 0.670 | adduct | M + 1×repeat | -H |
| C2H3O | C_2H_3O+ | 43.0160 | 329492.84 | 0.650 | adduct | M | H shift -2 | -H |

### POMH_neg

| Formula | Raw | m/z | Intensity | NetScore | GenType | Path |
|---|---:|---:|---:|---:|---|
| C3H7O2 | C_3H_7O_2- | 75.0435 | 57820.54 | 0.670 | adduct | M + 1×repeat | -H |
| C2H3O | C_2H_3O- | 43.0196 | 651632.99 | 0.650 | adduct | M | H shift -2 | -H |
| C4H9O3 | C_4H_9O_3- | 105.0535 | 41664.19 | 0.590 | adduct | M + 2×repeat | -H |
| C2H5O2 | C_2H_5O_2- | 61.0296 | 751641.94 | 0.580 | adduct | M | H shift -1 | O | ; | break 1 bond(s) + 1×repeat | H shift +1 | -H | ; | brea |
| C3H5O2 | C_3H_5O_2- | 73.0292 | 102024.82 | 0.570 | adduct | M + 1×repeat | H shift -2 | -H |

### POMH_pos

| Formula | Raw | m/z | Intensity | NetScore | GenType | Path |
|---|---:|---:|---:|---:|---|
| C2H5O | C_2H_5O+ | 45.0342 | 2903316.11 | 0.750 | adduct | M | -H |
| C2H5O | C^13CH_5O+ | 46.0335 | 104816.38 | 0.750 | adduct | M | -H |
| C2H4O | C_2H_4O+ | 44.0266 | 2592918.67 | 0.700 | adduct | M | H shift -1 | -H |
| C3H7O2 | C_3H_7O_2+ | 75.0398 | 961400.25 | 0.670 | adduct | M + 1×repeat | -H |
| C2H3O | C_2H_3O+ | 43.0165 | 600248.17 | 0.650 | adduct | M | H shift -2 | -H |

---

## 5. Filter Statistics

Total annotations removed by atomic/diatomic filter: **210**

Breakdown of excluded ion types:

| Formula | Count | Category |
|---|---:|
| C2H3 | 10 | diatomic |
| C2H | 10 | diatomic |
| CH3 | 9 | atomic |
| H | 8 | atomic |
| C | 8 | atomic |
| CH | 8 | atomic |
| CH2 | 8 | atomic |
| CH3O | 8 | diatomic |
| C2H5 | 7 | diatomic |
| Cl | 7 | atomic |
| Na | 6 | atomic |
| K | 6 | atomic |
| Cs | 6 | atomic |
| O | 6 | atomic |
| HO | 6 | atomic |
| HOSi | 6 | diatomic |
| CHO | 6 | diatomic |
| C2H4 | 5 | diatomic |
| C2 | 5 | diatomic |
| Si | 5 | atomic |