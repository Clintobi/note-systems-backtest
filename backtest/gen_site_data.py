"""Export every backtested note (with its observation path) for the interactive page in docs/."""
import bisect, datetime as dt, json, statistics as st
P = json.load(open("prices.json"))
BAR, N_OBS, GROSS, FEE = 0.65, 26, 0.015, 0.15
out = {"meta": {"barrier": BAR, "obs": N_OBS, "gross_bps": 150, "fee": FEE}, "stocks": {}}
for s, rows in P.items():
    days = [dt.date.fromisoformat(d) for d, _ in rows]; px = [p for _, p in rows]
    close = lambda d: px[bisect.bisect_right(days, d) - 1]
    notes = []
    for i, d0 in enumerate(days):
        if d0.weekday() != 4 or d0 < dt.date(2015, 1, 1) or d0 > dt.date(2025, 9, 19): continue
        s0 = px[i]; path = []; cp = 0; oc = None
        for k in range(1, N_OBS + 1):
            r = close(d0 + dt.timedelta(days=14 * k)) / s0; path.append(round(r, 4))
            if k < N_OBS:
                if r >= BAR: cp += 1
                if r >= 1: oc = "ac"; break
            else:
                if r >= BAR: cp += 1; oc = "cash"
                else: oc = "ki"
        held = len(path); fin = path[-1]
        coupon_ret = cp * GROSS * (1 - FEE) + ((fin - 1) if oc == "ki" else 0)
        shield = ((1 - fin) if oc == "ki" else 0) - cp * GROSS - 0.0025
        notes.append({"d": d0.isoformat(), "s0": round(s0, 2), "o": oc, "h": held, "c": cp,
                      "p": path, "r": round(coupon_ret, 4), "sh": round(shield, 4)})
    k = len(notes); ki = [n for n in notes if n["o"] == "ki"]
    ml = st.mean([(n["p"][-1] - 1) if n["o"] == "ki" else 0 for n in notes]); mc = st.mean([n["c"] for n in notes])
    out["stocks"][s] = {"notes": notes, "summary": {
        "n": k, "ac1": round(100 * sum(n["o"] == "ac" and n["h"] == 1 for n in notes) / k, 1),
        "ki": round(100 * len(ki) / k, 1), "fair_bps": round(10000 * (-ml / mc) / (1 - FEE), 0) if mc else 0,
        "avg_ret": round(100 * st.mean(n["r"] for n in notes), 2), "shield": round(100 * st.mean(n["sh"] for n in notes), 2)}}
json.dump(out, open("../docs/notes.json", "w"), separators=(",", ":"))
print({s: v["summary"] for s, v in out["stocks"].items()}); print(sum(len(v["notes"]) for v in out["stocks"].values()), "notes")
