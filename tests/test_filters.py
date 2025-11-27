# src/options_strategy_lab/filters.py

from typing import Optional, Iterable
import pandas as pd

def filter_bwb_candidates(
    bwb_df: Iterable,
    min_credit: Optional[float] = 0.0,
    min_dte: Optional[int] = None,
    max_dte: Optional[int] = None,
    min_short_delta: Optional[float] = None,
    max_short_delta: Optional[float] = None,
) -> pd.DataFrame:
    """
    PURPOSE
    -------
    Apply fast, interpretable filters to a list/DataFrame of candidate 
    Broken-Wing Butterflies (BWBs).

    We filter BEFORE scoring, so we don’t waste compute on spreads that 
    would never be traded (ex: too little credit, too far DTE, wrong deltas).

    INPUT
    -----
    `bwb_df` is expected to be either:
      - a pandas DataFrame, OR
      - a list of dictionaries (each dict = one spread)
  
    EXPECTED COLUMNS:
      credit        : net premium collected when opening the BWB
      dte           : days to expiration
      short_delta   : the delta of the short strike (key for risk)
    
    OPTIONAL FILTERS:
      min_credit      – require spreads to return at least X credit
      min_dte         – minimum days to expiration
      max_dte         – maximum days to expiration
      min_short_delta – filter based on “short strike delta” range
      max_short_delta – e.g. keep only 20–40 delta spreads
    
    This returns a clean DataFrame of viable trades.
    """

    # Convert any list-of-dicts automatically into a DataFrame
    # This gives us a consistent structure to apply filtering logic.
    df = pd.DataFrame(bwb_df)

    # `mask` starts as "True for every row", then we AND conditions to it.
    # This allows stacking an arbitrary number of filters.
    mask = pd.Series(True, index=df.index)

    # Require a minimum credit (default = 0, meaning >= 0)
    if min_credit is not None:
        mask &= df["credit"] >= min_credit

    # Minimum DTE (e.g. only trade spreads expiring in >= 3 days)
    if min_dte is not None:
        mask &= df["dte"] >= min_dte

    # Maximum DTE (e.g. exclude long-dated spreads outside our timeframe)
    if max_dte is not None:
        mask &= df["dte"] <= max_dte

    # Minimum delta allowed for the short strike
    # Example: min_short_delta = 0.10 means “avoid ultra-low delta wings.”
    if min_short_delta is not None:
        mask &= df["short_delta"] >= min_short_delta

    # Maximum delta for short strike
    # Example: max_short_delta = 0.40 -> avoids deep ITM structures.
    if max_short_delta is not None:
        mask &= df["short_delta"] <= max_short_delta

    # Final filtered DataFrame
    return df.loc[mask].reset_index(drop=True)
