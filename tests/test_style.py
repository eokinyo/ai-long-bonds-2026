"""Caption, hyphenation, and byte-identical reruns."""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import CAPTION, OUTPUT  # noqa: E402
from fig1_us_treasury_yields import plot_yields, tidy_yields  # noqa: E402
from fig2_ai_issuance_shares import load_shares, plot_shares  # noqa: E402

FORBIDDEN = ("30-year", "10-year", "2-year", "long-dated", "long-term")


def test_caption_text():
    assert CAPTION == "Source: author's calculations"


def test_output_svgs_have_caption_and_no_hyphenated_labels():
    for name in ("fig1_us_treasury_yields.svg", "fig2_ai_issuance_shares.svg"):
        text = (OUTPUT / name).read_text(encoding="utf-8")
        assert CAPTION in text
        lower = text.lower()
        for phrase in FORBIDDEN:
            assert phrase not in lower, (name, phrase)
        # No dataset codes or chart credits.
        assert "daily_treasury_yield_curve" not in text
        assert "Luku" not in text
        assert "eokinyo" not in text.lower()


def test_source_labels_avoid_hyphenation():
    from fig1_us_treasury_yields import LABELS
    from fig2_ai_issuance_shares import MARKET_LABELS

    blob = " ".join([*LABELS.values(), *MARKET_LABELS.values(), "AI firms' share of long dated bond issuance"])
    for phrase in FORBIDDEN:
        assert phrase not in blob
    assert "30 year" in LABELS["30_year"]
    assert "long dated" in "AI firms' share of long dated bond issuance"
    assert "10 years or more" in MARKET_LABELS["corporate"]


def test_plots_are_byte_identical_on_a_second_run(tmp_path):
    df = tidy_yields()
    shares = load_shares()
    d1, d2 = tmp_path / "a", tmp_path / "b"
    d1.mkdir(); d2.mkdir()
    plot_yields(df, output_dir=d1)
    plot_shares(shares, output_dir=d1)
    plot_yields(df, output_dir=d2)
    plot_shares(shares, output_dir=d2)
    for name in (
        "fig1_us_treasury_yields.png",
        "fig1_us_treasury_yields.svg",
        "fig2_ai_issuance_shares.png",
        "fig2_ai_issuance_shares.svg",
    ):
        b1 = (d1 / name).read_bytes()
        b2 = (d2 / name).read_bytes()
        assert b1 == b2, name
        assert len(b1) > 0
