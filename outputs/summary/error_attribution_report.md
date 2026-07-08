# Peak-Level Error Attribution Report
Each evaluated peak is categorized by where its best-matching network formula ranks:

- **rank_1_50**: matched in top 50 scored formulas
- **rank_51_100**: matched, rank 51-100
- **rank_101_200**: matched, rank 101-200
- **rank_201_500**: matched, rank 201-500
- **rank_500_plus**: matched, but buried very deep
- **missing**: no network formula within m/z tolerance at all

## Per-Material Rank Distribution

| Material | Peaks | rank1-50 | 51-100 | 101-200 | 201-500 | 500+ | missing | rMed | rP75 | rMax | Diagnosis |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| COC      |   10 | 90.0% |  0.0% |  0.0% |  0.0% |  0.0% | 10.0% |   28 |   32 |   40 | 🟢 OK (good top-50 coverage) |
| ETFE     |   18 | 33.3% | 27.8% |  0.0% |  0.0% |  0.0% | 38.9% |   34 |   58 |   75 | 🟢 OK (good top-50 coverage) |
| EVA      |   13 | 61.5% | 30.8% |  0.0% |  0.0% |  0.0% |  7.7% |   28 |   75 |   97 | 🟢 OK (good top-50 coverage) |
| FEP      |   20 | 40.0% |  0.0% |  0.0% |  0.0% |  0.0% | 60.0% |   12 |   14 |   20 | 🟢 OK (good top-50 coverage) |
| Nomex    |   12 | 16.7% | 41.7% | 33.3% |  0.0% |  0.0% |  8.3% |   99 |  102 |  123 | 🟡 RANKING (formulas exist but buried deep) |
| PEEK     |   13 | 38.5% | 53.8% |  0.0% |  0.0% |  0.0% |  7.7% |   64 |   67 |   71 | 🟢 OK (good top-50 coverage) |
| PEI      |   14 | 28.6% | 50.0% |  7.1% |  0.0% |  0.0% | 14.3% |   77 |   80 |  159 | 🟡 mixed |
| PEN      |   18 | 33.3% | 22.2% | 33.3% |  5.6% |  0.0% |  5.6% |   99 |  148 |  359 | 🟢 OK (good top-50 coverage) |
| PFA      |   20 | 45.0% |  0.0% |  0.0% |  0.0% |  0.0% | 55.0% |    4 |   13 |   15 | 🟢 OK (good top-50 coverage) |
| PI       |   16 | 31.2% | 50.0% |  0.0% |  0.0% |  0.0% | 18.8% |   68 |   73 |   78 | 🟢 OK (good top-50 coverage) |
| POMC     |   20 | 75.0% |  0.0% |  0.0% |  0.0% |  0.0% | 25.0% |    7 |   10 |   21 | 🟢 OK (good top-50 coverage) |
| POMH     |   21 | 81.0% |  0.0% |  0.0% |  0.0% |  0.0% | 19.0% |    7 |   11 |   21 | 🟢 OK (good top-50 coverage) |
| PPS      |   16 | 62.5% |  0.0% |  0.0% |  0.0% |  0.0% | 37.5% |    9 |   12 |   29 | 🟢 OK (good top-50 coverage) |
| PTFE     |    9 | 66.7% |  0.0% |  0.0% |  0.0% |  0.0% | 33.3% |    5 |   10 |   46 | 🟢 OK (good top-50 coverage) |
| PVDF     |   24 | 37.5% |  0.0% |  0.0% |  0.0% |  0.0% | 62.5% |   26 |   29 |   34 | 🟢 OK (good top-50 coverage) |

## Rank Distribution Statistics

| Material | rMin | rMedian | rP75 | rP90 | rMax |
|---|---:|---:|---:|---:|---:|
| COC      |    7 |   28 |   32 |   39 |   40 |
| ETFE     |    1 |   34 |   58 |   74 |   75 |
| EVA      |    1 |   28 |   75 |   91 |   97 |
| FEP      |    1 |   12 |   14 |   16 |   20 |
| Nomex    |    1 |   99 |  102 |  121 |  123 |
| PEEK     |    1 |   64 |   67 |   68 |   71 |
| PEI      |   13 |   77 |   80 |   81 |  159 |
| PEN      |   10 |   99 |  148 |  150 |  359 |
| PFA      |    1 |    4 |   13 |   14 |   15 |
| PI       |    3 |   68 |   73 |   76 |   78 |
| POMC     |    1 |    7 |   10 |   13 |   21 |
| POMH     |    1 |    7 |   11 |   16 |   21 |
| PPS      |    5 |    9 |   12 |   18 |   29 |
| PTFE     |    2 |    5 |   10 |   28 |   46 |
| PVDF     |    1 |   26 |   29 |   33 |   34 |

## Top-50 Intensity Peaks Analysis

Shows whether the STRONGEST peaks have network formulas and how they rank:

| Material | Top50Peaks | Matched | Missing | InRank1-50 | Diagnosis |
|---|---:|---:|---:|---:|---|
| COC      |   10 |    9 |    1 |    9 | 🟢 strong peaks well-covered |
| ETFE     |   18 |   11 |    7 |    6 | 🟢 strong peaks well-covered |
| EVA      |   13 |   12 |    1 |    8 | 🟢 strong peaks well-covered |
| FEP      |   20 |    8 |   12 |    8 | 🔴 strong peaks MISSING from network |
| Nomex    |   12 |   11 |    1 |    2 | 🟡 strong peaks matched but RANKED POORLY |
| PEEK     |   13 |   12 |    1 |    5 | 🟡 strong peaks matched but RANKED POORLY |
| PEI      |   14 |   12 |    2 |    4 | 🟡 strong peaks matched but RANKED POORLY |
| PEN      |   18 |   17 |    1 |    6 | 🟡 strong peaks matched but RANKED POORLY |
| PFA      |   20 |    9 |   11 |    9 | 🔴 strong peaks MISSING from network |
| PI       |   16 |   13 |    3 |    5 | 🟡 strong peaks matched but RANKED POORLY |
| POMC     |   20 |   15 |    5 |   15 | 🟢 strong peaks well-covered |
| POMH     |   21 |   17 |    4 |   17 | 🟢 strong peaks well-covered |
| PPS      |   16 |   10 |    6 |   10 | 🟢 strong peaks well-covered |
| PTFE     |    9 |    6 |    3 |    6 | 🟢 strong peaks well-covered |
| PVDF     |   24 |    9 |   15 |    9 | 🔴 strong peaks MISSING from network |