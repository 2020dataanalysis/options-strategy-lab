# scripts/run_bwb_scan.py
from options_strategy_lab import run_bwb_scan

def main():
    results = run_bwb_scan(
        chain_csv_path="data/flat/aapl_chain_flat.csv",
        underlying="AAPL",
        expiry="2025-11-28",
    )
    print(results.head())

if __name__ == "__main__":
    main()
