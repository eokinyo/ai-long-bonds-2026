# AI long bonds 2026: charts

Code for the charts in the article "AI is now borrowing at the long end of the bond market".
Chart 1 is built from official US Treasury daily par yield CSVs. Chart 2 uses four values
typed from BIS Bulletin 140, page 6. No other figures are typed in by hand.

| Figure | Script | Output |
|---|---|---|
| 1. US Treasury yields since 2024: daily par yields, 2 year, 10 year and 30 year, 2 Jan 2024 to the latest date, with the 7 Oct 2026 30 year high marked | `fig1_us_treasury_yields.py` | `output/fig1_us_treasury_yields.png`, `.svg` and `.csv` |
| 2. AI firms' share of long dated bond issuance: grouped bars for 2024 against 2026 (share of corporate issuance and of gross Treasury issuance at 10 years or more) | `fig2_ai_issuance_shares.py` | `output/fig2_ai_issuance_shares.png` and `.svg` |

Both charts are 1600 px wide. The caption on each chart is "Source: author's calculations".
Labels use open compounds ("30 year", "long dated"), not hyphenated forms.

## Sources

| Source | File | Release date | Retrieved |
|---|---|---|---|
| US Department of the Treasury, Daily Treasury Par Yield Curve Rates, 2024, 2025 and 2026 | [2026 CSV](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/2026/all?type=daily_treasury_yield_curve&field_tdr_date_value=2026&page&_format=csv) (the same URL pattern with 2024 and 2025 in place of 2026) | Daily; latest observation in this run is stated by the script | 11 Nov 2026 |
| BIS Bulletin no 140, Drehmann and Eren, "Building AI on credit: structures and spillovers", p. 6 and Graph 3.C | [bulletin-140-building-ai-credit-structures-and-spillovers.pdf](https://www.bis.org/publications/bulletin-140-building-ai-credit-structures-and-spillovers.pdf) | 27 October 2026 | 11 Nov 2026 |

The four Chart 2 values are in `input/bis140_long_issuance_shares.csv`, with the source URL in a comment.
The Bulletin writes: in 2026, hyperscaler bonds with maturities of 10 years or more accounted for
about 24 percent of corporate issuance at those maturities and 13 percent of gross Treasury issuance,
up from about 3 percent and 1.5 percent, respectively, in 2024.

## How to run

From a clean clone, one command reproduces both PNGs, both SVGs and the tidy CSV:

```bash
./run.sh
```

That creates a virtual environment, installs the pinned packages in `requirements.txt`,
downloads the three Treasury CSVs into `data/` (unless they are already cached) and writes the
outputs to `output/`. Then:

```bash
.venv/bin/python -m pytest -q
```

Downloaded Treasury files are cached in `data/` and are not committed. Delete them to download again.
If the Treasury revises a year file at the same URL, Chart 1 may change.

## Licence

Code: MIT (see `LICENSE`). Data remain under the publishers' terms (US Treasury; BIS).
