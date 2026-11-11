"""Figure 1: US Treasury yields since 2024 (2 year, 10 year and 30 year)."""
from __future__ import annotations

import pandas as pd

from common import (
    CAPTION,
    DATA,
    FIGSIZE,
    HIGH_30_YEAR_DATE,
    OUTPUT,
    TREASURY_START,
    TREASURY_YEARS,
    add_caption,
    download,
    save_chart,
    style,
    treasury_csv_url,
)

MATURITIES = {
    "2 Yr": "2_year",
    "10 Yr": "10_year",
    "30 Yr": "30_year",
}
LABELS = {
    "2_year": "2 year",
    "10_year": "10 year",
    "30_year": "30 year",
}
COLORS = {
    "2_year": "#5b8def",
    "10_year": "#1f4e9c",
    "30_year": "#c0392b",
}
STEM = OUTPUT / "fig1_us_treasury_yields"


def download_treasury_csvs() -> list[tuple[int, object]]:
    paths = []
    for year in TREASURY_YEARS:
        path = download(treasury_csv_url(year), f"daily_treasury_yield_curve_{year}.csv")
        text = path.read_text(encoding="utf-8", errors="replace")
        if "Date" not in text.splitlines()[0]:
            raise RuntimeError(
                f"Stop: Treasury file for {year} is not a yield CSV. "
                f"First line: {text.splitlines()[0][:120]!r}"
            )
        paths.append((year, path))
    return paths


def tidy_yields(paths: list[tuple[int, object]] | None = None) -> pd.DataFrame:
    if paths is None:
        paths = download_treasury_csvs()
    frames = []
    for year, path in paths:
        raw = pd.read_csv(path)
        raw.columns = [str(c).strip().strip('"') for c in raw.columns]
        missing = [c for c in ("Date", *MATURITIES) if c not in raw.columns]
        if missing:
            raise RuntimeError(f"Stop: {path} is missing columns {missing}")
        part = raw[["Date", *MATURITIES]].copy()
        part["date"] = pd.to_datetime(part["Date"], format="%m/%d/%Y")
        for src, dest in MATURITIES.items():
            part[dest] = pd.to_numeric(part[src], errors="coerce")
        part["source_year"] = year
        frames.append(part[["date", *MATURITIES.values()]])
    df = pd.concat(frames, ignore_index=True)
    df = df.drop_duplicates(subset=["date"], keep="last")
    df = df[df["date"] >= pd.Timestamp(TREASURY_START)].sort_values("date")
    gap = df[list(MATURITIES.values())].isna().any()
    if gap.any():
        bad = gap[gap].index.tolist()
        raise RuntimeError(f"Stop: missing yields in {bad}")
    if df.empty:
        raise RuntimeError("Stop: no Treasury yields on or after 2 Jan 2024")
    return df.reset_index(drop=True)


def write_tidy_csv(df: pd.DataFrame, path=None) -> object:
    path = path or STEM.with_suffix(".csv")
    path.parent.mkdir(exist_ok=True)
    out = df.copy()
    out["date"] = out["date"].dt.strftime("%Y-%m-%d")
    out.to_csv(path, index=False, float_format="%.2f")
    return path


def plot_yields(df: pd.DataFrame, output_dir=None) -> object:
    from matplotlib import dates as mdates

    plt = style()
    output_dir = output_dir or OUTPUT
    stem = output_dir / STEM.name
    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=100)
    for col in MATURITIES.values():
        ax.plot(df["date"], df[col], color=COLORS[col], lw=2.8, label=LABELS[col], zorder=3)
        last = df.iloc[-1]
        ax.annotate(
            f"{LABELS[col]}  {last[col]:.2f}%",
            (last["date"], last[col]),
            xytext=(12, 0),
            textcoords="offset points",
            va="center",
            color=COLORS[col],
            fontsize=18,
            fontweight="bold",
        )

    high_day = pd.Timestamp(HIGH_30_YEAR_DATE)
    high_rows = df[df["date"] == high_day]
    if high_rows.empty:
        raise RuntimeError(f"Stop: {HIGH_30_YEAR_DATE} is missing from the Treasury series")
    high_val = float(high_rows.iloc[0]["30_year"])
    ax.scatter([high_day], [high_val], color=COLORS["30_year"], s=70, zorder=5, clip_on=False)
    ax.axvline(high_day, color="#bbbbbb", lw=1.0, ls="--", zorder=1)
    ax.annotate(
        f"30 year high\n7 Oct 2026, {high_val:.2f}%",
        (high_day, high_val),
        xytext=(-18, 22),
        textcoords="offset points",
        ha="right",
        va="bottom",
        color=COLORS["30_year"],
        fontsize=15,
        fontweight="bold",
        arrowprops=dict(arrowstyle="-", color=COLORS["30_year"], lw=1.0),
    )

    ax.set_title("US Treasury yields since 2024", loc="left", pad=16)
    ax.set_ylabel("Percent")
    ax.grid(axis="y", color="#dddddd", zorder=0)
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.set_xlim(pd.Timestamp("2024-01-01"), df["date"].max())
    ax.margins(x=0)
    fig.subplots_adjust(left=0.07, right=0.82, top=0.88, bottom=0.12)
    add_caption(fig, CAPTION)
    save_chart(fig, stem)
    plt.close(fig)
    return stem


def main() -> None:
    df = tidy_yields()
    csv_path = write_tidy_csv(df)
    plot_yields(df)
    last = df.iloc[-1]
    high = df.loc[df["date"] == pd.Timestamp(HIGH_30_YEAR_DATE)].iloc[0]
    print(f"Wrote {csv_path}")
    print(
        f"Latest {last['date'].date()}: "
        f"2 year {last['2_year']:.2f}, 10 year {last['10_year']:.2f}, "
        f"30 year {last['30_year']:.2f}"
    )
    print(f"30 year on 7 Oct 2026: {high['30_year']:.2f}")


if __name__ == "__main__":
    main()
