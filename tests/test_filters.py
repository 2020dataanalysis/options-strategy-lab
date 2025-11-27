# tests/test_filters.py

import pandas as pd
from options_strategy_lab.filters import filter_bwb_candidates


def test_filter_bwb_candidates():
    """
    Basic sanity test for the BWB filter helper.

    We construct three fake BWB candidates with different credits:
      - 0.25 (too small)
      - 0.75
      - 1.10

    Then:
      - we call filter_bwb_candidates(..., min_credit=0.50)
      - we expect only the last two to survive
      - and we assert that all remaining credits are >= 0.50
    """

    candidates = [
        {"credit": 0.25, "dte": 5, "short_delta": 0.30},
        {"credit": 0.75, "dte": 5, "short_delta": 0.30},
        {"credit": 1.10, "dte": 5, "short_delta": 0.30},
    ]

    filtered = filter_bwb_candidates(candidates, min_credit=0.50)

    # Expect exactly 2 rows: 0.75 and 1.10
    assert len(filtered) == 2

    # And every surviving row must satisfy the filter condition
    assert (filtered["credit"] >= 0.50).all()
