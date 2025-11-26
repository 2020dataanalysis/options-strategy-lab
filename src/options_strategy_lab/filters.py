# src/options_strategy_lab/filters.py

from __future__ import annotations
import pandas as pd


def filter_broken_wing_butterflies(
    bwb_df: pd.DataFrame,
    min_credit: float | None = 0.0,
    min_dte: int | None = None,
    max_dte: int | None = None,
    min_short_delta: float | None = None,
    max_short_delta: float | None = None,
) -> pd.DataFrame:
    """
    Apply simple, interpretable filters to BWB candidates.

    Assumes bwb_df has columns:
      - credit
      - dte              (days to expiration)
      - short_delta      (abs(delta) of short strike)
    """

    df = bwb_df.copy()
    mask = pd.Series(True, index=df.index)

    if min_credit is not None:
        mask &= df["credit"] >= min_credit

    if min_dte is not None:
        mask &= df["dte"] >= min_dte

    if max_dte is not None:
        mask &= df["dte"] <= max_dte

    if min_short_delta is not None:
        mask &= df["short_delta"] >= min_short_delta

    if max_short_delta is not None:
        mask &= df["short_delta"] <= max_short_delta

    return df.loc[mask].reset_index(drop=True)
