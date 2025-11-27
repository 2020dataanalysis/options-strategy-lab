from options_strategy_lab.filters import filter_bwb_candidates

# from src.filters import filter_bwb_candidates



def test_min_credit_filter():
    # build a small fake DataFrame / list of structures
    candidates = [...]
    filtered = filter_bwb_candidates(candidates, min_credit=0.50)
    assert all(c.credit >= 0.50 for c in filtered)
