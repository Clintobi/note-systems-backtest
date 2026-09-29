"""Research-house chart set for the Note Systems backtest article.

House style modelled on institutional crypto research decks: charcoal background,
Title Case headline top-left, wordmark top-right, one-line method subtitle,
faint gridlines, legend centred at the bottom, 'Data as of | Source' footer.
Run with a Python that has matplotlib + numpy.
"""
import json, sys, datetime as dt, collections, bisect
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import FancyBboxPatch, Rectangle
from matplotlib.colors import ListedColormap
import matplotlib.dates as mdates

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backtest"))
import os; os.chdir(ROOT / "backtest")
from deep import run, stats, P  # noqa: E402

for f in ["/System/Library/Fonts/HelveticaNeue.ttc", "/System/Library/Fonts/Helvetica.ttc"]:
    try: fm.fontManager.addfont(f)
    except Exception: pass

BG_TOP, BG_BOT = "#232323", "#161616"
INK, INK2, INK3 = "#FFFFFF", "#A3A3A3", "#6E6E6E"
GRID = "#FFFFFF"
LAV = "#A99BFF"
PURPLE, GOLD, GREEN, RED, BLUE, TEAL, ORANGE = "#7B61FF", "#E8B21E", "#3DD68C", "#F0544F", "#4C8DF6", "#22B8CF", "#F28C28"
WORDMARK = "@0xbuchi"
ASOF = "Data as of Sep 23, 2026"
OUT = ROOT / "charts"

plt.rcParams.update({
    "font.family": "Helvetica Neue", "font.size": 20, "text.color": INK,
    "axes.labelcolor": INK2, "xtick.color": INK, "ytick.color": INK,
    "axes.edgecolor": "none", "axes.facecolor": "none", "figure.facecolor": BG_BOT,
    "xtick.labelsize": 20, "ytick.labelsize": 20, "axes.labelsize": 20,
    "legend.frameon": False, "legend.fontsize": 20,
})

def frame(title, subtitle, source="Yahoo Finance adjusted closes, Note Systems docs, @0xbuchi"):
    fig = plt.figure(figsize=(20.48, 11.52), dpi=100)
    bg = fig.add_axes([0, 0, 1, 1], zorder=-10); bg.axis("off")
    grad = np.linspace(0, 1, 256).reshape(-1, 1)
    bg.imshow(grad, aspect="auto", cmap=matplotlib.colors.LinearSegmentedColormap.from_list("g", [BG_TOP, BG_BOT]), extent=[0, 1, 0, 1])
    fig.text(0.033, 0.915, title, fontsize=40, weight="bold", color=INK, va="bottom")
    fig.text(0.967, 0.915, WORDMARK, fontsize=40, weight="bold", color=INK, va="bottom", ha="right")
    fig.text(0.033, 0.878, subtitle, fontsize=19, color=INK2, va="bottom")
    fig.text(0.967, 0.035, f"{ASOF} | Source: {source}", fontsize=18, weight="bold", color=LAV, ha="right")
    return fig

def style(ax, ygrid=True, xgrid=False):
    ax.grid(axis="y" if ygrid and not xgrid else ("x" if xgrid and not ygrid else "both"), color=GRID, alpha=0.08, lw=1)
    if not ygrid and not xgrid: ax.grid(False)
    ax.tick_params(length=0, pad=10)
    for s in ax.spines.values(): s.set_visible(False)

def legend_bottom(fig, handles, labels, ncol=None, y=0.075):
    fig.legend(handles, labels, loc="center", bbox_to_anchor=(0.5, y), ncol=ncol or len(labels), handlelength=1.6, columnspacing=2.4, fontsize=20)

def save(fig, name):
    fig.savefig(OUT / f"{name}.png", dpi=100, facecolor=BG_BOT)
    plt.close(fig); print("saved", name)

def note_box(ax, x, y, head, lines, w, h, color=PURPLE, transform=None):
    tr = transform or ax.transAxes
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.004,rounding_size=0.012", transform=tr,
                                facecolor="#221F38", edgecolor=color, lw=2, zorder=20))
    ax.text(x + 0.02, y + h - 0.045, head, transform=tr, fontsize=18, color=GREEN, zorder=21, va="top")
    for i, l in enumerate(lines):
        ax.text(x + 0.02, y + h - 0.12 - i * 0.07, l, transform=tr, fontsize=18 if i == 0 else 16,
                color=INK if i == 0 else INK2, zorder=21, va="top")

