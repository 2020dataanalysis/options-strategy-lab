# src/options_strategy_lab/__init__.py
from .data_loader import load_chain_csv, select_ticker_and_expiry
from .strategies import generate_bwb_candidates
from .scoring import apply_basic_filters, add_bwb_metrics_and_score


def run_bwb_scan(
    csv_path: str,
    ticker: str,
    expiry: str,
):
    df = load_chain_csv(csv_path)
    calls = select_ticker_and_expiry(df, ticker=ticker, expiry=expiry, call_only=True)
    bwb_raw = generate_bwb_candidates(calls)
    bwb_filtered = apply_basic_filters(bwb_raw)
    bwb_scored = add_bwb_metrics_and_score(bwb_filtered)
    return bwb_scored




# src/options_strategy_lab/__init__.py

from .data_loader import load_chain_csv, select_ticker_and_expiry
from .strategies import generate_bwb_candidates
from .scoring import score_broken_wing_butterflies, sort_by_score


def run_bwb_scan(csv_path: str, underlying: str, expiry: str):
    """
    High-level convenience wrapper used by scripts/run_bwb_scan.py.

    1. Load flattened chain CSV
    2. Slice by underlying + expiry + CALLs
    3. Generate BWB candidates
    4. Score + sort
    """
    chain_df = load_chain_csv(csv_path)
    calls_slice = select_ticker_and_expiry(
        chain_df,
        underlying=underlying,
        expiry=expiry,
        put_call="CALL",
    )

    bwb_candidates = generate_bwb_candidates(calls_slice)
    scored = score_broken_wing_butterflies(bwb_candidates)
    ranked = sort_by_score(scored)
    return ranked

