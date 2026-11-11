"""Shared paths, downloads, chart style, and byte-stable PNG/SVG saving."""
from __future__ import annotations

import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUTPUT = ROOT / "output"
INPUT = ROOT / "input"

# ellyokinyo.com article figures are 1600 px wide.
WEBSITE_WIDTH_PX = 1600
WEBSITE_HEIGHT_PX = 950
DPI = 100
FIGSIZE = (WEBSITE_WIDTH_PX / DPI, WEBSITE_HEIGHT_PX / DPI)  # 16 x 9.5 in
CAPTION = "Source: author's calculations"
SVG_HASHSALT = "ai-long-bonds-2026"

USER_AGENT = "Mozilla/5.0 (compatible; ai-long-bonds-2026; research)"

TREASURY_YEARS = (2024, 2025, 2026)
TREASURY_START = "2024-01-02"
HIGH_30_YEAR_DATE = "2026-10-07"

BIS140_PDF = (
    "https://www.bis.org/publications/bulletin-140-building-ai-credit-structures-and-spillovers.pdf"
)
BIS140_SHARES = INPUT / "bis140_long_issuance_shares.csv"


def treasury_csv_url(year: int) -> str:
    return (
        "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/"
        f"daily-treasury-rates.csv/{year}/all?type=daily_treasury_yield_curve"
        f"&field_tdr_date_value={year}&page&_format=csv"
    )


def download(url: str, name: str) -> Path:
    """Download url to data/name unless it is already there."""
    DATA.mkdir(exist_ok=True)
    path = DATA / name
    if not path.exists():
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=120) as r, open(path, "wb") as f:
                f.write(r.read())
        except Exception as exc:  # noqa: BLE001 - surface a stop-rule message
            if path.exists():
                path.unlink()
            raise RuntimeError(f"Stop: could not download {url}: {exc}") from exc
    return path


def style():
    import matplotlib
    matplotlib.use("Agg")
    matplotlib.rcParams["svg.hashsalt"] = SVG_HASHSALT
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "font.size": 18,
        "axes.titlesize": 26,
        "axes.labelsize": 18,
        "xtick.labelsize": 16,
        "ytick.labelsize": 16,
        "legend.fontsize": 16,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "svg.hashsalt": SVG_HASHSALT,
    })
    return plt


def add_caption(fig, text: str = CAPTION) -> None:
    fig.text(0.01, 0.015, text, fontsize=14, color="#555555", ha="left", va="bottom")


def _set_svg_pixel_size(path: Path, width: int, height: int) -> None:
    """Point-size SVG from matplotlib, retargeted to website width in pixels."""
    text = path.read_text(encoding="utf-8")
    pattern = r'(<svg[^>]* width=")[^"]+(" height=")[^"]+"'
    repl = rf'\g<1>{width}px\g<2>{height}px"'
    text, n = re.subn(pattern, repl, text, count=1)
    if n != 1:
        raise RuntimeError(f"could not set SVG pixel size on {path}")
    path.write_text(text, encoding="utf-8")


def save_chart(fig, stem: Path) -> None:
    """Write PNG and SVG at website width, with stable SVG metadata and hashsalt."""
    stem.parent.mkdir(exist_ok=True)
    png = stem.with_suffix(".png")
    svg = stem.with_suffix(".svg")
    fig.savefig(png, dpi=DPI, metadata={"Software": None})
    fig.savefig(svg, metadata={"Date": None})
    _set_svg_pixel_size(svg, WEBSITE_WIDTH_PX, WEBSITE_HEIGHT_PX)
