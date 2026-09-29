# Note Systems backtest

A backtest of the default [Note Systems](https://note.systems) autocallable note on a decade of real stock prices, written for the article *Structured Notes, But on the Blockchain* by [@0xbuchi](https://x.com/0xbuchi).

The Note Systems docs explain how a note pays. This repo measures how often each ending actually happens, what the coupon would need to be for each stock, and how the economics split between the two sides (COUPON and SHIELD).

Every number in the article can be reproduced from this code.

## What it does

- **Universe:** the eight Stock Tokens with feeds on Note Systems testnet: NVDA, TSLA, AAPL, MSFT, AMZN, META, COIN, HOOD.
- **Prices:** daily closes adjusted for splits and dividends (Yahoo Finance), which approximates the ERC-8056 multiplier already folded into Stock Token feeds.
- **Notes:** one new note struck at every Friday close from January 2015 to September 2025 (COIN from April 2021, HOOD from August 2021). 3,683 notes in total.
- **Terms (the standing template in the docs, Sep 2026):** 8 weekly observations, autocall at 100% of S0 on intermediate observations, coupon paid when the close is at or above 65% of S0, no coupon memory, knock-in judged only at the final observation (physical settlement at S0). Each observation uses the last close on or before the scheduled date.
- **Economics:** reference coupon of 50 bps per observation (the live coupon floats between 25 and 125 bps with demand), 25% coupon fee, 0.75% notional fee paid by SHIELD at strike. Series created under the earlier schedule use 15% and 0.25%.

## Headline results (current template)

| | |
|---|---|
| Notes | 3,683 |
| Autocalled at the first check (1 week) | 56.1% |
| Ended within four weeks | 79.0% |
| Ended early at any point | 85.3% |
| Ran all 8 weeks, repaid in cash | 13.5% |
| Knocked in | 1.1% (42 notes; average loss 43.6%, worst 61.1%) |
| Knock-ins from notes struck Sep 2021 to Nov 2022 | 30 of 42 |
| Ran all 8 weeks, ended down but above the barrier (SHIELD paid, protection never paid out) | 12.2% |
| SHIELD vs holding the stock, at 50 bps | -1.6% per note on average |

Break-even gross coupon per weekly observation (COUPON side, average profit of zero):

| AAPL | MSFT | AMZN | META | TSLA | NVDA | HOOD | COIN |
|---|---|---|---|---|---|---|---|
| 0 bps | 0 | 0 | 12 | 24 | 36 | 96 | 127 |

AAPL, MSFT and AMZN had no knock-ins in the sample, so their break-even is zero; that reflects the decade, not a claim that those notes are riskless. COIN's break-even sits just above the template's 125 bps cap.

Rolling the COUPON side at 50 bps (a new note the Friday after each one ends, from January 2015): about 15% a year on AAPL, MSFT, AMZN and META, 10% on TSLA, roughly flat on NVDA, -3% on HOOD and -28% on COIN.

The interactive page and `docs/notes.json` use this template (`backtest/gen_site_data.py`).

### Earlier template

`backtest.py`, `deep.py`, `roll.py` and the PNGs in `charts/` model the launch-era docs example: 26 fortnightly observations, 150 bps per observation, 15% and 0.25% fees. Under that template 58.6% of notes autocalled at the first check, 2.1% knocked in (average loss 60.1%), and 72 of 76 knock-ins came from notes struck Jul 2021 to May 2022.

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
