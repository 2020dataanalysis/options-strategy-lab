# src/options_strategy_lab/__init__.py

from .data_loader import load_chain_csv, select_ticker_and_expiry
from .strategies import generate_bwb_candidates
from .scoring import score_broken_wing_butterflies, sort_by_score


def run_bwb_scan(
    chain_csv_path: str,
    underlying: str,
    expiry: str,
    top_n: int = 20,
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

    bwb_scored = score_broken_wing_butterflies(bwb_candidates)
    bwb_sorted = sort_by_score(bwb_scored, top_n=top_n)

    return bwb_sorted
