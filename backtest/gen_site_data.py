"""Export every backtested note (with its observation path) for the interactive page in docs/.

Terms are the per-underlying standing templates published in the Note Systems docs
(concepts/autocallable-notes, "Standing templates", testnet deployment 11, 29 Sep 2026):
twelve weekly coupon observations five trading days apart, autocall and barrier per
underlying, 25% coupon fee, 0.75% notional fee paid by SHIELD at strike. The coupon is
held at each template's reference rate (the rate a balanced book discovers).
"""
import datetime as dt, json, statistics as st

P = json.load(open("prices.json"))
N_OBS, STEP, FEE, NFEE = 12, 5, 0.25, 0.0075
# underlying: (autocall, barrier, coupon floor, reference, coupon cap), coupons per weekly observation
TEMPLATES = {
    "AAPL": (1.05, 0.88, 0.0010, 0.0030, 0.0060),
    "MSFT": (1.05, 0.85, 0.0010, 0.0045, 0.0080),
    "AMZN": (1.05, 0.85, 0.0025, 0.0050, 0.0095),
    "NVDA": (1.05, 0.80, 0.0015, 0.0045, 0.0140),
    "META": (1.05, 0.80, 0.0030, 0.0055, 0.0100),
    "TSLA": (1.10, 0.75, 0.0030, 0.0055, 0.0150),
    "HOOD": (1.10, 0.60, 0.0025, 0.0075, 0.0130),
    "COIN": (1.10, 0.60, 0.0040, 0.0075, 0.0160),
}


def run(sym):
    """One note struck at every Friday close, 2015-01-01 to 2025-09-19."""
    ac, bar, _, ref, _ = TEMPLATES[sym]
    days = [dt.date.fromisoformat(d) for d, _ in P[sym]]
    px = [p for _, p in P[sym]]
    notes = []
    for i, d0 in enumerate(days):
        if d0.weekday() != 4 or d0 < dt.date(2015, 1, 1) or d0 > dt.date(2025, 9, 19): continue
        if i + STEP * N_OBS >= len(px): break
        s0 = px[i]; path = []; cp = 0; oc = None
        for k in range(1, N_OBS + 1):
            r = px[i + STEP * k] / s0; path.append(round(r, 4))
            if k < N_OBS:
                if r >= bar: cp += 1
                if r >= ac: oc = "ac"; break
            else:
                if r >= bar: cp += 1; oc = "cash"
                else: oc = "ki"
        fin = path[-1]; end = days[i + STEP * len(path)]
        coupon_ret = cp * ref * (1 - FEE) + ((fin - 1) if oc == "ki" else 0)
        shield = ((1 - fin) if oc == "ki" else 0) - cp * ref - NFEE
        notes.append({"d": d0.isoformat(), "e": end.isoformat(), "s0": round(s0, 2), "o": oc, "h": len(path),
                      "c": cp, "p": path, "r": round(coupon_ret, 4), "sh": round(shield, 4)})
    return notes


if __name__ == "__main__":
    out = {"meta": {"obs": N_OBS, "step_trading_days": STEP, "fee": FEE, "notional_fee": NFEE,
                    "source": "Note Systems docs, standing templates, testnet deployment 11, 29 Sep 2026"}, "stocks": {}}
    for s in TEMPLATES:
        notes = run(s); k = len(notes); ki = [n for n in notes if n["o"] == "ki"]
        ac, bar, lo, ref, cap = TEMPLATES[s]
        ml = st.mean([(n["p"][-1] - 1) if n["o"] == "ki" else 0 for n in notes]); mc = st.mean([n["c"] for n in notes])
        out["stocks"][s] = {"t": {"ac": ac, "bar": bar, "floor": lo, "ref": ref, "cap": cap}, "notes": notes, "summary": {
            "n": k, "ac1": round(100 * sum(n["o"] == "ac" and n["h"] == 1 for n in notes) / k, 1),
            "ki": round(100 * len(ki) / k, 1), "fair_bps": round(10000 * (-ml / mc) / (1 - FEE), 0) if mc else 0,
            "avg_ret": round(100 * st.mean(n["r"] for n in notes), 2), "shield": round(100 * st.mean(n["sh"] for n in notes), 2)}}
    json.dump(out, open("../docs/notes.json", "w"), separators=(",", ":"))
    print({s: v["summary"] for s, v in out["stocks"].items()}); print(sum(len(v["notes"]) for v in out["stocks"].values()), "notes")
