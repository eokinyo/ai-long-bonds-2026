"""Checks on the Treasury yield series and Chart 1 outputs."""
import struct
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import HIGH_30_YEAR_DATE, OUTPUT, WEBSITE_HEIGHT_PX, WEBSITE_WIDTH_PX, treasury_csv_url  # noqa: E402
from fig1_us_treasury_yields import tidy_yields, write_tidy_csv  # noqa: E402

# Values from the #101 data plan, checked against the official Treasury CSV.
PLAN = {
    "2026-01-02": {"2_year": 3.47, "10_year": 4.19, "30_year": 4.86},
    "2026-10-07": {"30_year": 5.67},
    "2026-11-10": {"2_year": 4.73, "10_year": 4.98, "30_year": 5.35},
}


def png_size(path: Path) -> tuple[int, int]:
    w, h = struct.unpack(">II", path.read_bytes()[16:24])
    return w, h


def test_treasury_url_pattern():
    url = treasury_csv_url(2026)
    assert "daily-treasury-rates.csv/2026/all" in url
    assert "type=daily_treasury_yield_curve" in url
    assert "field_tdr_date_value=2026" in url
    assert url.startswith("https://home.treasury.gov/")
    assert treasury_csv_url(2024) != url


def test_series_starts_2_jan_2024():
    df = tidy_yields()
    assert df["date"].min() == pd.Timestamp("2024-01-02")
    assert (df["date"].diff().dropna() > pd.Timedelta(0)).all()


def test_plan_dates_match_treasury_csv():
    df = tidy_yields()
    for day, expect in PLAN.items():
        row = df[df["date"] == pd.Timestamp(day)]
        assert not row.empty, f"missing {day}"
        for col, want in expect.items():
            assert float(row.iloc[0][col]) == want, (day, col, row.iloc[0][col], want)


def test_7_oct_2026_is_in_the_series():
    df = tidy_yields()
    row = df[df["date"] == pd.Timestamp(HIGH_30_YEAR_DATE)]
    assert not row.empty
    assert float(row.iloc[0]["30_year"]) == 5.67


def test_latest_row_matches_raw_2026_csv():
    df = tidy_yields()
    last = df.iloc[-1]
    raw_path = Path(__file__).resolve().parents[1] / "data" / "daily_treasury_yield_curve_2026.csv"
    raw = pd.read_csv(raw_path)
    raw.columns = [str(c).strip().strip('"') for c in raw.columns]
    raw["date"] = pd.to_datetime(raw["Date"], format="%m/%d/%Y")
    match = raw[raw["date"] == last["date"]]
    assert not match.empty
    src = match.iloc[0]
    assert float(last["2_year"]) == float(src["2 Yr"])
    assert float(last["10_year"]) == float(src["10 Yr"])
    assert float(last["30_year"]) == float(src["30 Yr"])


def test_tidy_csv_and_chart_outputs_exist():
    df = tidy_yields()
    write_tidy_csv(df)
    csv_path = OUTPUT / "fig1_us_treasury_yields.csv"
    tidy = pd.read_csv(csv_path)
    assert list(tidy.columns) == ["date", "2_year", "10_year", "30_year"]
    assert len(tidy) == len(df)
    png = OUTPUT / "fig1_us_treasury_yields.png"
    svg = OUTPUT / "fig1_us_treasury_yields.svg"
    assert png.exists() and svg.exists()
    assert png_size(png) == (WEBSITE_WIDTH_PX, WEBSITE_HEIGHT_PX)
    svg_text = svg.read_text(encoding="utf-8")
    assert f'width="{WEBSITE_WIDTH_PX}px"' in svg_text
    assert f'height="{WEBSITE_HEIGHT_PX}px"' in svg_text
    assert "dc:date" not in svg_text.lower()
