from src.broken_wing_butterfly import BrokenWingButterfly

def test_bwb_payoff_simple():
    # use a tiny, hand-checkable example
    bwb = BrokenWingButterfly(
        k1=95, k2=100, k3=110,
        credit=1.50,  # whatever your object expects
    )
    # spot at expiry where you know the payoff
    payoff = bwb.payoff_at_expiry(underlying_price=100)
    assert payoff == pytest.approx(expected_value)
