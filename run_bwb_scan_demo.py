from options_strategy_lab import run_bwb_scan

if __name__ == "__main__":
    results = run_bwb_scan(
        "data/flat/aapl_chain_flat.csv",
        "AAPL",
        "2025-11-28",
        apply_filters=True,          # 👈 turn filters on
        min_credit=0.50,             # optional, uses defaults if omitted
        min_short_delta=0.10,
        max_short_delta=0.90,
    )
    print(results)
