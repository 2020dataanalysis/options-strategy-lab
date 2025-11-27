# src/options_strategy_lab/filters.py

from typing import Optional, Union, Sequence
from collections.abc import Mapping
import pandas as pd


def filter_bwb_candidates(
    candidates: Union[pd.DataFrame, Sequence[Mapping]],
    min_credit: Optional[float] = 0.0,
    min_dte: Optional[int] = None,
    max_dte: Optional[int] = None,
    min_short_delta: Optional[float] = None,
    max_short_delta: Optional[float] = None,
) -> pd.DataFrame:
    """
    Apply simple, interpretable filters to BWB candidates.

    Accepts either:
      - a pandas DataFrame, or
      - a sequence (list/tuple) of dict-like objects.

    Expected columns/keys:
      - credit
      - dte              (days to expiration)
      - short_delta      (abs(delta) of short strike)
    """

    # 1. Normalize input to a DataFrame
    if isinstance(candidates, pd.DataFrame):
        df = candidates.copy()
    else:
        # We expect a list/sequence of mapping-like rows
        if not isinstance(candidates, Sequence) or len(candidates) == 0:
            raise ValueError("candidates must be a non-empty DataFrame or sequence of dict-like objects")

        first = candidates[0]
        if not isinstance(first, Mapping):
            raise TypeError(
                f"When passing a sequence, each element must be dict-like with keys "
                f"'credit', 'dte', 'short_delta'. Got element of type {type(first)}."
            )

        # Now we can safely build a DataFrame from list-of-dicts
        df = pd.DataFrame(candidates)

    # 2. Sanity-check required columns
    required_cols = {"credit", "dte", "short_delta"}
    missing = required_cols - set(df.columns)
    if missing:
        raise KeyError(f"Missing required columns in candidates: {missing}")

    # 3. Start with all rows passing
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
