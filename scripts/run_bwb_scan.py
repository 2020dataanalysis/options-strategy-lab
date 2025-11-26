from pathlib import Path
from options_strategy_lab.data_loader import load_chain_csv, select_ticker_and_expiry

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CHAIN_CSV = PROJECT_ROOT / "data" / "flat" / "aapl_chain_flat.csv"

if __name__ == "__main__":
    df = load_chain_csv(str(CHAIN_CSV))
    print("Total rows in CSV:", len(df))
    print("Unique expiry values:", df["expiry"].unique())

    from options_strategy_lab import run_bwb_scan

    results = run_bwb_scan(
        chain_csv_path=str(CHAIN_CSV),
        underlying="AAPL",
        expiry="2025-11-28",
        top_n=20,
    )
    print(results.head())
