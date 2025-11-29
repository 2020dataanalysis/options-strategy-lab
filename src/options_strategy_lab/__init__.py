# src/options_strategy_lab/__init__.py

from typing import Optional
from .data_loader import load_chain_csv, select_ticker_and_expiry
from .strategies import generate_bwb_candidates
from .scoring import (
    score_broken_wing_butterflies,
    sort_by_score,
    apply_basic_filters,
)


def run_bwb_scan(
    chain_csv_path: str,
    underlying: str,
    expiry: str,
    top_n: int = 20,
    apply_filters: bool = False,
    min_credit: float = 0.50,
    min_short_delta: float = 0.10,
    max_short_delta: float = 0.30,
    min_dte: int = 1,
    max_dte: Optional[int] = None,
):
    """
    End-to-end:
      - load CSV
      - slice to one underlying + expiry + CALLs
      - generate BWB structures
      - score and sort
    """
    df = load_chain_csv(chain_csv_path)

    calls_slice = select_ticker_and_expiry(
        df,
        ticker=underlying,
        expiry=expiry,
        put_call="CALL",
    )

    if calls_slice.empty:
        print("No CALL rows found for", underlying, expiry)
        return calls_slice  # empty

    bwb_candidates = generate_bwb_candidates(calls_slice)

    if bwb_candidates.empty:
        print("No BWB combinations generated (maybe too few strikes?).")
        return bwb_candidates



    # 🔽🔽🔽 THIS is where your `if apply_filters:` block goes 🔽🔽🔽
    if apply_filters:
        before = len(bwb_candidates)
        bwb_candidates = apply_basic_filters(
            bwb_candidates,
            min_credit=min_credit,
            min_dte=min_dte,
            max_dte=max_dte,
            min_short_delta=min_short_delta,
            max_short_delta=max_short_delta,
        )
        after = len(bwb_candidates)
        print(
            f"Filters applied: {before} → {after} BWB candidates "
            f"(min_credit={min_credit}, short_delta∈[{min_short_delta}, {max_short_delta}])"
        )
        if bwb_candidates.empty:
            print("All BWB candidates filtered out.")
            return bwb_candidates
    # 🔼🔼🔼 end of filter block 🔼🔼🔼



    bwb_scored = score_broken_wing_butterflies(bwb_candidates)
    bwb_sorted = sort_by_score(bwb_scored, top_n=top_n)

    return bwb_sorted
