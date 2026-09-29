"""Backtest of the Note Systems default autocallable on real stock history.

Terms follow the protocol defaults in note.systems/docs:
  26 fortnightly observations (52 weeks), autocall at 100% of S0 on obs 1..25,
  coupon paid on any observation with close >= 65% of S0 (no memory),
  knock-in judged only at obs 26: close < 65% -> paid in stock at S0.
  Coupon fee 15% of gross coupon (COUPON side), notional fee 0.25% (SHIELD side).
One note starts every Friday close. Prices are Yahoo adjusted closes (splits and
dividends folded in, like the ERC-8056 multiplier in Stock Token feeds).
"""
import bisect
import datetime as dt
import json
import statistics as st

BARRIER, AUTOCALL, N_OBS, FEE = 0.65, 1.00, 26, 0.15
DOCS_GROSS = 0.015  # docs' illustrative 150 bps per observation

prices = json.load(open("prices.json"))


def run(sym):
    days = [dt.date.fromisoformat(d) for d, _ in prices[sym]]
    px = [p for _, p in prices[sym]]

    def close_on_or_before(d):
        i = bisect.bisect_right(days, d) - 1
        return px[i] if i >= 0 else None

    notes = []
    for i, d0 in enumerate(days):
        if d0.weekday() != 4 or d0 < dt.date(2015, 1, 1):
            continue
        maturity = d0 + dt.timedelta(days=14 * N_OBS)
        if maturity > days[-1]:
            break
        s0, coupons, outcome, ratio, held = px[i], 0, None, None, 0
        for k in range(1, N_OBS + 1):
            p = close_on_or_before(d0 + dt.timedelta(days=14 * k))
            r = p / s0
            if k < N_OBS:
                if r >= BARRIER:
                    coupons += 1
                if r >= AUTOCALL:
                    outcome, held = "autocall", k
                    break
            else:
                held = k
                if r >= BARRIER:
                    coupons += 1
                    outcome = "cash"
                else:
                    outcome, ratio = "knock-in", r
        notes.append(dict(sym=sym, start=d0.isoformat(), outcome=outcome,
                          coupons=coupons, held=held, ratio=ratio))
    return notes


def coupon_return(n, gross):
    loss = (n["ratio"] - 1) if n["outcome"] == "knock-in" else 0.0
    return n["coupons"] * gross * (1 - FEE) + loss


def shield_vs_holding(n, gross):
    put = (1 - n["ratio"]) if n["outcome"] == "knock-in" else 0.0
    return put - n["coupons"] * gross - 0.0025


def summarize(notes):
    k = len(notes)
    ac = [n for n in notes if n["outcome"] == "autocall"]
    ki = [n for n in notes if n["outcome"] == "knock-in"]
    rets = [coupon_return(n, DOCS_GROSS) for n in notes]
    ann = [coupon_return(n, DOCS_GROSS) / (n["held"] * 14 / 365) for n in notes]
    mean_loss = st.mean([(n["ratio"] - 1) if n["outcome"] == "knock-in" else 0 for n in notes])
    mean_cpn = st.mean([n["coupons"] for n in notes])
    fair_net = -mean_loss / mean_cpn if mean_cpn else 0  # net coupon where COUPON breaks even
    return dict(
        notes=k,
        autocall_pct=100 * len(ac) / k,
        median_autocall_weeks=st.median([2 * n["held"] for n in ac]) if ac else None,
        autocall_first_obs_pct=100 * sum(n["held"] == 1 for n in ac) / k,
        cash_maturity_pct=100 * sum(n["outcome"] == "cash" for n in notes) / k,
        knockin_pct=100 * len(ki) / k,
        avg_knockin_loss_pct=100 * st.mean([1 - n["ratio"] for n in ki]) if ki else 0,
        worst_knockin_loss_pct=100 * max([1 - n["ratio"] for n in ki]) if ki else 0,
        avg_coupons=mean_cpn,
        docs_rate_avg_return_pct=100 * st.mean(rets),
        docs_rate_avg_annualized_pct=100 * st.mean(ann),
        docs_rate_losing_pct=100 * sum(r < 0 for r in rets) / k,
        docs_rate_worst_pct=100 * min(rets),
        shield_avg_vs_holding_pct=100 * st.mean(shield_vs_holding(n, DOCS_GROSS) for n in notes),
        fair_gross_bps_per_obs=10000 * fair_net / (1 - FEE),
        fair_gross_annual_pct=100 * 26 * fair_net / (1 - FEE),
    )


if __name__ == "__main__":
    allnotes, table = [], {}
    for s in prices:
        ns = run(s)
        allnotes += ns
        table[s] = summarize(ns)
    table["ALL"] = summarize(allnotes)
    json.dump(dict(table=table, notes=allnotes), open("results.json", "w"), indent=1)
    cols = ["notes", "autocall_pct", "median_autocall_weeks", "cash_maturity_pct", "knockin_pct",
            "avg_knockin_loss_pct", "worst_knockin_loss_pct", "docs_rate_avg_annualized_pct",
            "docs_rate_losing_pct", "docs_rate_worst_pct", "shield_avg_vs_holding_pct",
            "fair_gross_bps_per_obs", "fair_gross_annual_pct"]
    print("sym  " + " | ".join(c[:14] for c in cols))
    for s, r in table.items():
        print(f"{s:5}" + " | ".join(f"{(r[c] if r[c] is not None else 0):14.1f}" for c in cols))
