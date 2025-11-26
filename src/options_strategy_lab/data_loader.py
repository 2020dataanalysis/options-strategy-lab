# src/options_strategy_lab/data_loader.py
from pathlib import Path
import pandas as pd


def load_chain_csv(path: str) -> pd.DataFrame:
    """
    Load flattened options chain CSV.

    Expected columns (from your aapl_chain_flat.csv):
        underlying, underlying_price, put_call, option_symbol, root, expiry,
        dte_key, days_to_expiration, strike, bid, ask, mid, last, mark,
        volume, open_interest, iv, delta, gamma, theta, vega, rho,
        intrinsic_value, extrinsic_value, in_the_money, expiration_type,
        exercise_type, interest_rate_chain, base_chain_iv
    """
    path = Path(path)
    df = pd.read_csv(path)

    # basic sanity checks (optional, but nice for the assignment)
    required_cols = {"underlying", "expiry", "put_call", "strike", "mid", "days_to_expiration", "delta"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    return df


def select_ticker_and_expiry(
    df: "pd.DataFrame",
    ticker: str,
    expiry: str,
    call_only: bool = True,
) -> "pd.DataFrame":
    """
    Filter the chain to a single underlying + expiry (and calls only, by default).
    """
    mask = (df["underlying"] == ticker) & (df["expiry"] == expiry)
    if call_only:
        mask &= df["put_call"] == "CALL"
    return df.loc[mask].copy()
