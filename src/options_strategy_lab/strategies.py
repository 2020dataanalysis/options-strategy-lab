# src/options_strategy_lab/strategies.py
from dataclasses import dataclass
import itertools
import pandas as pd


@dataclass
class BrokenWingButterfly:
    """
    Representation of a call BWB:

    Long 1 @ K1
    Short 2 @ K2
    Long 1 @ K3, where K2 - K1 != K3 - K2 (asymmetric wings)
    """
    underlying: str
    expiry: str
    k1: float
    k2: float
    k3: float
    credit: float          # entry credit (per share)
    max_profit: float      # per share
    max_loss: float        # per share
    dte: int               # days to expiration
    short_delta: float     # |delta| of short leg (for filters)


def generate_bwb_candidates(calls_df: pd.DataFrame) -> pd.DataFrame:
    """
    Given a DataFrame of CALL options for one expiry,
    enumerate Broken Wing Butterflies.

    calls_df is expected to contain one row per strike,
    with 'strike', 'mid', 'delta', 'expiry', 'underlying', 'days_to_expiration'.
    """
    rows_by_strike = {row.strike: row for row in calls_df.itertuples(index=False)}

    bwb_rows = []

    strikes = sorted(rows_by_strike.keys())
    # Triples of strikes with K1 < K2 < K3
    for k1, k2, k3 in itertools.combinations(strikes, 3):
        # enforce broken-wing asymmetry
        if (k2 - k1) == (k3 - k2):
            continue

        c1 = rows_by_strike[k1]
        c2 = rows_by_strike[k2]
        c3 = rows_by_strike[k3]

        credit = 2 * c2.mid - c1.mid - c3.mid  # net credit, per share

        # max profit / loss are computed in scoring.py;
        # here we just collect structure + simple fields
        bwb_rows.append(
            {
                "underlying": c1.underlying,
                "expiry": c1.expiry,
                "k1": k1,
                "k2": k2,
                "k3": k3,
                "credit": credit,
                "dte": int(c1.days_to_expiration),
                "short_delta": float(abs(c2.delta)),
            }
        )

    return pd.DataFrame(bwb_rows)
