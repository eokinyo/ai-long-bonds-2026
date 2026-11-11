"""Checks on the typed BIS Bulletin 140 p. 6 values and Chart 2 outputs."""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import BIS140_PDF, BIS140_SHARES, CAPTION, OUTPUT, WEBSITE_HEIGHT_PX, WEBSITE_WIDTH_PX  # noqa: E402
from fig2_ai_issuance_shares import bar_label, load_shares  # noqa: E402

EXPECTED = {
    ("corporate", 2024): (3.0, "yes"),
    ("corporate", 2026): (24.0, "yes"),
    ("treasury", 2024): (1.5, "yes"),
    ("treasury", 2026): (13.0, "no"),
}


def test_source_url_is_in_the_csv_comment():
    text = BIS140_SHARES.read_text(encoding="utf-8")
    assert text.splitlines()[0].startswith("#")
    assert BIS140_PDF in text
    assert "p. 6" in text


def test_four_typed_values():
    df = load_shares()
    assert len(df) == 4
    for (market, year), (share, approx) in EXPECTED.items():
        row = df[(df["market"] == market) & (df["year"] == year)].iloc[0]
        assert float(row["share_percent"]) == share
        assert row["approximately"] == approx


def test_bar_labels_use_about_where_the_bulletin_does():
    df = load_shares()
    labels = {(r["market"], int(r["year"])): bar_label(r) for _, r in df.iterrows()}
    assert labels[("corporate", 2024)] == "about 3%"
    assert labels[("corporate", 2026)] == "about 24%"
    assert labels[("treasury", 2024)] == "about 1.5%"
    assert labels[("treasury", 2026)] == "13%"


def test_chart2_outputs_exist_at_website_width():
    png = OUTPUT / "fig2_ai_issuance_shares.png"
    svg = OUTPUT / "fig2_ai_issuance_shares.svg"
    assert png.exists() and svg.exists()
    w, h = struct.unpack(">II", png.read_bytes()[16:24])
    assert (w, h) == (WEBSITE_WIDTH_PX, WEBSITE_HEIGHT_PX)
    svg_text = svg.read_text(encoding="utf-8")
    assert f'width="{WEBSITE_WIDTH_PX}px"' in svg_text
    assert f'height="{WEBSITE_HEIGHT_PX}px"' in svg_text
    assert CAPTION in svg_text