SYMS = ["NVDA", "TSLA", "AAPL", "MSFT", "AMZN", "META", "COIN", "HOOD"]
NOTES = {s: run(s) for s in SYMS}
ALL = sum(NOTES.values(), [])

# ---------------------------------------------------------------- 1 payoff
def payoff():
    fig = frame("Payoff at Maturity, Per 100 USDG of Notional",
                "Value at final observation vs final close as % of S0, excluding coupons; default terms, barrier 65%, autocall 100%")
    ax = fig.add_axes([0.075, 0.2, 0.78, 0.63]); style(ax, xgrid=False)
    x = np.linspace(0, 150, 1501)
    coupon = np.where(x >= 65, 100, x)            # cash above barrier, stock at S0 below
    stock = x                                     # holding the stock unhedged
    shield = np.where(x >= 65, x, 100)            # keeps stock above barrier, gets 100 below
    ax.axvspan(0, 65, color=RED, alpha=0.07, lw=0)
    ax.axvspan(65, 100, color=GOLD, alpha=0.06, lw=0)
    ax.plot(x, coupon, color=PURPLE, lw=4)
    ax.plot(x, shield, color=GOLD, lw=4)
    ax.axvline(65, color=RED, lw=1.5, ls="--", alpha=.8); ax.axvline(100, color=INK2, lw=1.2, ls="--", alpha=.6)
    ax.set_xlim(0, 150); ax.set_ylim(0, 160)
    ax.set_xticks([0, 25, 50, 65, 100, 125, 150]); ax.set_xticklabels(["0%", "25%", "50%", "65%\nbarrier", "100%\nS0", "125%", "150%"])
    ax.set_yticks(range(0, 161, 20)); ax.set_ylabel("Value at maturity (USDG)")
    ax.text(32, 150, "KNOCK-IN ZONE", color=RED, fontsize=17, ha="center")
    ax.text(82.5, 150, "SHIELD GAP", color=GOLD, fontsize=17, ha="center")
    ax.text(82.5, 142, "stock down, put never pays", color=INK2, fontsize=15, ha="center")
    ax.text(151, 100, " COUPON\n 100 cash", color=PURPLE, fontsize=19, va="center", clip_on=False)
    ax.text(151, 150, " SHIELD\n keeps stock", color=GOLD, fontsize=19, va="center", clip_on=False)
    ax.annotate("COUPON receives stock at S0:\nloses 1 - S_T/S0", xy=(40, 40), xytext=(8, 85), fontsize=16, color=INK2,
                arrowprops=dict(arrowstyle="-", color=INK3))
    ax.annotate("SHIELD swaps its stock\nfor 100 USDG", xy=(40, 100), xytext=(12, 120), fontsize=16, color=INK2,
                arrowprops=dict(arrowstyle="-", color=INK3))
    h = [plt.Line2D([], [], color=PURPLE, lw=4), plt.Line2D([], [], color=GOLD, lw=4)]
    legend_bottom(fig, h, ["COUPON (cash leg)", "SHIELD (stock leg, equals holding the stock above the barrier)"])
    save(fig, "01_payoff")

