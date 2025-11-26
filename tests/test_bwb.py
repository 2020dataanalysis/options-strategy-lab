# tests/test_bwb.py
import pandas as pd
from options_strategy_lab.scoring import (
    payoff_bwb_per_share,
    max_profit_and_loss,
    apply_basic_filters,
)


def test_payoff_known_example():
    """
    Simple sanity check of payoff shape for a toy BWB:
    K1=95, K2=100, K3=110, credit=2.00
    """
    k1, k2, k3, credit = 95.0, 100.0, 110.0, 2.0

    # Below K1: only entry credit
    assert payoff_bwb_per_share(90, k1, k2, k3) + credit == 2.0

    # Very far above K3: worst loss region
    _, max_loss = max_profit_and_loss(k1, k2, k3, credit)
    assert max_loss > 0


def test_filters_behave_as_expected():
    df = pd.DataFrame(
        [
            {"dte": 5, "credit": 0.60, "short_delta": 0.25},  # should pass
            {"dte": 0, "credit": 0.60, "short_delta": 0.25},  # bad DTE
            {"dte": 5, "credit": 0.10, "short_delta": 0.25},  # bad credit
            {"dte": 5, "credit": 0.60, "short_delta": 0.40},  # bad delta
        ]
    )

    filtered = apply_basic_filters(df)
    assert len(filtered) == 1
