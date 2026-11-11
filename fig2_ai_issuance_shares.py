"""Figure 2: AI firms' share of long dated bond issuance, 2024 against 2026."""
from __future__ import annotations

import pandas as pd

from common import BIS140_SHARES, CAPTION, FIGSIZE, OUTPUT, add_caption, save_chart, style

STEM = OUTPUT / "fig2_ai_issuance_shares"

# Display labels (hyphenation off).
MARKET_LABELS = {
    "corporate": "Corporate issuance,\n10 years or more",
    "treasury": "Treasury issuance,\n10 years or more",
}
YEAR_COLORS = {2024: "#9aa3ad", 2026: "#1f4e9c"}
MARKET_ORDER = ["corporate", "treasury"]
YEAR_ORDER = [2024, 2026]


def load_shares(path=None) -> pd.DataFrame:
    path = path or BIS140_SHARES
    df = pd.read_csv(path, comment="#", skipinitialspace=True)
    df.columns = [c.strip() for c in df.columns]
    expected = {"market", "year", "share_percent", "approximately"}
    if set(df.columns) != expected:
        raise RuntimeError(f"Stop: unexpected columns in {path}: {list(df.columns)}")
    df["year"] = df["year"].astype(int)
    df["share_percent"] = pd.to_numeric(df["share_percent"])
    df["approximately"] = df["approximately"].str.strip().str.lower()
    if set(df["market"]) != {"corporate", "treasury"}:
        raise RuntimeError(f"Stop: unexpected markets in {path}")
    if set(df["year"]) != {2024, 2026}:
        raise RuntimeError(f"Stop: unexpected years in {path}")
    if len(df) != 4:
        raise RuntimeError(f"Stop: expected four share values, got {len(df)}")
    return df.sort_values(["market", "year"]).reset_index(drop=True)


def bar_label(row: pd.Series) -> str:
    value = row["share_percent"]
    number = f"{value:g}%"
    if row["approximately"] == "yes":
        return f"about {number}"
    return number


def plot_shares(df: pd.DataFrame, output_dir=None) -> object:
    plt = style()
    output_dir = output_dir or OUTPUT
    stem = output_dir / STEM.name
    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=100)

    x = list(range(len(MARKET_ORDER)))
    width = 0.34
    offsets = {2024: -width / 2, 2026: width / 2}

    for year in YEAR_ORDER:
        vals = []
        for market in MARKET_ORDER:
            row = df[(df["market"] == market) & (df["year"] == year)].iloc[0]
            vals.append(float(row["share_percent"]))
        xpos = [i + offsets[year] for i in x]
        bars = ax.bar(
            xpos,
            vals,
            width=width,
            color=YEAR_COLORS[year],
            label=str(year),
            zorder=3,
        )
        for bar, market, val in zip(bars, MARKET_ORDER, vals):
            row = df[(df["market"] == market) & (df["year"] == year)].iloc[0]
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                val + 0.7,
                bar_label(row),
                ha="center",
                va="bottom",
                fontsize=16,
                fontweight="bold",
                color=YEAR_COLORS[year],
            )

    ax.set_xticks(x)
    ax.set_xticklabels([MARKET_LABELS[m] for m in MARKET_ORDER])
    ax.set_ylabel("Percent")
    ax.set_ylim(0, 32)
    ax.set_title("AI firms' share of long dated bond issuance", loc="left", pad=16)
    ax.grid(axis="y", color="#dddddd", zorder=0)
    ax.legend(frameon=False, loc="upper left")
    ax.tick_params(axis="x", length=0)
    fig.subplots_adjust(left=0.08, right=0.97, top=0.88, bottom=0.16)
    add_caption(fig, CAPTION)
    save_chart(fig, stem)
    plt.close(fig)
    return stem


def main() -> None:
    df = load_shares()
    plot_shares(df)
    for _, row in df.iterrows():
        print(f"{row['market']} {int(row['year'])}: {bar_label(row)}")
    print(f"Wrote {STEM.with_suffix('.png')} and {STEM.with_suffix('.svg')}")


if __name__ == "__main__":
    main()
