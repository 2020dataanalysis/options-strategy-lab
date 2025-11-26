# src/options_strategy_lab/data_loader.py
from typing import Optional
import pandas as pd
from pathlib import Path


def load_chain_csv(csv_path: str) -> pd.DataFrame:
    """
    Load a flattened options chain CSV into a DataFrame.
    """
    path = Path(csv_path)
    df = pd.read_csv(path)

    # Normalize column names just in case (strip spaces)
    df.columns = [c.strip() for c in df.columns]

    return df


def select_ticker_and_expiry(
    df: pd.DataFrame,
    *,
    underlying: str,
    expiry: str,
    put_call: Optional[str] = None,
) -> pd.DataFrame:
    """
    Slice the flattened chain for:
      - a single underlying symbol
      - a single expiry (string, e.g. '2025-11-28')
      - optional put_call filter ('CALL' or 'PUT')

    We normalize:
      - underlying → stripped, uppercased
      - expiry    → first 10 chars (YYYY-MM-DD), stripped
    """

    df = df.copy()

    # Normalize underlying
    df["underlying_norm"] = (
        df["underlying"].astype(str).str.strip().str.upper()
    )

    # Normalize expiry: keep just 'YYYY-MM-DD'
    df["expiry_norm"] = (
        df["expiry"].astype(str).str.strip().str.slice(0, 10)
    )

    mask = (
        (df["underlying_norm"] == underlying.upper())
        & (df["expiry_norm"] == expiry)
    )

    if put_call is not None and "put_call" in df.columns:
        df["put_call_norm"] = (
            df["put_call"].astype(str).str.strip().str.upper()
        )
        mask &= df["put_call_norm"] == put_call.upper()

    out = df.loc[mask].copy().reset_index(drop=True)

    # Drop helper columns
    for col in ["underlying_norm", "expiry_norm", "put_call_norm"]:
        if col in out.columns:
            out.drop(columns=col, inplace=True)

    return out
