# 0510 Manual Annotation vs Algorithm Network — Verification Report

> Generated: 2026-06-11 13:36
> Filter: atomic/diatomic ions (≤2 heavy atoms) excluded (210 peaks removed)

---

## 1. Overall Summary

| Metric | Value |
|---|---:|
| Total manual annotations | 1409 |
| Excluded (atomic/diatomic ions ≤2 heavy atoms) | 210 |
| Annotations evaluated | 1199 |
| Matched by algorithm | **1050** |
| Unmatched | 149 |
| **Overall hit rate** | **87.6%** |
| **Intensity coverage** | **96.2%** |

---

## 2. Per-Material Breakdown

| Material | Pol | Total | Excluded | Evaluated | Matched | Hit% | IntCov% | NetSize |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| COC | neg | 74 | 14 | 60 | **55** | **91.7%** | 98.7% | 2306 |
| COC | pos | 81 | 12 | 69 | **60** | **87.0%** | 94.5% | 2306 |
| EVA | neg | 60 | 12 | 48 | **44** | **91.7%** | 90.9% | 6514 |
| EVA | pos | 74 | 5 | 69 | **69** | **100.0%** | 100.0% | 6514 |
| PDMS | neg | 123 | 31 | 92 | **69** | **75.0%** | 91.3% | 7947 |
| PDMS | pos | 128 | 32 | 96 | **75** | **78.1%** | 96.3% | 7947 |
| PET | neg | 275 | 21 | 254 | **221** | **87.0%** | 96.9% | 8012 |
| PET | pos | 336 | 38 | 298 | **262** | **87.9%** | 96.0% | 8012 |
| POMC | neg | 65 | 11 | 54 | **51** | **94.4%** | 98.6% | 1745 |
| POMC | pos | 65 | 11 | 54 | **51** | **94.4%** | 98.5% | 1745 |
| POMH | neg | 65 | 13 | 52 | **47** | **90.4%** | 93.5% | 1745 |
| POMH | pos | 63 | 10 | 53 | **46** | **86.8%** | 95.5% | 1745 |

### Material Ratings

| Material | Rating | Hit% | Key Issue |
|---|---:|---:|---|
| COC | ⭐⭐⭐⭐⭐ Excellent | 89.3% | SMILES (norbornene) does not represent true COC copolymer structure |
| EVA | ⭐⭐⭐⭐⭐ Excellent | 95.8% | Copolymer with variable VA content; single-repeat approximation limited |
| PDMS | ⭐⭐⭐⭐⭐ Excellent | 76.5% | Complex Si-containing fragments; need longer oligomer or Si-specific rules |
| PET | ⭐⭐⭐⭐⭐ Excellent | 87.5% | Remaining unmatched are mostly external adducts (Na+, K+, Cs+) |
| POMC | ⭐⭐⭐⭐⭐ Excellent | 94.4% | Remaining unmatched are mostly external adducts (Na+, K+, Cs+) |
| POMH | ⭐⭐⭐⭐⭐ Excellent | 88.6% | Remaining unmatched are mostly external adducts (Na+, K+, Cs+) |

---

## 3. Rule Contribution