# ---------------------------------------------------------------- 2 table
def legs_table():
    fig = frame("COUPON vs SHIELD: What Each Leg Holds",
                "Both legs are ERC-1155 positions in the same series; one unit = 1 USDG of matched notional",
                source="Note Systems docs, @0xbuchi")
    ax = fig.add_axes([0.033, 0.1, 0.934, 0.76]); ax.axis("off"); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    rows = [
        ("DEPOSITS", "USDG", "Stock Tokens + USDG prefund of the max coupon bill (104.25% of notional in docs example)"),
        ("ROLE", "Sells crash insurance (the insurer)", "Buys crash insurance (the customer)"),
        ("OPTION POSITION", "Short a down-and-in put struck at S0", "Long a down-and-in put at S0 that switches off on autocall"),
        ("CASH FLOWS", "Receives coupon at every close >= barrier, net of 15% fee", "Pays gross coupon at every close >= barrier"),
        ("ON AUTOCALL", "Principal + that coupon, in cash", "Stock back + unused prefund; protection ends"),
        ("MATURITY >= 65%", "Principal in cash + final coupon", "Stock back + unused prefund"),
        ("MATURITY < 65%", "Stock Tokens valued at S0 (loss = 1 - S_T/S0)", "100 USDG per unit; stock goes to COUPON"),
        ("FEES", "15% of each paid coupon", "0.25% of matched notional at strike"),
        ("PRIMARY RISK", "Knock-in at maturity", "Paying coupons for cover that never pays"),
    ]
    x0, c1, c2 = 0.0, 0.19, 0.595
    ax.add_patch(Rectangle((c1 - .005, 0), c2 - c1 - .01, 1, facecolor="#2A2640", edgecolor="none"))
    ax.add_patch(Rectangle((c2 - .005, 0), 1 - c2 + .005, 1, facecolor="#2E2A1C", edgecolor="none"))
    ax.text(c1 + .01, 0.955, "COUPON", fontsize=24, weight="bold", color=PURPLE); ax.text(c1 + .12, 0.958, "CASH LEG", fontsize=15, color=INK2)
    ax.text(c2 + .01, 0.955, "SHIELD", fontsize=24, weight="bold", color=GOLD); ax.text(c2 + .105, 0.958, "STOCK LEG", fontsize=15, color=INK2)
    rh = 0.098
    for i, (k, a, b) in enumerate(rows):
        y = 0.9 - (i + 1) * rh + rh * 0.35
        ax.plot([0, 1], [0.9 - i * rh - 0.005] * 2, color=GRID, alpha=0.09, lw=1)
        ax.text(x0 + .005, y, k, fontsize=16, color=INK2, family="Menlo", va="center")
        ax.text(c1 + .01, y, a, fontsize=19, color=INK, va="center", wrap=True)
        ax.text(c2 + .01, y, b, fontsize=19, color=INK, va="center", wrap=True)
    save(fig, "02_legs_table")

# ---------------------------------------------------------------- 3 heatmap
def heatmap():
    fig = frame("Every Backtested Note, by Start Week",
                "3,683 notes, one struck every Friday close Jan 2015 - Sep 2025; 26 fortnightly observations, barrier 65%, autocall 100%")
    ax = fig.add_axes([0.075, 0.2, 0.9, 0.63]); style(ax, ygrid=False)
    starts = sorted({n["start"] for n in ALL})
    idx = {d: i for i, d in enumerate(starts)}
    code = {"ac1": 1, "ac": 2, "cash": 3, "ki": 4}
    M = np.zeros((len(SYMS), len(starts)))
    for r, s in enumerate(SYMS):
        for n in NOTES[s]:
            c = "ac1" if n["oc"] == "ac" and n["held"] == 1 else n["oc"]
            M[r, idx[n["start"]]] = code[c]
    cmap = ListedColormap(["#1C1C1C", PURPLE, BLUE, GOLD, RED])
    x0, x1 = mdates.date2num(starts[0]), mdates.date2num(starts[-1] + dt.timedelta(days=7))
    ax.imshow(M, aspect="auto", cmap=cmap, vmin=0, vmax=4, interpolation="nearest", extent=[x0, x1, len(SYMS) - .5, -.5])
    ax.set_yticks(range(len(SYMS))); ax.set_yticklabels(SYMS)
    ax.xaxis_date(); ax.xaxis.set_major_locator(mdates.YearLocator()); ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    for r in range(len(SYMS) - 1): ax.axhline(r + .5, color=BG_BOT, lw=4)
    a, b = mdates.date2num(dt.date(2021, 7, 1)), mdates.date2num(dt.date(2022, 6, 1))
    ax.add_patch(Rectangle((a, -.62), b - a, len(SYMS) + .24, fill=False, ec=GREEN, lw=2, ls="--", clip_on=False))
    ax.text((a + b) / 2, -.85, "JUL 2021 - MAY 2022 · 72 OF 76 KNOCK-INS", color=GREEN, fontsize=16, ha="center", clip_on=False)
    ax.text(mdates.date2num(dt.date(2019, 6, 1)), 6.5, "COIN, HOOD\nnot yet listed", color=INK3, fontsize=15, ha="center", va="center")
    h = [Rectangle((0, 0), 1, 1, color=c) for c in [PURPLE, BLUE, GOLD, RED]]
    legend_bottom(fig, h, ["Autocalled at first check (58.6%)", "Autocalled later (37.3%)", "Ran to term, cash (2.0%)", "Knocked in (2.1%)"])
    save(fig, "03_heatmap")

