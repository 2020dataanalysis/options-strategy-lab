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
Total rows in CSV: 400
Unique expiry values: [...]
   underlying    expiry    k1    k2    k3  credit  ...  max_profit  max_loss  score
0       AAPL  2025-11-28  265.0  267.5  272.5  2.40  ...      4.90      0.10  49.00
1       AAPL  2025-11-28  265.0  267.5  275.0  4.35  ...      6.85      0.65  10.53
...
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