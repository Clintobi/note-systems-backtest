# Note Systems backtest

A backtest of the default [Note Systems](https://note.systems) autocallable note on a decade of real stock prices, written for the article *Structured Notes, But on the Blockchain* by [@0xbuchi](https://x.com/0xbuchi).

The Note Systems docs explain how a note pays. This repo measures how often each ending actually happens, what the coupon would need to be for each stock, and how the economics split between the two sides (COUPON and SHIELD).

Every number in the article can be reproduced from this code.

## What it does

- **Universe:** the eight Stock Tokens with feeds on Note Systems testnet: NVDA, TSLA, AAPL, MSFT, AMZN, META, COIN, HOOD.
- **Prices:** daily closes adjusted for splits and dividends (Yahoo Finance), which approximates the ERC-8056 multiplier already folded into Stock Token feeds.
- **Notes:** one new note struck at every Friday close from January 2015 to September 2025 (COIN from April 2021, HOOD from August 2021). 3,683 notes in total.
- **Terms:** the per-underlying standing templates published in the docs (concepts/autocallable-notes, "Standing templates", testnet deployment 11, 29 Sep 2026): twelve weekly coupon observations five trading days apart, knock-in judged only at the final observation (physical settlement at S0), no coupon memory.

| | AAPL | MSFT | AMZN | NVDA | META | TSLA | HOOD | COIN |
|---|---|---|---|---|---|---|---|---|
| Autocall | 105% | 105% | 105% | 105% | 105% | 110% | 110% | 110% |
| Barrier | 88% | 85% | 85% | 80% | 80% | 75% | 60% | 60% |
| Coupon band, bps/week (floor, reference, cap) | 10 / 30 / 60 | 10 / 45 / 80 | 25 / 50 / 95 | 15 / 45 / 140 | 30 / 55 / 100 | 30 / 55 / 150 | 25 / 75 / 130 | 40 / 75 / 160 |

- **Economics:** coupon held at each template's reference rate; 25% coupon fee; 0.75% notional fee paid by SHIELD at strike.

## Headline results (standing templates)

| | |
|---|---|
| Notes | 3,683 |
| Average length | 6.25 weeks (median 5); the docs expect six to eight |
| Autocalled at the first check | 13.6% |
| Ended early at any point | 73.1% |
| Ran all 12 weeks, repaid in cash | 21.6% |
| Knocked in | 5.3% (194 notes; average loss 31.7%, worst 73.4%) |
| Knock-ins from notes struck Sep 2021 to Dec 2022 | 102 of 194 |
| Ran to term below S0 but above the barrier (SHIELD paid, protection never paid out) | 15.7% |
| SHIELD vs holding the stock | -2.0% per note on average (every stock negative) |

Break-even gross coupon per weekly observation (COUPON side, average profit of zero) vs the template reference:

| | AAPL | MSFT | AMZN | NVDA | META | TSLA | HOOD | COIN |
|---|---|---|---|---|---|---|---|---|
| Break-even, 2015-2025 | 31 | 6 | 28 | 46 | 36 | 44 | 94 | 87 |
| Template reference | 30 | 45 | 50 | 45 | 55 | 55 | 75 | 75 |
| Template cap | 60 | 80 | 95 | 140 | 100 | 150 | 130 | 160 |

The interactive page and `docs/notes.json` use these templates (`backtest/gen_site_data.py`).

### Earlier templates

`backtest.py`, `deep.py`, `roll.py` and the PNGs in `charts/` model the launch-era docs example (26 fortnightly observations, 65% barrier, 100% autocall, 150 bps, 15% and 0.25% fees). Those results are kept for reference only.

## Run it

```bash
cd backtest
python3 fetch_prices.py   # downloads prices.json, end date pinned to 23 Sep 2026
python3 gen_site_data.py  # current template: docs/notes.json + summary
python3 backtest.py       # per-stock table + results.json
python3 roll.py           # rolling COUPON vs holding, roll.json
python3 deep.py           # barrier / length sensitivity, deep.json
```

The backtest scripts use only the Python standard library. The charts in `charts/` are rendered by `charts/make_charts.py`, which needs `matplotlib` and `numpy`.

## Caveats

- Notes overlap and are not independent.
- 2015 to 2025 was mostly a bull market; past knock-in rates are not a forecast.
- Break-even coupons ignore the yield idle USDG could earn elsewhere, so a fair coupon in practice is higher.
- The docs' 52-week template is modelled; live series may use shorter schedules (the length sensitivity covers 8, 16 and 26 weeks).
- This is an independent analysis, not affiliated with Note Systems. Nothing here is financial advice.

## License

MIT

## Interactive simulator

`docs/` is a static page (GitHub Pages) that lets you pick any stock and any start week and see how that note ended. Regenerate its data with `python3 backtest/gen_site_data.py` (run from `backtest/`).