# ---------------------------------------------------------------- 4 duration
def duration():
    fig = frame("Most 52-Week Notes End at the First Check",
                "Share of notes by the observation at which they ended (autocall or maturity), all eight Stock Tokens, 3,683 notes")
    ax = fig.add_axes([0.075, 0.43, 0.87, 0.4]); style(ax)
    ax2 = fig.add_axes([0.075, 0.2, 0.87, 0.19]); style(ax2)
    ends = collections.Counter(n["held"] for n in ALL); N = len(ALL)
    xs = np.arange(1, 27); share = np.array([100 * ends.get(k, 0) / N for k in xs])
    col = [PURPLE] * 25 + [GOLD]
    ax.bar(xs, share, color=col, width=.72)
    for k in [1, 2, 3]: ax.text(k, share[k - 1] + 1.2, f"{share[k-1]:.1f}%", ha="center", fontsize=17)
    ax.text(26, share[-1] + 1.2, f"{share[-1]:.1f}%", ha="center", fontsize=17, color=GOLD)
    ax.set_xlim(.4, 26.6); ax.set_xticks([]); ax.set_ylabel("Share of notes (%)"); ax.set_ylim(0, 66)
    cum = np.cumsum(share)
    ax2.plot(xs, cum, color=INK, lw=3); ax2.fill_between(xs, cum, color=INK, alpha=.05)
    ax2.set_xlim(.4, 26.6); ax2.set_ylim(50, 102); ax2.set_yticks([60, 80, 100]); ax2.set_yticklabels(["60%", "80%", "100%"])
    ax2.set_xticks([1, 5, 10, 15, 20, 26]); ax2.set_xticklabels(["Wk 2", "Wk 10", "Wk 20", "Wk 30", "Wk 40", "Wk 52\nmaturity"])
    ax2.set_ylabel("Cumulative")
    ax2.text(6.2, 88, "90% of notes had ended by week 10", fontsize=17, color=INK2) if cum[4] >= 90 else None
    ax.text(14, 45, f"Median note: 2 weeks · Mean coupons paid: {stats(ALL)['mean_cpn']:.2f}", fontsize=19, color=INK2, ha="center")
    h = [Rectangle((0, 0), 1, 1, color=PURPLE), Rectangle((0, 0), 1, 1, color=GOLD), plt.Line2D([], [], color=INK, lw=3)]
    legend_bottom(fig, h, ["Ended early by autocall", "Reached maturity", "Cumulative share ended"])
    save(fig, "04_duration")

