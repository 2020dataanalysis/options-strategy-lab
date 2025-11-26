from options_strategy_lab import run_bwb_scan

if __name__ == "__main__":
    results = run_bwb_scan("data/flat/aapl_chain_flat.csv", "AAPL", "2025-11-28")
    print(results.head())