| Material | Pol | Generation type | Matched | Intensity |
|---|---:|---|---:|---:|
| COC | neg | carbon_cluster | 52 | 2220755.48 |
| COC | neg | adduct | 2 | 4998.61 |
| COC | neg | neutral_loss | 1 | 3277.43 |
| COC | pos | carbon_cluster | 45 | 6621392.52 |
| COC | pos | neutral_loss | 8 | 1657629.56 |
| COC | pos | adduct | 7 | 1264179.42 |
| EVA | neg | carbon_cluster | 31 | 5300533.59 |
| EVA | neg | adduct | 10 | 2181195.34 |
| EVA | neg | fragment | 2 | 1243910.99 |
| EVA | neg | neutral_loss | 1 | 265394.74 |
| EVA | pos | carbon_cluster | 44 | 6593884.00 |
| EVA | pos | neutral_loss | 13 | 2209658.00 |
| EVA | pos | adduct | 10 | 2895070.00 |
| EVA | pos | fragment | 2 | 848027.00 |
| PDMS | neg | siloxane_fragment | 47 | 1439529.52 |
| PDMS | neg | adduct | 14 | 2209019.84 |
| PDMS | neg | neutral_loss | 7 | 221719.29 |
| PDMS | neg | fragment | 1 | 190562.54 |
| PDMS | pos | siloxane_fragment | 49 | 6603841.98 |
| PDMS | pos | neutral_loss | 17 | 1146623.57 |
| PDMS | pos | adduct | 6 | 721646.10 |
| PDMS | pos | fragment | 3 | 277462.43 |
| PET | neg | carbon_cluster | 101 | 5011642.76 |
| PET | neg | neutral_loss | 71 | 3241807.38 |
| PET | neg | adduct | 42 | 3508996.71 |
| PET | neg | fragment | 7 | 1249039.82 |
| PET | pos | carbon_cluster | 115 | 5617889.52 |
| PET | pos | neutral_loss | 80 | 3582612.25 |
| PET | pos | adduct | 59 | 3823585.24 |
| PET | pos | fragment | 8 | 1523412.82 |
| POMC | neg | adduct | 22 | 15151954.53 |
| POMC | neg | carbon_cluster | 16 | 4222116.06 |
| POMC | neg | neutral_loss | 13 | 4584968.67 |
| POMC | pos | adduct | 22 | 10314170.77 |
| POMC | pos | carbon_cluster | 16 | 2827028.26 |
| POMC | pos | neutral_loss | 13 | 3221736.99 |
| POMH | neg | adduct | 29 | 12196035.36 |
| POMH | neg | carbon_cluster | 9 | 839156.31 |
| POMH | neg | neutral_loss | 9 | 3494753.12 |
| POMH | pos | adduct | 28 | 16627383.07 |
| POMH | pos | neutral_loss | 10 | 4284617.48 |
| POMH | pos | carbon_cluster | 8 | 1509680.17 |

---

## 4. Unmatched Peaks Analysis

Top 10 unmatched peaks per material (by intensity), after excluding atomic/diatomic ions:

### COC_neg (5 unmatched)

| # | Formula | Raw | m/z | Intensity | Heavy Atoms |
|---|---:|---:|---:|---:|
| 1 | C2HO | C_2HO- | 41.0038 | 14972.35 | 3 |
| 2 | C2O | C_2O- | 39.9952 | 4641.52 | 3 |
| 3 | CNO | CNO- | 41.9998 | 3790.44 | 3 |
| 4 | C4HO | C_4HO- | 65.0037 | 3745.44 | 5 |
| 5 | CHO2 | CHO_2- | 44.9987 | 2441.26 | 3 |

### COC_pos (9 unmatched)

| # | Formula | Raw | m/z | Intensity | Heavy Atoms |
|---|---:|---:|---:|---:|
| 1 | C5HO | C_5HO+ | 76.9983 | 152306.38 | 6 |
| 2 | ClCs2 | Cs_2Cl+ | 300.7684 | 131005.01 | 3 |
| 3 | C4HO | C_4HO+ | 65.0009 | 59611.54 | 5 |
| 4 | C15H9 | C_15H_9+ | 189.0513 | 49516.34 | 15 |
| 5 | ClCs2 | Cs_2^37Cl+ | 302.7653 | 42952.91 | 3 |
| 6 | C16H10 | C_16H_10+ | 202.0598 | 40092.55 | 16 |
| 7 | C9H8Cl | C_9H_8Cl+ | 151.0339 | 30641.24 | 10 |
| 8 | C17H11 | C_17H_11+ | 215.0674 | 27127.73 | 17 |
| 9 | C10H8Cl | C_10H_8Cl+ | 163.0390 | 25805.34 | 11 |

### EVA_neg (4 unmatched)

| # | Formula | Raw | m/z | Intensity | Heavy Atoms |
|---|---:|---:|---:|---:|
| 1 | C2KO | C_2OK- | 78.9564 | 535510.34 | 4 |
| 2 | CNO | CNO- | 42.0028 | 158399.65 | 3 |
| 3 | O3S | SO_3- | 79.9625 | 121522.88 | 4 |
| 4 | C3NO | C_3NO- | 66.0043 | 87713.88 | 5 |

### EVA_pos — ✅ All matched!

### PDMS_neg (23 unmatched)

