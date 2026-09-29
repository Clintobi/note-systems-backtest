import json,bisect,datetime as dt,statistics as st,collections
P=json.load(open("prices.json")); FEE=0.15; DOCS=0.015
def run(sym,barrier=0.65,n_obs=26,step=14,start=dt.date(2015,1,1),end_start=dt.date(2025,9,19)):
    days=[dt.date.fromisoformat(d) for d,_ in P[sym]]; px=[p for _,p in P[sym]]
    def c(d):
        i=bisect.bisect_right(days,d)-1; return px[i]
    out=[]
    for i,d0 in enumerate(days):
        if d0.weekday()!=4 or d0<start or d0>end_start: continue
        if d0+dt.timedelta(days=step*n_obs)>days[-1]: break
        s0=px[i]; cp=0; oc=None; ratio=None; held=0
        for k in range(1,n_obs+1):
            r=c(d0+dt.timedelta(days=step*k))/s0
            if k<n_obs:
                if r>=barrier: cp+=1
                if r>=1: oc,held="ac",k; break
            else:
                held=k
                if r>=barrier: cp+=1; oc="cash"; ratio=r
                else: oc="ki"; ratio=r
        out.append(dict(sym=sym,start=d0,oc=oc,cp=cp,held=held,ratio=ratio))
    return out
def stats(ns,n_obs=26):
    k=len(ns); ki=[n for n in ns if n["oc"]=="ki"]; ac=[n for n in ns if n["oc"]=="ac"]; cash=[n for n in ns if n["oc"]=="cash"]
    ml=st.mean([(n["ratio"]-1) if n["oc"]=="ki" else 0 for n in ns]); mc=st.mean([n["cp"] for n in ns])
    fair=(-ml/mc)/(1-FEE) if mc else 0
    cret=[n["cp"]*DOCS*(1-FEE)+((n["ratio"]-1) if n["oc"]=="ki" else 0) for n in ns]
    shield=[((1-n["ratio"]) if n["oc"]=="ki" else 0)-n["cp"]*DOCS-0.0025 for n in ns]
    trap_loss=[1-n["ratio"] for n in cash if n["ratio"]<1]
    return dict(n=k,ac1=100*sum(n["oc"]=="ac" and n["held"]==1 for n in ns)/k,ac=100*len(ac)/k,
        med_wk=st.median([n["held"]*2 for n in ns]),mean_cpn=mc,cash=100*len(cash)/k,ki=100*len(ki)/k,
        ki_loss=100*st.mean([1-n["ratio"] for n in ki]) if ki else 0,ki_worst=100*max([1-n["ratio"] for n in ki]) if ki else 0,
        fair_bps=10000*fair,docs_mean=100*st.mean(cret),docs_lose=100*sum(r<0 for r in cret)/k,
        shield_vs_hold=100*st.mean(shield),trap_avg_loss=100*st.mean(trap_loss) if trap_loss else 0)
syms=list(P)
R={}
print("== per stock, default template")
base={s:run(s) for s in syms}; allb=sum(base.values(),[])
for s in syms+["ALL"]:
    ns=allb if s=="ALL" else base[s]; r=stats(ns); R[s]=r
    print(f"{s:5} n={r['n']:4} ac1={r['ac1']:5.1f} ac={r['ac']:5.1f} medwk={r['med_wk']:4.0f} cpn={r['mean_cpn']:4.2f} cash={r['cash']:4.1f} ki={r['ki']:4.1f} kiloss={r['ki_loss']:5.1f} worst={r['ki_worst']:5.1f} fair={r['fair_bps']:6.1f} docsmean={r['docs_mean']:5.2f} lose={r['docs_lose']:4.1f} shield={r['shield_vs_hold']:5.2f} traploss={r['trap_avg_loss']:4.1f}")
print("\n== barrier sensitivity (ALL)")
SB={}
for b in [0.50,0.55,0.60,0.65,0.70,0.75,0.80]:
    ns=sum((run(s,barrier=b) for s in syms),[]); r=stats(ns); SB[b]=r
    print(f"barrier {int(b*100)}%: ki={r['ki']:4.1f}% fair={r['fair_bps']:6.1f}bps kiloss={r['ki_loss']:4.1f}")
print("\n== template length (ALL), fortnightly")
SL={}
for n_obs in [4,8,13,26]:
    ns=sum((run(s,n_obs=n_obs) for s in syms),[]); r=stats(ns); SL[n_obs]=r
    print(f"{n_obs:2} obs ({n_obs*2} wk): n={r['n']} ac={r['ac']:4.1f} ki={r['ki']:4.1f} cash={r['cash']:4.1f} fair={r['fair_bps']:6.1f} medwk={r['med_wk']}")
print("\n== fair coupon per stock at 60/65/70 barrier")
FB={}
for s in syms:
    FB[s]={b:stats(run(s,barrier=b))['fair_bps'] for b in [0.60,0.65,0.70]}
    print(s,{k:round(v,1) for k,v in FB[s].items()})
json.dump(dict(per_stock=R,barrier={str(k):v for k,v in SB.items()},length={str(k):v for k,v in SL.items()},fair_by_barrier={s:{str(k):v for k,v in d.items()} for s,d in FB.items()}),open("deep.json","w"),indent=1,default=str)