# ---------------------------------------------------------------- 5 cycle
def cycle():
    fig = frame("Knock-Ins Followed the Cycle Top",
                "Top: equal-weight index of the eight Stock Tokens (log, rebased to 100). Bottom: knocked-in notes by month of strike")
    ax = fig.add_axes([0.075, 0.4, 0.87, 0.43]); style(ax)
    ax2 = fig.add_axes([0.075, 0.2, 0.87, 0.17]); style(ax2)
    series = {s: {dt.date.fromisoformat(d): p for d, p in P[s]} for s in SYMS}
    days = sorted(set().union(*[set(v) for v in series.values()]))
    days = [d for d in days if d >= dt.date(2015, 1, 2)]
    lvl = 100.0; out = []; prev = {}
    for d in days:
        rets = []
        for s in SYMS:
            if d in series[s]:
                if s in prev: rets.append(series[s][d] / prev[s] - 1)
                prev[s] = series[s][d]
        if rets: lvl *= 1 + np.mean(rets)
        out.append(lvl)
    ax.plot(days, out, color=PURPLE, lw=2.6); ax.set_yscale("log")
    ax.set_yticks([100, 300, 1000, 3000]); ax.set_yticklabels(["100", "300", "1,000", "3,000"]); ax.minorticks_off()
    a, b = dt.date(2021, 7, 1), dt.date(2022, 6, 1)
    for x in (ax, ax2): x.axvspan(a, b, color=GREEN, alpha=.1, lw=0)
    ax.text(dt.date(2021, 12, 15), out[0] * 1.2, "Notes struck here\nproduced 72 of 76 knock-ins", color=GREEN, fontsize=17, ha="center")
    ki = collections.Counter(dt.date(n["start"].year, n["start"].month, 15) for n in ALL if n["oc"] == "ki")
    ax2.bar(list(ki), list(ki.values()), width=25, color=RED)
    ax2.set_ylabel("Knock-ins"); ax2.set_yticks([0, 10, 20])
    for x in (ax, ax2): x.set_xlim(dt.date(2015, 1, 1), dt.date(2026, 9, 30)); x.xaxis.set_major_locator(mdates.YearLocator()); x.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.set_xticklabels([])
    h = [plt.Line2D([], [], color=PURPLE, lw=3), Rectangle((0, 0), 1, 1, color=RED), Rectangle((0, 0), 1, 1, color=GREEN, alpha=.3)]
    legend_bottom(fig, h, ["Equal-weight index (log)", "Knocked-in notes by strike month", "Jul 2021 - May 2022"])
    save(fig, "05_cycle")

# ---------------------------------------------------------------- 6 return dist
def returns():
    fig = frame("Small, Frequent Gains and Rare, Deep Losses",
                "Distribution of per-note COUPON return at the docs' illustrative 150 bps gross coupon (1.275% net), log count scale, 3,683 notes")
    ax = fig.add_axes([0.075, 0.2, 0.87, 0.63]); style(ax)
    r = np.array([100 * (n["cp"] * .015 * .85 + ((n["ratio"] - 1) if n["oc"] == "ki" else 0)) for n in ALL])
    bins = np.arange(-90, 40, 2.5)
    h, e = np.histogram(r, bins=bins)
    cols = [RED if x < 0 else PURPLE for x in e[:-1]]
    ax.bar(e[:-1] + 1.25, np.where(h > 0, h, np.nan), width=2.2, color=cols)
    ax.set_yscale("log"); ax.set_ylim(.8, 5000); ax.set_yticks([1, 10, 100, 1000]); ax.set_yticklabels(["1", "10", "100", "1,000"]); ax.minorticks_off()
    ax.set_xlim(-90, 40); ax.set_xticks(range(-80, 41, 20)); ax.set_xticklabels([f"{x:+d}%" if x else "0%" for x in range(-80, 41, 20)])
    ax.set_xlabel("Return over the life of the note"); ax.set_ylabel("Number of notes (log)")
    ax.axvline(0, color=INK2, lw=1.2, ls="--")
    med = np.median(r)
    ax.annotate(f"Median {med:+.2f}%\n(one coupon, then autocall)", xy=(med, 2000), xytext=(10, 2400), fontsize=17, color=INK2,
                arrowprops=dict(arrowstyle="-", color=INK3))
    note_box(ax, 0.06, 0.52, "LEFT TAIL", [f"{(r < 0).sum()} notes lost money ({100*(r<0).mean():.1f}%)", f"Worst {r.min():.1f}%, all from knock-ins"], .36, .25)
    hh = [Rectangle((0, 0), 1, 1, color=PURPLE), Rectangle((0, 0), 1, 1, color=RED)]
    legend_bottom(fig, hh, ["Notes with a gain", "Notes with a loss"])
    save(fig, "06_returns")

