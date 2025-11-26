# src/options_strategy_lab/data_loader.py

import pandas as pd
from pathlib import Path


def load_chain_csv(csv_path: str) -> pd.DataFrame:
    """
    Load a flattened options chain CSV into a DataFrame.

    Expected columns include at least:
      - underlying
      - expiry
      - put_call
      - strike
      - mid
      - delta
      - days_to_expiration
    """
    path = Path(csv_path)
    df = pd.read_csv(path)

    # Normalize column names just in case (strip spaces, lower-case)
    df.columns = [c.strip() for c in df.columns]

    return df


def select_ticker_and_expiry(
    df: pd.DataFrame,
    *,
    underlying: str,
    expiry: str,
    put_call: str | None = None,
) -> pd.DataFrame:
    """
    Slice the flattened chain for:
      - a single underlying symbol
      - a single expiry (string, e.g. '2025-11-28')
      - optional put_call filter ('CALL' or 'PUT')

    Returns a DataFrame filtered to those rows.
    """

    mask = (df["underlying"] == underlying) & (df["expiry"] == expiry)

    if put_call is not None:
        mask &= df["put_call"] == put_call

    out = df.loc[mask].copy().reset_index(drop=True)
    return out
