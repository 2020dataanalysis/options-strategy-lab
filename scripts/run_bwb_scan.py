# scripts/run_bwb_scan.py

from options_strategy_lab import run_bwb_scan

if __name__ == "__main__":
    results = run_bwb_scan(
        "data/flat/aapl_chain_flat.csv",
        "AAPL",
        "2025-11-28",
        min_credit=0.05,
        max_dte=45,
        max_short_delta=0.35,
    )
    print(results.head(20))