# ---------------------------------------------------------------- 7 break-even
def breakeven():
    fig = frame("Break-Even Coupons Span Two Orders of Magnitude",
                "Gross coupon per observation at which COUPON broke even on average, net of 15% fee; markers show barrier at 60%, 65%, 70%")
    ax = fig.add_axes([0.1, 0.2, 0.78, 0.63]); style(ax, ygrid=False, xgrid=True)
    order = ["AAPL", "MSFT", "TSLA", "AMZN", "NVDA", "META", "COIN", "HOOD"]
    vals = {s: {b: stats(run(s, barrier=b))["fair_bps"] for b in (0.60, 0.65, 0.70)} for s in order}
    ax.set_xscale("symlog", linthresh=10); ax.set_xlim(-1, 400)
    ax.set_xticks([0, 10, 30, 100, 150, 300]); ax.set_xticklabels(["0", "10", "30", "100", "150", "300 bps"]); ax.minorticks_off()
    for i, s in enumerate(order):
        v = vals[s]
        ax.plot([v[0.60], v[0.70]], [i, i], color=INK3, lw=3, solid_capstyle="round", zorder=1)
        ax.scatter([v[0.60]], [i], s=120, color=BG_BOT, edgecolor=PURPLE, lw=2.5, zorder=3)
        ax.scatter([v[0.70]], [i], s=120, color=BG_BOT, edgecolor=GOLD, lw=2.5, zorder=3)
        ax.scatter([v[0.65]], [i], s=260, color=INK, zorder=4)
        lab = "0 (no knock-ins in sample)" if v[0.65] == 0 else f"{v[0.65]:.0f} bps"
        ax.text(max(v[0.70], 1) * 1.25 + 2, i, lab, va="center", fontsize=18, color=INK2)
    ax.set_yticks(range(len(order))); ax.set_yticklabels(order); ax.set_ylim(-.7, len(order) - .3)
    ax.axvline(150, color=RED, lw=2, ls="--")
    ax.text(150, len(order) - .25, "  Docs illustrative rate: 150 bps", color=RED, fontsize=17, va="bottom")
    h = [plt.Line2D([], [], marker="o", ls="", color=INK, ms=14), plt.Line2D([], [], marker="o", ls="", mfc=BG_BOT, mec=PURPLE, mew=2.5, ms=11),
         plt.Line2D([], [], marker="o", ls="", mfc=BG_BOT, mec=GOLD, mew=2.5, ms=11)]
    legend_bottom(fig, h, ["Barrier 65% (default)", "Barrier 60%", "Barrier 70%"])
    save(fig, "07_breakeven")

# ---------------------------------------------------------------- 8 barrier
def barrier():
    fig = frame("Lower Barriers Trade Frequency for Severity",
                "Knock-in rate and average principal loss on knocked-in notes by barrier level, all eight Stock Tokens, 3,683 notes per level")
    bs = np.arange(0.50, 0.81, 0.025)
    st_ = [stats(sum((run(s, barrier=b) for s in SYMS), [])) for b in bs]
    ax = fig.add_axes([0.075, 0.2, 0.4, 0.6]); style(ax)
    ax2 = fig.add_axes([0.56, 0.2, 0.4, 0.6]); style(ax2)
    x = bs * 100
    ki = [s["ki"] for s in st_]; loss = [s["ki_loss"] for s in st_]
    ax.plot(x, ki, color=RED, lw=3.5, marker="o", ms=8); ax2.plot(x, loss, color=GOLD, lw=3.5, marker="o", ms=8)
    for a, y, fmt in [(ax, ki, "{:.1f}%"), (ax2, loss, "{:.0f}%")]:
        a.axvline(65, color=INK2, lw=1.2, ls="--"); a.set_xticks([50, 55, 60, 65, 70, 75, 80]); a.set_xticklabels([f"{v}%" for v in [50, 55, 60, 65, 70, 75, 80]])
        a.set_xlabel("Barrier (% of S0)")
        for xi, yi in [(x[0], y[0]), (x[6], y[6]), (x[-1], y[-1])]: a.text(xi, yi + (0.12 if a is ax else 1.5), fmt.format(yi), ha="center", fontsize=17)
    ax.set_title("Share of notes knocked in", loc="left", fontsize=22, color=INK, pad=14); ax.set_ylim(0, 3.4)
    ax.set_yticks([0, 1, 2, 3]); ax.set_yticklabels(["0%", "1%", "2%", "3%"])
    ax2.set_title("Average loss when knocked in", loc="left", fontsize=22, color=INK, pad=14); ax2.set_ylim(40, 72)
    ax2.set_yticks([40, 50, 60, 70]); ax2.set_yticklabels(["40%", "50%", "60%", "70%"])
    h = [plt.Line2D([], [], color=RED, lw=3.5), plt.Line2D([], [], color=GOLD, lw=3.5), plt.Line2D([], [], color=INK2, lw=1.2, ls="--")]
    legend_bottom(fig, h, ["Knock-in rate", "Average loss on knocked-in notes", "Docs default, 65%"])
    save(fig, "08_barrier")

