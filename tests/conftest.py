"""Build the chart outputs once if they are not already present."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="session", autouse=True)
def build_outputs():
    from fig1_us_treasury_yields import plot_yields, tidy_yields, write_tidy_csv
    from fig2_ai_issuance_shares import load_shares, plot_shares

    df = tidy_yields()
    write_tidy_csv(df)
    plot_yields(df)
    plot_shares(load_shares())
