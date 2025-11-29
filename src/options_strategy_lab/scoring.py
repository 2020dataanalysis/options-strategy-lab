# src/options_strategy_lab/scoring.py

from __future__ import annotations   # 👈 must be first (after comments/docstring)
from typing import Optional          # 👈 now safely below it
import pandas as pd
from .filters import filter_bwb_candidates


def _bwb_pnl_points(k1: float, k2: float, k3: float, credit: float):
    """
    Compute P&L at key points for a call BWB:
      Long 1 @ K1, Short 2 @ K2, Long 1 @ K3, opened for net credit.

    We evaluate P&L at:
      - S <= K1  → PnL_low
      - S  = K2  → PnL_k2
      - S >= K3  → PnL_high

    Payoff summary (per share):

      S <= K1:
        all OTM → payoff = 0 → PnL = credit

      K1 < S <= K2:
        long K1 ITM only → payoff = (S - K1)
        PnL = (S - K1) + credit
        at S = K2 → PnL_k2 = (K2 - K1) + credit

      K2 < S <= K3:
        long K1 ITM, short 2x K2 ITM
        payoff = (S - K1) - 2 * (S - K2) = -S + 2K2 - K1
        (we don't need an interior point explicitly for extrema in this toy model)

      S >= K3:
        all ITM
        payoff = (S - K1) - 2*(S - K2) + (S - K3)
               = -K1 + 2K2 - K3 (constant)
        PnL_high = -K1 + 2*K2 - K3 + credit
    """
    pnl_low = credit
    pnl_k2 = (k2 - k1) + credit
    pnl_high = (-k1 + 2 * k2 - k3) + credit

    pnl_candidates = [pnl_low, pnl_k2, pnl_high]

    max_profit = max(max(pnl_candidates), 0.0)
    max_loss = max(0.0, -min(pnl_candidates))

    return pnl_low, pnl_k2, pnl_high, max_profit, max_loss


def score_broken_wing_butterflies(bwb_df: pd.DataFrame) -> pd.DataFrame:
    """
    Given a DataFrame of BWB structures (from generate_bwb_candidates),
    add max_profit, max_loss, and a simple score = max_profit / max_loss.
    """

    df = bwb_df.copy()

    # Ensure required columns exist
    required_cols = {"k1", "k2", "k3", "credit"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns in BWB DataFrame: {missing}")

    pnl_low_list = []
    pnl_k2_list = []
    pnl_high_list = []
    max_profit_list = []
    max_loss_list = []
    score_list = []

    for row in df.itertuples(index=False):
        k1 = float(row.k1)
        k2 = float(row.k2)
        k3 = float(row.k3)
        credit = float(row.credit)

        pnl_low, pnl_k2, pnl_high, max_profit, max_loss = _bwb_pnl_points(
            k1, k2, k3, credit
        )

        pnl_low_list.append(pnl_low)
        pnl_k2_list.append(pnl_k2)
        pnl_high_list.append(pnl_high)
        max_profit_list.append(max_profit)
        max_loss_list.append(max_loss)

        if max_loss > 0:
            score = max_profit / max_loss
        else:
            # If there is no downside (in this toy calc), treat as very high score
            score = float("inf") if max_profit > 0 else 0.0

        score_list.append(score)

    df["pnl_low"] = pnl_low_list
    df["pnl_at_k2"] = pnl_k2_list
    df["pnl_high"] = pnl_high_list
    df["max_profit"] = max_profit_list
    df["max_loss"] = max_loss_list
    df["score"] = score_list

    return df


def sort_by_score(bwb_scored_df: pd.DataFrame, top_n: int | None = None) -> pd.DataFrame:
    """
    Sort BWB rows by descending score. Optionally return only top_n rows.
    """
    sorted_df = bwb_scored_df.sort_values("score", ascending=False)
    if top_n is not None:
        sorted_df = sorted_df.head(top_n)
    return sorted_df






def max_profit_and_loss(
    k1: float,
    k2: float,
    k3: float,
    credit: float,
) -> tuple[float, float]:
    """
    Compute the *maximum profit* and *maximum loss* of a CALL Broken-Wing Butterfly
    (BWB) per share, assuming the classic 1:-2:1 structure:

        +1 call at K1  (lower strike)
        -2 calls at K2 (body / short strike)
        +1 call at K3  (upper strike)
        opened for a net CREDIT.

    We use the closed-form payoffs at the three important regions:

      1. S_T <= K1       → "low" region
      2. S_T =  K2       → body peak
      3. S_T >= K3       → "high" region

    For any CALL BWB of this form:

        a = K2 - K1  (width of the lower wing)
        b = K3 - K2  (width of the upper wing)

      - Low-region PnL (S_T <= K1):
            pnl_low = credit

      - At-the-body PnL (S_T = K2):
            pnl_at_k2 = a + credit

      - High-region PnL (S_T >= K3):
            raw structure payoff = a - b
            pnl_high = (a - b) + credit

    The function returns:

        max_profit : max(pnl_low, pnl_at_k2, pnl_high)
        max_loss   : largest *downside* as a positive number
                     = max(0, -min(pnl_low, pnl_at_k2, pnl_high))

    This matches the columns you already see in your BWB table:
        - max_profit
        - max_loss
        - and score = max_profit / max_loss
    """

    # Wing widths
    a = k2 - k1  # lower wing: K2 - K1
    b = k3 - k2  # upper wing: K3 - K2

    # Region payoffs (per share), including the opening credit
    pnl_low = credit                    # S_T <= K1
    pnl_at_k2 = a + credit              # S_T = K2
    pnl_high = (a - b) + credit         # S_T >= K3

    # Max profit is simply the best of the three regions
    max_profit = max(pnl_low, pnl_at_k2, pnl_high)

    # Max loss is the worst negative PnL, returned as a positive magnitude
    min_pnl = min(pnl_low, pnl_at_k2, pnl_high)
    max_loss = max(0.0, -min_pnl)

    return max_profit, max_loss




def payoff_bwb_per_share(
    underlying_price: float,
    k1: float,
    k2: float,
    k3: float,
) -> float:
    """
    Vanilla expiration payoff (per share) for a 1:-2:1 call broken-wing butterfly,
    **excluding** entry credit.

    Position:
      +1 call at K1
      -2 calls at K2
      +1 call at K3

    Payoff at expiry (ignoring credit):
        max(S - K1, 0)
      - 2 * max(S - K2, 0)
      +     max(S - K3, 0)

    The tests add the entry credit separately when they want P&L.
    """
    s = underlying_price

    leg_k1 = max(s - k1, 0.0)
    leg_k2 = -2.0 * max(s - k2, 0.0)
    leg_k3 = max(s - k3, 0.0)

    return leg_k1 + leg_k2 + leg_k3




def apply_basic_filters(
    bwb_candidates,
    min_credit: float = 0.50,
    min_dte: int = 1,
    max_dte: Optional[int] = None,
    min_short_delta: float = 0.10,
    max_short_delta: float = 0.30,
):
    """
    Basic "sane default" filters for BWB candidates.

    Used by tests and by the simple end-to-end scan.

    Defaults chosen so that:
      - credit >= 0.50      (ignore tiny credits)
      - dte >= 1            (exclude same-day / expired)
      - 0.10 <= delta <= 0.30 for the short strike

    Parameters can be overridden by the caller, but the tests rely
    on these defaults.
    """
    return filter_bwb_candidates(
        bwb_candidates,
        min_credit=min_credit,
        min_dte=min_dte,
        max_dte=max_dte,
        min_short_delta=min_short_delta,
        max_short_delta=max_short_delta,
    )