# ---------------------------------------------------------------- 9 length
def length():
    fig = frame("Shorter Notes Leave SHIELD Exposed More Often",
                "Outcome mix by template length, fortnightly observations, same 3,683 start dates; gold = stock ended between barrier and S0")
    ax = fig.add_axes([0.14, 0.2, 0.8, 0.63]); style(ax, ygrid=False, xgrid=True)
    lens = [(4, "8 weeks"), (8, "16 weeks"), (13, "26 weeks"), (26, "52 weeks (docs)")]
    for i, (n, lab) in enumerate(lens):
        s = stats(sum((run(sym, n_obs=n) for sym in SYMS), []))
        left = 0
        for k, c in [("ac", BLUE), ("cash", GOLD), ("ki", RED)]:
            ax.barh(i, s[k], left=left, color=c, height=.62, edgecolor=BG_BOT, lw=2)
            if s[k] > 4: ax.text(left + 1.2, i, f"{s[k]:.1f}%", va="center", fontsize=18, color="#111" if c == GOLD else INK)
            left += s[k]
        ax.text(101, i, f"{s['ki']:.1f}%", va="center", fontsize=18, color=RED)
    ax.set_yticks(range(4)); ax.set_yticklabels([l for _, l in lens]); ax.invert_yaxis()
    ax.set_xlim(0, 100); ax.set_xticks([0, 25, 50, 75, 100]); ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"])
    h = [Rectangle((0, 0), 1, 1, color=c) for c in [BLUE, GOLD, RED]]
    legend_bottom(fig, h, ["Autocalled", "Ran to term between barrier and S0 (SHIELD gap)", "Knocked in"])
    save(fig, "09_length")

# ---------------------------------------------------------------- 10 shield
def shield():
    fig = frame("SHIELD Paid for Protection It Mostly Did Not Need",
                "Average SHIELD result vs holding the same stock unhedged, per note, at the docs' 150 bps coupon; includes 0.25% notional fee")
    ax = fig.add_axes([0.1, 0.2, 0.84, 0.63]); style(ax, ygrid=False, xgrid=True)
    d = sorted(((stats(NOTES[s])["shield_vs_hold"], s) for s in SYMS))
    for i, (v, s) in enumerate(d):
        ax.barh(i, v, color=GREEN if v > 0 else RED, height=.6)
        ax.text(v + (0.12 if v > 0 else -0.12), i, f"{v:+.1f}%", va="center", ha="left" if v > 0 else "right", fontsize=18)
    allv = stats(ALL)["shield_vs_hold"]
    ax.axvline(allv, color=INK2, lw=1.5, ls="--"); ax.text(allv, len(d) - .35, f"  All notes: {allv:+.1f}%", color=INK2, fontsize=17)
    ax.axvline(0, color=INK, lw=1.2, alpha=.5)
    ax.set_yticks(range(len(d))); ax.set_yticklabels([s for _, s in d]); ax.set_xlim(-7.5, 3)
    ax.set_xticks([-6, -4, -2, 0, 2]); ax.set_xticklabels(["-6%", "-4%", "-2%", "0%", "+2%"])
    h = [Rectangle((0, 0), 1, 1, color=RED), Rectangle((0, 0), 1, 1, color=GREEN)]
    legend_bottom(fig, h, ["SHIELD trailed holding", "SHIELD beat holding"])
    save(fig, "10_shield")

