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
python run_bwb_scan_demo.py
Filters applied: 100 → 9 BWB candidates (min_credit=0.5, short_delta∈[0.1, 0.9])
  underlying      expiry     k1     k2     k3  credit  dte  short_delta  pnl_low  pnl_at_k2  pnl_high  max_profit  max_loss     score
0       AAPL  2025-11-28  270.0  272.5  277.5   1.205    3        0.825    1.205      3.705    -1.295       3.705     1.295  2.861004
1       AAPL  2025-11-28  270.0  272.5  280.0   2.130    3        0.825    2.130      4.630    -2.870       4.630     2.870  1.613240
5       AAPL  2025-11-28  272.5  275.0  280.0   0.530    3        0.673    0.530      3.030    -1.970       3.030     1.970  1.538071
2       AAPL  2025-11-28  270.0  272.5  282.5   2.535    3        0.825    2.535      5.035    -4.965       5.035     4.965  1.014099
6       AAPL  2025-11-28  272.5  275.0  282.5   0.935    3        0.673    0.935      3.435    -4.065       3.435     4.065  0.845018
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

## Assumptions

This prototype makes a number of simplifying assumptions to keep the problem focused on strategy construction and ranking rather than full production trading:

1. **Data snapshot & scope**

   * I work off a *single* flattened options chain snapshot (`aapl_chain_flat.csv`), not a live feed.
   * The universe is **one underlying (AAPL)** and **one expiry** at a time (e.g. 2025-11-28).
   * Only **standard equity options** are considered (no weeklies vs monthlies distinctions beyond the `expiration_type` field).

2. **Price inputs**

   * Option “price” for each leg is approximated by the **mid price**:
     [
     \text{mid} = \frac{\text{bid} + \text{ask}}{2}
     ]
   * No explicit modeling of **slippage** or **partial fills**; fills are assumed near mid for ranking purposes.
   * Payoffs are computed on a **per-share basis** and implicitly scaled by the standard contract multiplier (100) when interpreting P&L.

3. **Payoff and exercise style**

   * Broken-wing butterfly (BWB) payoffs are treated as if the options were **European-style** and held to expiry to evaluate:

     * P&L below K1 (far OTM),
     * P&L at the short strike K2,
     * P&L above K3 (far OTM on the other side).
   * Early exercise, assignment risk, and path-dependent effects are **ignored** for the scoring function (this is purely a static payoff snapshot).

4. **Interest rates, carry, and volatility**

   * A single chain-level **risk-free rate** field (`interest_rate_chain`) is used as a reference, but not fully integrated into pricing; pricing is based on the quoted chain, not a model.
   * The chain’s **implied volatility** (`iv` per strike, `base_chain_iv` for the chain) is treated as descriptive rather than used in a forward pricing model.
   * No **vol surface dynamics** are modeled; the system assumes current IV is a reasonable snapshot for ranking candidates right now.

5. **Transaction costs and capital**

   * **Commissions, fees, and margin requirements** are ignored in the score.
   * `max_profit` and `max_loss` are calculated from idealized payoffs of the structure, assuming the position can be opened at quoted mid prices.
   * No constraints are enforced around **buying power**, portfolio concentration, or risk limits.

6. **Filters and eligibility**

   * BWB candidates are built only from **CALL** strikes in ascending order (K1 < K2 < K3) with a defined wing asymmetry.
   * Filters are simple and interpretable:

     * `min_credit` to avoid tiny-credit structures,
     * `min_dte` / `max_dte` to keep trades in a desired time window,
     * `short_delta` bands to keep short strikes in a reasonable risk/likelihood range.
   * The scoring metric
     [
     \text{score} = \frac{\text{max_profit}}{\text{max_loss}}
     ]
     is used only as a *ranking heuristic*, not as a full risk-adjusted return measure.

---

## Next Steps if This Were Part of a Larger System

If this prototype were integrated into a full options-trading platform, I’d extend it along several axes:

1. **Data & ingestion**

   * Move from a CSV snapshot to a **live data pipeline** (e.g., Schwab / broker API) with:

     * scheduled chain refreshes,
     * support for **multiple underlyings** and **multiple expiries**,
     * persistent storage (e.g., Postgres, parquet in object storage) for historical analysis.
   * Add **data quality checks**: missing strikes, crossed markets, stale quotes, and corporate actions.

2. **Richer strategy layer**

   * Generalize the current BWB generator into a **strategy library**:

     * broken-wing butterflies (calls and puts),
     * symmetric butterflies,
     * vertical spreads / credit spreads,
     * iron condors and other multi-leg structures.
   * Provide a common representation for any multi-leg strategy (list of legs with side, size, strike, expiry, price) plus reusable payoff functions.

3. **Risk & P&L modeling**

   * Extend from static payoff at expiry to **scenario analysis**:

     * P&L vs underlying price *and* time (T+X days),
     * stress scenarios (e.g. ±2σ, vol crush/spike).
   * Integrate **transaction costs, fees, and fills** more realistically:

     * configurable commission schedule,
     * conservative fills (e.g. leaning toward bid/ask instead of mid).
   * Compute richer risk metrics:

     * breakeven points,
     * return on capital,
     * margin impact (if broker margin model is available).

4. **Feature engineering for ML / ranking**

   * Turn the current descriptive columns into a **feature set** for ranking / ML:

     * moneyness (K / spot),
     * skew between wings and underlying IV,
     * term structure (relative position vs other expiries),
     * liquidity features (volume, open interest, bid-ask width).
   * Use historical trade outcomes to learn **data-driven scores** instead of only `max_profit / max_loss`.

5. **User configuration and policy**

   * Expose filters as **user-level settings**:

     * preferred DTE window,
     * min credit, max defined risk,
     * target short delta range,
     * allowed underlyings / sectors.
   * Support **portfolio-aware constraints**:

     * per-ticker risk caps,
     * sector/industry diversification,
     * max number of open structures per expiry.

6. **Execution & integration**

   * Add an **order construction layer** that converts a chosen BWB into broker-specific order objects (e.g., multi-leg complex order).
   * Implement a **“preview vs place”** flow:

     * preview margin/commissions,
     * confirm via UI or API,
     * submit & monitor order status.
   * Integrate with **position tracking** so open BWBs can be monitored against the original entry assumptions and score.

7. **Monitoring, logging, and UX**

   * Log all candidate generation, filters applied, and final selections for **auditability**.
   * Build a simple **dashboard / notebook** layer:

     * tables of top candidates,
     * payoff diagrams,
     * historical performance per strategy template.
   * Add health checks and alerting for:

     * stale data,
     * failed API calls,
     * unusually thin or gappy markets.

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