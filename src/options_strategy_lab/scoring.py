# src/options_strategy_lab/scoring.py
import pandas as pd


def apply_basic_filters(
    bwb_df: pd.DataFrame,
    min_dte: int = 1,
    max_dte: int = 10,
    min_credit: float = 0.50,
    min_short_delta: float = 0.20,
    max_short_delta: float = 0.35,
) -> pd.DataFrame:
    """
    Apply assignment-style pre-filters to the candidate BWBs.
    """
    mask = (
        (bwb_df["dte"].between(min_dte, max_dte))
        & (bwb_df["credit"] >= min_credit)
        & (bwb_df["short_delta"].between(min_short_delta, max_short_delta))
    )
    return bwb_df.loc[mask].copy()


def payoff_bwb_per_share(s: float, k1: float, k2: float, k3: float) -> float:
    """
    Terminal payoff of a BWB (per share) at expiration price s,
    ignoring entry credit.
    Strategy: +1C(K1), -2C(K2), +1C(K3).
    """
    def call_payoff(k: float) -> float:
        return max(s - k, 0.0)

    return call_payoff(k1) - 2 * call_payoff(k2) + call_payoff(k3)


def max_profit_and_loss(
    k1: float,
    k2: float,
    k3: float,
    credit: float,
) -> tuple[float, float]:
    """
    Compute max profit and max loss (per share) of the BWB,
    using simple piecewise evaluation at key price points.

    PnL(s) = payoff_bwb_per_share(s) + credit
    """
    # Evaluate PnL at key breakpoints:
    #  - below K1, at K1, K2, K3, and above K3.
    candidates = [k1 - 1e-6, k1, k2, k3, k3 + 10_000]  # large above-K3
    pnls = [payoff_bwb_per_share(s, k1, k2, k3) + credit for s in candidates]

    max_profit = max(pnls)
    max_loss = -min(pnls)  # positive number

    return max_profit, max_loss


def add_bwb_metrics_and_score(bwb_df: pd.DataFrame) -> pd.DataFrame:
    """
    For each BWB candidate, compute:
        - max_profit
        - max_loss
        - score = max_profit / max_loss  (simple risk/reward metric)
    Returns a sorted DataFrame (descending by score).
    """
    metrics = bwb_df.copy()

    profits = []
    losses = []
    scores = []

    for row in metrics.itertuples(index=False):
        max_profit, max_loss = max_profit_and_loss(
            row.k1, row.k2, row.k3, row.credit
        )
        profits.append(max_profit)
        losses.append(max_loss)
        scores.append(max_profit / max_loss if max_loss > 0 else float("nan"))

    metrics["max_profit"] = profits
    metrics["max_loss"] = losses
    metrics["score"] = scores

    # Sort best → worst
    metrics = metrics.sort_values(by="score", ascending=False).reset_index(drop=True)
    return metrics