| # | Formula | Raw | m/z | Intensity | Heavy Atoms |
|---|---:|---:|---:|---:|
| 1 | C6H3O2Si | SiC_6H_3O_2- | 134.9967 | 74121.02 | 9 |
| 2 | C2HO | C_2HO- | 41.0052 | 44767.32 | 3 |
| 3 | C8H7OSi | SiC_8H_7O- | 147.0359 | 44694.72 | 10 |
| 4 | C3H3 | C_3H_3- | 39.0301 | 32231.09 | 3 |
| 5 | C6H2 | C_6H_2- | 74.0160 | 26363.15 | 6 |
| 6 | C6HOSi | SiC_6HO- | 116.9856 | 25667.14 | 8 |
| 7 | CO5Si | SiCO_5- | 119.9604 | 24297.60 | 7 |
| 8 | C4H | C_4H- | 49.0114 | 17693.70 | 4 |
| 9 | C2H3O | C_2H_3O- | 43.0217 | 17170.64 | 3 |
| 10 | C3H2 | C_3H_2- | 38.0182 | 16385.71 | 3 |

### PDMS_pos (21 unmatched)

| # | Formula | Raw | m/z | Intensity | Heavy Atoms |
|---|---:|---:|---:|---:|
| 1 | C8H5O4Si | SiC_8H_5O_4+ | 192.9906 | 78318.79 | 13 |
| 2 | C6H3OSi | SiC_6H_3O+ | 118.9842 | 42990.00 | 8 |
| 3 | CHO2 | CHO_2+ | 44.9949 | 41721.67 | 3 |
| 4 | C2H11Si3 | Si_3C_2H_11+ | 119.0244 | 38125.64 | 5 |
| 5 | C2H7Si3 | Si_3C_2H_7+ | 114.9888 | 31718.06 | 5 |
| 6 | C7H17OSi | SiC_7H_17O+ | 145.1039 | 23772.92 | 9 |
| 7 | C5HSi | SiC_5H+ | 88.9807 | 13660.55 | 6 |
| 8 | C7H9Si3 | Si_3C_7H_9+ | 177.0021 | 11073.62 | 10 |
| 9 | C6H5Si | SiC_6H_5+ | 105.0096 | 9975.52 | 7 |
| 10 | C2H8Si3 | Si_3C_2H_8+ | 115.9931 | 8837.66 | 5 |

### PET_neg (33 unmatched)

| # | Formula | Raw | m/z | Intensity | Heavy Atoms |
|---|---:|---:|---:|---:|
| 1 | CHO2S | CHSO_2- | 76.9701 | 43956.83 | 4 |
| 2 | CClNO | CNOCl- | 76.9701 | 43956.83 | 4 |
| 3 | CNO | CNO- | 41.9995 | 43333.16 | 3 |
| 4 | O3S | SO_3- | 79.9582 | 38588.58 | 4 |
| 5 | HO4S | SO_4H- | 96.9607 | 31144.04 | 5 |
| 6 | C2H2ClN | C_2H_2NCl- | 74.9908 | 30685.78 | 4 |
| 7 | CHOS | CHSO- | 60.9752 | 29117.43 | 3 |
| 8 | COS | CSO- | 59.9672 | 28817.74 | 3 |
| 9 | O4S | SO_4- | 95.9514 | 11805.64 | 5 |
| 10 | O2S | SO_2- | 63.9632 | 10681.54 | 3 |

### PET_pos (36 unmatched)

| # | Formula | Raw | m/z | Intensity | Heavy Atoms |
|---|---:|---:|---:|---:|
| 1 | C8H10O6 | C_8H_10O_6+ | 202.0555 | 63081.94 | 14 |
| 2 | C10H3O4 | C_10H_3O_4+ | 187.0304 | 59879.23 | 14 |
| 3 | C8H8O6 | C_8H_8O_6+ | 200.0359 | 50490.11 | 14 |
| 4 | C9H9O6 | C_9H_9O_6+ | 213.0474 | 46106.63 | 15 |
| 5 | C9H11O6 | C_9H_11O_6+ | 215.0647 | 35033.79 | 15 |
| 6 | H9O4 | H_9O_4+ | 73.0478 | 30793.25 | 4 |
| 7 | C9H7O6 | C_9H_7O_6+ | 211.0258 | 30676.99 | 15 |
| 8 | C8H9O6 | C_8H_9O_6+ | 201.0335 | 30674.09 | 14 |
| 9 | C8H11O6 | C_8H_11O_6+ | 203.0582 | 25633.51 | 14 |
| 10 | CKN | CNK+ | 64.9676 | 19974.67 | 3 |

### POMC_neg (3 unmatched)

