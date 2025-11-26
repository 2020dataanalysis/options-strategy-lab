# src/options_strategy_lab/__init__.py

from typing import Optional

from .data_loader import load_chain_csv, select_ticker_and_expiry
from .strategies import generate_bwb_candidates
from .filters import filter_broken_wing_butterflies
from .scoring import score_broken_wing_butterflies, sort_by_score


def run_bwb_scan(
    csv_path: str,
    underlying: str,
    expiry: str,
    *,
    # default filter knobs – you can tweak for the assignment
    min_credit: float = 0.0,
    min_dte: Optional[int] = None,
    max_dte: Optional[int] = None,
    min_short_delta: Optional[float] = None,
    max_short_delta: Optional[float] = None,
):
    """
    High-level pipeline:

      1) Load flattened chain CSV
      2) Slice to (underlying, expiry, CALL)
      3) Generate BWB candidates
      4) Filter candidates
      5) Score & rank by score
    """
    chain_df = load_chain_csv(csv_path)

    calls_slice = select_ticker_and_expiry(
        chain_df,
        underlying=underlying,
        expiry=expiry,
        put_call="CALL",
    )

    bwb_candidates = generate_bwb_candidates(calls_slice)

    filtered = filter_broken_wing_butterflies(
        bwb_candidates,
        min_credit=min_credit,
        min_dte=min_dte,
        max_dte=max_dte,
        min_short_delta=min_short_delta,
        max_short_delta=max_short_delta,
    )

    scored = score_broken_wing_butterflies(filtered)
    ranked = sort_by_score(scored)

    return ranked