# ---------------------------------------------------------------- 11 roll
def roll():
    R = json.load(open(ROOT / "backtest" / "roll.json"))
    fig = frame("Rolling COUPON vs Holding the Stock",
                "Growth of 1 USDG, COUPON rolled back to back at the docs' 150 bps coupon vs buy-and-hold, log scale; COIN and HOOD from listing")
    order = ["AAPL", "MSFT", "META", "AMZN", "TSLA", "NVDA", "HOOD", "COIN"]
    for k, s in enumerate(order):
        r, c = divmod(k, 4)
        ax = fig.add_axes([0.06 + c * 0.235, 0.55 - r * 0.36, 0.195, 0.25]); style(ax); ax.margins(x=0.05)
        path = [(dt.date.fromisoformat(d), w) for d, w in R[s]["path"]]
        start = path[0][0] - dt.timedelta(days=14 * 1)
        px = [(dt.date.fromisoformat(d), p) for d, p in P[s] if dt.date.fromisoformat(d) >= start]
        p0 = px[0][1]
        ax.plot([d for d, _ in px], [p / p0 for _, p in px], color=INK3, lw=1.8)
        ax.plot([start] + [d for d, _ in path], [1] + [w for _, w in path], color=GOLD, lw=2.6, drawstyle="steps-post")
        ax.set_yscale("log"); ax.minorticks_off(); ax.tick_params(labelsize=14, pad=6)
        ax.xaxis.set_major_locator(mdates.YearLocator(4 if s not in ("COIN", "HOOD") else 2)); ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}x"))
        ax.set_title(f"{s}", loc="left", fontsize=22, weight="bold", color=INK, pad=30)
        ax.text(0, 1.03, f"roll {R[s]['cagr']:+.0f}%/yr · hold {R[s]['hold_cagr']:+.0f}%/yr", transform=ax.transAxes, ha="left", fontsize=15, color=INK2)
    h = [plt.Line2D([], [], color=GOLD, lw=3), plt.Line2D([], [], color=INK3, lw=2)]
    legend_bottom(fig, h, ["Roll COUPON notes", "Hold the stock"], y=0.085)
    save(fig, "11_roll")

def header():
    fig = plt.figure(figsize=(15, 6), dpi=100)
    bg = fig.add_axes([0, 0, 1, 1], zorder=-10); bg.axis("off")
    bg.imshow(np.linspace(0, 1, 256).reshape(-1, 1), aspect="auto", cmap=matplotlib.colors.LinearSegmentedColormap.from_list("g", [BG_TOP, BG_BOT]), extent=[0, 1, 0, 1])
    ax = fig.add_axes([0.0, 0.0, 1, 0.34]); ax.axis("off")
    starts = sorted({n["start"] for n in ALL}); idx = {d: i for i, d in enumerate(starts)}
    code = {"ac1": 1, "ac": 2, "cash": 3, "ki": 4}; M = np.zeros((len(SYMS), len(starts)))
    for r, s in enumerate(SYMS):
        for n in NOTES[s]:
            M[r, idx[n["start"]]] = code["ac1" if n["oc"] == "ac" and n["held"] == 1 else n["oc"]]
    ax.imshow(M, aspect="auto", cmap=ListedColormap(["#1C1C1C", PURPLE, BLUE, GOLD, RED]), vmin=0, vmax=4, interpolation="nearest", alpha=.9)
    for r in range(len(SYMS) - 1): ax.axhline(r + .5, color=BG_BOT, lw=2)
    fig.text(0.045, 0.80, "Structured Notes Onchain", fontsize=52, weight="bold", color=INK, va="center")
    fig.text(0.045, 0.64, "Backtesting Note Systems across a decade of stock prices", fontsize=26, color=INK2, va="center")
    fig.text(0.045, 0.49, "3,683 notes · 8 Stock Tokens · 2015 to 2025", fontsize=20, color=LAV, weight="bold", va="center")
    fig.text(0.955, 0.80, WORDMARK, fontsize=26, weight="bold", color=INK, va="center", ha="right")
    fig.savefig(OUT / "00_header.png", dpi=100, facecolor=BG_BOT); plt.close(fig); print("saved 00_header")

if __name__ == "__main__":
    header()
    for f in [payoff, legs_table, heatmap, duration, cycle, returns, breakeven, barrier, length, shield, roll]:
        f()
