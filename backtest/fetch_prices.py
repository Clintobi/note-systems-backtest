"""Download daily adjusted closes (splits + dividends) from Yahoo Finance's public chart endpoint.

The end date is pinned to 23 Sep 2026 so the published numbers reproduce exactly.
Output: prices.json  {symbol: [[YYYY-MM-DD, adj_close], ...]}
"""
import datetime as dt
import json
import urllib.request

SYMBOLS = ["NVDA", "TSLA", "AAPL", "MSFT", "AMZN", "META", "COIN", "HOOD"]
START = int(dt.datetime(2014, 1, 1, tzinfo=dt.timezone.utc).timestamp())
END = int(dt.datetime(2026, 9, 24, tzinfo=dt.timezone.utc).timestamp())

out = {}
for s in SYMBOLS:
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{s}"
           f"?period1={START}&period2={END}&interval=1d&events=div%2Csplit")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    r = json.load(urllib.request.urlopen(req, timeout=60))["chart"]["result"][0]
    adj = r["indicators"]["adjclose"][0]["adjclose"]
    out[s] = [(dt.datetime.fromtimestamp(t, dt.timezone.utc).date().isoformat(), a)
              for t, a in zip(r["timestamp"], adj) if a]
    print(s, len(out[s]), out[s][0][0], "->", out[s][-1][0])
json.dump(out, open("prices.json", "w"))
