# src/options_strategy_lab/data_loader.py

import pandas as pd
from pathlib import Path


def load_chain_csv(path: str) -> pd.DataFrame:
    """
    Load a flattened options chain from CSV.

    Expected columns (at minimum):
      underlying, expiry, put_call, strike, mid, delta, days_to_expiration
    """
    path = Path(path)
    df = pd.read_csv(path)

    # Normalize column names (lowercase, strip spaces)
    df.columns = [c.strip().lower() for c in df.columns]

    # Handle possible alternative names
    rename_map = {}

    # our CSV has "days_to_expiration" already, but if not:
    if "dte" in df.columns and "days_to_expiration" not in df.columns:
        rename_map["dte"] = "days_to_expiration"

    # sometimes people use "option_type" instead of "put_call"
    if "option_type" in df.columns and "put_call" not in df.columns:
        rename_map["option_type"] = "put_call"

    if rename_map:
        df = df.rename(columns=rename_map)

    return df


def select_ticker_and_expiry(
    df: pd.DataFrame,
    ticker: str,
    expiry: str,
    put_call: str = "CALL",
) -> pd.DataFrame:
    """
    Slice the chain down to a single underlying, expiry, and option type.

    Returns one row per strike with:
      underlying, expiry, strike, mid, delta, days_to_expiration
    """
    # work on a copy
    df2 = df.copy()

    # sanity: show what unique values exist (you can uncomment prints while debugging)
    # print("unique underlying:", df2["underlying"].unique())
    # print("unique expiry:", df2["expiry"].unique())
    # print("unique put_call:", df2["put_call"].unique())

    # Ensure the key columns are there
    required_cols = {"underlying", "expiry", "put_call", "strike", "mid", "delta", "days_to_expiration"}
    missing = required_cols - set(df2.columns)
    if missing:
        raise ValueError(f"Missing columns in chain CSV: {missing}")

    mask = (
        (df2["underlying"] == ticker)
        & (df2["put_call"].str.upper() == put_call.upper())
        & (df2["expiry"].astype(str) == str(expiry))
    )

    slice_df = df2.loc[mask, ["underlying", "expiry", "strike", "mid", "delta", "days_to_expiration"]].copy()

    # Clean types
    slice_df["strike"] = slice_df["strike"].astype(float)
    slice_df["mid"] = slice_df["mid"].astype(float)
    slice_df["delta"] = slice_df["delta"].astype(float)
    slice_df["days_to_expiration"] = slice_df["days_to_expiration"].astype(int)

    return slice_df
