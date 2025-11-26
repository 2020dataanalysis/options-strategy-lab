# **options-strategy-lab**

A small research toolkit for generating, evaluating, and ranking **options trading structures** — currently focused on **Broken Wing Butterflies (BWB)**.
This project loads a flattened option chain (from Schwab API), filters/selects an expiry, generates candidate structures, computes payoff-based metrics, and outputs a ranked list.

This repository is structured as a minimal, clean, testable prototype for strategy research.

---

## **Features**

### ✔ Reads flattened option chain data

CSV format with columns like:

```
underlying, underlying_price, put_call, option_symbol, root, expiry,
strike, mid, delta, volume, open_interest, iv, intrinsic_value, extrinsic_value, ...
```

### ✔ Generates **Broken Wing Butterfly (BWB)** structures

For a call BWB:

* Long 1 @ K1
* Short 2 @ K2
* Long 1 @ K3
* With asymmetric wings: `(K2 - K1) != (K3 - K2)`

### ✔ Computes payoff metrics

For each structure the system computes:

* `pnl_low`
* `pnl_at_k2`
* `pnl_high`
* `max_profit`
* `max_loss`
* `score = max_profit / max_loss`

### ✔ Outputs a sorted list/table

Ranked by highest **reward-to-risk** score.

---

## **Repository Structure**

```
options-strategy-lab/
│
├── data/
│   ├── raw/                     ← raw chain JSON
│   └── flat/                    ← flattened chain CSVs
│       └── aapl_chain_flat.csv
│
├── src/options_strategy_lab/
│   ├── data_loader.py           ← load CSV, slice ticker/expiry
│   ├── strategies.py            ← generate_BWB_candidates()
│   ├── scoring.py               ← scoring & payoff functions
│   └── __init__.py              ← run_bwb_scan() pipeline
│
├── scripts/
│   └── run_bwb_scan.py          ← example execution script
│
├── notebooks/
│   └── README.md                ← optional analysis notes
│
├── tests/                       ← unit tests
│
├── pyproject.toml               ← package config
├── requirements.txt
└── README.md                    ← this file
```

---

## **Installation**

Create a virtual environment (recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install in editable mode:

```bash
python -m pip install -e .
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## **Usage**

### Run the BWB scanner on AAPL:

```bash
python scripts/run_bwb_scan.py
```

This:

1. Loads `data/flat/aapl_chain_flat.csv`
2. Selects `CALL` options for one expiry (default: `"2025-11-28"`)
3. Generates BWB candidates
4. Computes payoff metrics
5. Outputs a ranked list

### Example Output

```
python scripts/run_bwb_scan.py
Total rows in CSV: 400
Unique expiry values: ['2025-11-28' '2025-12-05' '2025-12-12' '2025-12-19' '2025-12-26'
 '2026-01-02' '2026-01-16' '2026-02-20' '2026-03-20' '2026-04-17'
 '2026-05-15' '2026-06-18' '2026-07-17' '2026-08-21' '2026-09-18'
 '2026-12-18' '2027-01-15' '2027-06-17' '2027-12-17' '2028-01-21']

   underlying      expiry     k1     k2     k3  credit  ...  pnl_low  pnl_at_k2  pnl_high  max_profit  max_loss      score
0        AAPL  2025-11-28  265.0  267.5  272.5   2.400  ...    2.400      4.900    -0.100       4.900     0.100  49.000000
1        AAPL  2025-11-28  265.0  267.5  275.0   4.350  ...    4.350      6.850    -0.650       6.850     0.650  10.538462
99       AAPL  2025-11-28  280.0  285.0  287.5  -0.505  ...   -0.505      4.495     1.995       4.495     0.505   8.900990
32       AAPL  2025-11-28  267.5  270.0  275.0   1.875  ...    1.875      4.375    -0.625       4.375     0.625   7.000000
2        AAPL  2025-11-28  265.0  267.5  277.5   5.905  ...    5.905      8.405    -1.595       8.405     1.595   5.269592

```

---

## **API Overview**

### **`run_bwb_scan(csv_path, underlying, expiry)`**

Full pipeline:

* load CSV
* slice by ticker/expiry
* generate BWBs
* score
* sort
* return DataFrame

### **`generate_bwb_candidates(calls_df)`**

Enumerates all valid broken-wing butterflies.

### **`score_broken_wing_butterflies(df)`**

Adds:

* payoff points
* max profit
* max loss
* score

### **`sort_by_score(df)`**

Sorts descending by score.

---

## **Roadmap**

Future extension points:

* Add **Vertical Credit Spreads**
* Add **filters** (delta range, credit min, OI, etc.)
* Add payoff plotting
* Add API service wrapper (FastAPI)
* Implement multi-ticker batch scans

---

## **License**

MIT License (permissive for interview and further development).

---