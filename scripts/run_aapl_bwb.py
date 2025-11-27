# scripts/run_aapl_bwb.py

from options_strategy_lab import run_bwb_scan

if __name__ == "__main__":
    results = run_bwb_scan(
        chain_csv_path="data/flat/aapl_chain_flat.csv",
        underlying="AAPL",
        expiry="2025-11-28",
        top_n=20,
    )
    print(results.to_string(index=False))
