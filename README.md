# Note Systems backtest

A backtest of the default [Note Systems](https://note.systems) autocallable note on a decade of real stock prices, written for the article *Structured Notes, But on the Blockchain* by [@0xbuchi](https://x.com/0xbuchi).

The Note Systems docs explain how a note pays. This repo measures how often each ending actually happens, what the coupon would need to be for each stock, and how the economics split between the two sides (COUPON and SHIELD).

Every number in the article can be reproduced from this code.

## What it does

- **Universe:** the eight Stock Tokens with feeds on Note Systems testnet: NVDA, TSLA, AAPL, MSFT, AMZN, META, COIN, HOOD.
- **Prices:** daily closes adjusted for splits and dividends (Yahoo Finance), which approximates the ERC-8056 multiplier already folded into Stock Token feeds.
- **Notes:** one new note struck at every Friday close from January 2015 to September 2025 (COIN from April 2021, HOOD from August 2021). 3,683 notes in total.
- **Terms (protocol defaults):** 26 fortnightly observations, autocall at 100% of S0 on intermediate observations, coupon paid when the close is at or above 65% of S0, no coupon memory, knock-in judged only at the final observation (physical settlement at S0). Each observation uses the last close on or before the scheduled date.
- **Economics:** coupons net of the 15% protocol fee; SHIELD pays the 0.25% notional fee at strike. The docs' illustrative coupon is 150 bps per observation.

## Headline results

| | |
|---|---|
| Notes | 3,683 |
| Autocalled at the first check (2 weeks) | 58.6% |
| Ended early at any point | 95.9% |
| Ran full term, repaid in cash | 2.0% |
| Knocked in | 2.1% (average loss 60.1%, worst 86.4%) |
| Knock-ins from notes struck Jul 2021 to May 2022 | 72 of 76 |
| SHIELD vs holding the stock, at 150 bps | -3.8% on average |

Break-even gross coupon per observation (COUPON side, average profit of zero):

| AAPL | MSFT | TSLA | AMZN | NVDA | META | COIN | HOOD |
|---|---|---|---|---|---|---|---|
| 0 bps | 0 bps | 20 | 28 | 32 | 52 | 220 | 244 |

AAPL and MSFT had no knock-ins in the sample, so their break-even is zero; that reflects the decade, not a claim that those notes are riskless.

Other results in `backtest/deep.py`: barrier sensitivity (50% to 80%), template length (8 to 52 weeks), per-stock SHIELD outcomes. Rolling COUPON vs buy-and-hold is in `backtest/roll.py`.

## Run it

```bash
cd backtest
python3 fetch_prices.py   # downloads prices.json, end date pinned to 23 Sep 2026
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