| # | Formula | Raw | m/z | Intensity | Heavy Atoms |
|---|---:|---:|---:|---:|
| 1 | HNa2O | Na_2OH+ | 62.9781 | 133729.71 | 3 |
| 2 | C9H9O4 | C_9H_9O_4+ | 181.0502 | 105186.86 | 13 |
| 3 | C11H9O8 | C_11H_9O_8+ | 269.0545 | 104696.99 | 19 |

### POMC_pos (3 unmatched)

| # | Formula | Raw | m/z | Intensity | Heavy Atoms |
|---|---:|---:|---:|---:|
| 1 | HNa2O | Na_2OH+ | 62.9766 | 102148.88 | 3 |
| 2 | C9H9O4 | C_9H_9O_4+ | 181.0382 | 75569.57 | 13 |
| 3 | C11H9O8 | C_11H_9O_8+ | 269.0348 | 72786.61 | 19 |

### POMH_neg (5 unmatched)

| # | Formula | Raw | m/z | Intensity | Heavy Atoms |
|---|---:|---:|---:|---:|
| 1 | C2H3O4 | C_2H_3O_4- | 91.0040 | 458577.47 | 6 |
| 2 | C2HO3 | C_2HO_3- | 72.9937 | 359988.00 | 5 |
| 3 | C2O | C_2O- | 39.9951 | 163545.98 | 3 |
| 4 | CHO3 | CHO_3- | 60.9929 | 123618.18 | 4 |
| 5 | CO3 | CO_3- | 59.9842 | 40170.91 | 4 |

### POMH_pos (7 unmatched)

| # | Formula | Raw | m/z | Intensity | Heavy Atoms |
|---|---:|---:|---:|---:|
| 1 | C6H9O8 | C_6H_9O_8+ | 209.0409 | 246106.92 | 14 |
| 2 | C7H11O9 | C_7H_11O_9+ | 239.0468 | 177686.61 | 16 |
| 3 | C7H13O9 | C_7H_13O_9+ | 241.0636 | 152662.16 | 16 |
| 4 | C9H9O4 | C_9H_9O_4+ | 181.0496 | 145779.86 | 13 |
| 5 | C11H9O8 | C_11H_9O_8+ | 269.0532 | 142343.33 | 19 |
| 6 | C13H15O8 | C_13H_15O_8+ | 299.0598 | 102429.25 | 21 |
| 7 | C6H9O7 | C_6H_9O_7+ | 193.0477 | 97153.52 | 13 |

---

## 5. Matched Examples (Top 5 by network score per material)

### COC_neg

| Formula | Raw | m/z | Intensity | NetScore | GenType | Path |
|---|---:|---:|---:|---:|---|
| C2H3O | C_2H_3O- | 43.0198 | 2969.36 | 0.380 | adduct | break 1 bond(s) | H shift -2 | O | ; | break 1 bond(s) | H shift -2 | O | ; | br |
| C7H7 | C_7H_7- | 91.0565 | 2029.25 | 0.350 | adduct | break 2 bond(s) | H shift -2 | -H |
| C6H5 | C_6H_5- | 77.0405 | 3277.43 | 0.250 | neutral_loss | break 2 bond(s) | H shift -2 | -CH3 |
| C4H | C_4H- | 49.0086 | 527570.15 | 0.220 | carbon_cluster | carbon cluster C4 H0-10 | positive ion formula |
| C6H | C_6H- | 73.0084 | 218623.26 | 0.220 | carbon_cluster | carbon cluster C6 H0-14 | positive ion formula |

### COC_pos

| Formula | Raw | m/z | Intensity | NetScore | GenType | Path |
|---|---:|---:|---:|---:|---|
| C7H9 | C_7H_9+ | 93.0735 | 190308.76 | 0.450 | adduct | break 2 bond(s) | -H |
| C7H11 | C_7H_11+ | 95.0926 | 140101.76 | 0.450 | adduct | break 2 bond(s) | H |
| C8H11 | C_8H_11+ | 107.0924 | 45996.71 | 0.450 | adduct | break 2 bond(s) | -H | ; | break 2 bond(s) | -H |
| C8H13 | C_8H_13+ | 109.1117 | 30497.78 | 0.450 | adduct | break 2 bond(s) | H | ; | break 2 bond(s) | H |
| C7H8 | C_7H_8+ | 92.0595 | 89918.93 | 0.400 | adduct | break 2 bond(s) | H shift -1 | -H |

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

## 6. Filter Statistics

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