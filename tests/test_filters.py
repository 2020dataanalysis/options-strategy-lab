# tests/test_filters.py

import pandas as pd
from options_strategy_lab.filters import filter_bwb_candidates

def test_min_credit_filter():
    # build a small fake DataFrame of BWB candidates
    df = pd.DataFrame(
        [
            {"underlying": "AAPL", "credit": 0.30, "dte": 3, "short_delta": 0.5},
            {"underlying": "AAPL", "credit": 0.60, "dte": 3, "short_delta": 0.5},
            {"underlying": "AAPL", "credit": 1.00, "dte": 3, "short_delta": 0.5},
        ]
    )

    filtered = filter_bwb_candidates(df, min_credit=0.50)

    # Only the rows with credit >= 0.50 should remain
    assert len(filtered) == 2
    assert filtered["credit"].min() >= 0.50
