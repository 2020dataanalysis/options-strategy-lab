# src/options_strategy_lab/scoring.py

from __future__ import annotations
import pandas as pd


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
