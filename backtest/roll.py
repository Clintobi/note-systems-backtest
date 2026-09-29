import json, datetime as dt, collections
from backtest import run, coupon_return, DOCS_GROSS, prices
R = json.load(open("results.json"))
notes = R["notes"]
# when did knock-ins start?
ki = collections.Counter((n["sym"], n["start"][:7]) for n in notes if n["outcome"] == "knock-in")
print("knock-in start months:", sorted(ki.items()))
# autocall at first observation
print("autocalled at obs 1: %.1f%%" % (100*sum(n["outcome"]=="autocall" and n["held"]==1 for n in notes)/len(notes)))
# rolling depositor: back-to-back notes from first eligible Friday
def roll(sym, gross, start="2015-01-02"):
    ns = [n for n in notes if n["sym"] == sym]
    by = {n["start"]: n for n in ns}
    starts = sorted(by)
    w, d, path, kis = 1.0, max(start, starts[0]), [], []
    i = next(j for j,s in enumerate(starts) if s >= d)
    while i < len(starts):
        n = by[starts[i]]
        w *= 1 + coupon_return(n, gross)
        end = dt.date.fromisoformat(n["start"]) + dt.timedelta(days=14*n["held"])
        path.append((end.isoformat(), w))
        if n["outcome"] == "knock-in": kis.append((n["start"], round(100*(n["ratio"]-1))))
        i = next((j for j in range(i+1, len(starts)) if starts[j] >= end.isoformat()), len(starts))
    yrs = (dt.date.fromisoformat(path[-1][0]) - dt.date.fromisoformat(starts[0] if starts[0]>start else start)).days/365
    px = dict(prices[sym]); d0 = min(k for k in px if k >= (starts[0] if starts[0]>start else start)); d1 = max(k for k in px if k <= path[-1][0])
    hold = px[d1]/px[d0]
    return dict(sym=sym, notes=len(path), years=round(yrs,1), wealth=round(w,2), cagr=round(100*(w**(1/yrs)-1),1),
                hold_multiple=round(hold,2), hold_cagr=round(100*(hold**(1/yrs)-1),1), knockins=kis, path=path)
out = {}
for s in prices:
    r = roll(s, DOCS_GROSS); out[s] = r
    print(f"{s:5} notes={r['notes']:3} yrs={r['years']} COUPON-roll x{r['wealth']} ({r['cagr']}%/yr) | hold stock x{r['hold_multiple']} ({r['hold_cagr']}%/yr) | knock-ins {r['knockins']}")
json.dump(out, open("roll.json","w"))
