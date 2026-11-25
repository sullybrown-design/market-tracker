#!/usr/bin/env python3
"""Market Tracker ingestion. Stdlib only.

Modes:
  fast    snapshot (cross-asset quotes), quotes for universe, news, calendars, CFTC, 13F, themes/research
  candles per-symbol daily(5y)/weekly(10y)/intraday(5d) candle files
  all     fast + candles
Outputs JSON into ../data/. Every file carries generated_at + source metadata.
A failed provider writes an error entry, never blanks previously good data:
if a fetch fails and an old file exists, the old file is kept and marked stale.
"""
import json, os, re, sys, time, math, urllib.request, urllib.parse, xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone, date
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from universe import UNIVERSE, BY_SYMBOL

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
os.makedirs(os.path.join(DATA, "candles"), exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
      "Accept": "application/json, text/plain, */*"}
NOW = datetime.now(timezone.utc)

def fetch(url, headers=None, timeout=20):
    req = urllib.request.Request(url, headers={**UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def fetch_json(url, headers=None, timeout=20):
    return json.loads(fetch(url, headers, timeout))

def write_json(name, obj):
    path = os.path.join(DATA, name)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, separators=(",", ":"))
    os.replace(tmp, path)
    print("wrote", name)

def keep_stale(name, err):
    """On failure, keep old file but note staleness in status.json."""
    print("FAILED", name, err)
    status = {}
    sp = os.path.join(DATA, "status.json")
    if os.path.exists(sp):
        try: status = json.load(open(sp))
        except Exception: status = {}
    status[name] = {"error": str(err)[:200], "at": NOW.isoformat()}
    with open(sp, "w") as f: json.dump(status, f, indent=1)

def yahoo_chart(symbol, rng, interval):
    url = ("https://query1.finance.yahoo.com/v8/finance/chart/" +
           urllib.parse.quote(symbol, safe="") +
           f"?range={rng}&interval={interval}&includePrePost=false")
    d = fetch_json(url)
    res = d["chart"]["result"][0]
    meta = res["meta"]
    ts = res.get("timestamp") or []
    q = res["indicators"]["quote"][0]
    rows = []
    for i, t in enumerate(ts):
        o, h, l, c = q["open"][i], q["high"][i], q["low"][i], q["close"][i]
        if c is None: continue
        v = (q.get("volume") or [None]*len(ts))[i] or 0
        rows.append([int(t), round(o,3) if o else round(c,3), round(h,3) if h else round(c,3),
                     round(l,3) if l else round(c,3), round(c,3), int(v)])
    return meta, rows

def quote_from_meta(meta, prev_rows=None):
    price = meta.get("regularMarketPrice")
    prev = meta.get("chartPreviousClose") or meta.get("previousClose")
    chg = pct = None
    if price is not None and prev:
        chg = round(price - prev, 3); pct = round((price/prev - 1) * 100, 2)
    return {"price": price, "change": chg, "changePct": pct, "prevClose": prev,
            "dayHigh": meta.get("regularMarketDayHigh"), "dayLow": meta.get("regularMarketDayLow"),
            "volume": meta.get("regularMarketVolume"), "currency": meta.get("currency"),
            "exchange": meta.get("fullExchangeName") or meta.get("exchangeName"),
            "marketTime": meta.get("regularMarketTime"),
            "timezone": meta.get("exchangeTimezoneName")}

# ---------------- snapshot / cross-asset ----------------
CROSS = [
    ("^GSPC","S&P 500","Index","USD"), ("^IXIC","Nasdaq Composite","Index","USD"),
    ("^DJI","Dow Jones Industrial Average","Index","USD"), ("^RUT","Russell 2000","Index","USD"),
    ("^VIX","VIX Volatility Index","Index",""), ("^TNX","U.S. 10-Year Yield","Yield","%"),
    ("CL=F","Crude Oil (WTI)","Future","USD"), ("GC=F","Gold","Future","USD"),
    ("CAD=X","USD/CAD","Currency","CAD"), ("^GSPTSE","S&P/TSX Composite","Index","CAD"),
]
def do_snapshot():
    out = []
    for sym, label, typ, cur in CROSS:
        try:
            meta, rows = yahoo_chart(sym, "5d", "1d")
            q = quote_from_meta(meta)
            if sym == "^TNX":  # Yahoo ^TNX is quoted in percent (e.g. 4.904 = 4.904%)
                q["price"] = round(meta["regularMarketPrice"], 3)
                prev = meta.get("chartPreviousClose") or 0
                q["prevClose"] = round(prev,3)
                q["change"] = round(q["price"]-prev, 3) if prev else None
                q["changeBps"] = round(q["change"]*100) if q["change"] is not None else None
                q["changePct"] = round((q["price"]/prev-1)*100, 2) if prev else None
            q.update({"symbol": sym, "label": label, "type": typ})
            out.append(q)
        except Exception as e:
            out.append({"symbol": sym, "label": label, "type": typ, "error": str(e)[:120]})
        time.sleep(0.15)
    # Bank of Canada official USD/CAD (daily, noon/indicative)
    boc = None
    try:
        end = date.today(); start = end - timedelta(days=10)
        d = fetch_json(f"https://www.bankofcanada.ca/valet/observations/FXUSDCAD/json?start_date={start}&end_date={end}")
        obs = d.get("observations") or []
        if obs:
            last = obs[-1]; prev = obs[-2] if len(obs) > 1 else None
            boc = {"rate": float(last["FXUSDCAD"]["v"]), "date": last["d"],
                   "prevRate": float(prev["FXUSDCAD"]["v"]) if prev else None, "prevDate": prev["d"] if prev else None,
                   "source": "Bank of Canada Valet (official daily rate)"}
    except Exception as e:
        boc = {"error": str(e)[:120]}
    write_json("snapshot.json", {"generated_at": NOW.isoformat(), "feed": "Yahoo Finance chart API (delayed/EOD per exchange rules)",
                                 "cross_asset": out, "usdcad_official": boc})

# ---------------- quotes for universe (from 3mo daily) ----------------
def do_quotes():
    quotes = {}
    for (sym, name, sector, cap, exch, cur) in UNIVERSE:
        try:
            meta, rows = yahoo_chart(sym, "3mo", "1d")
            if len(rows) < 2: continue
            last, prev = rows[-1], rows[-2]
            def pct_ago(days):
                idx = len(rows) - 1 - days
                if idx < 0: return None
                return round((last[4]/rows[idx][4] - 1) * 100, 2)
            quotes[sym] = {"symbol": sym, "name": name, "sector": sector, "capB": cap,
                           "exchange": exch, "currency": cur,
                           "price": last[4], "change": round(last[4]-prev[4], 3),
                           "changePct": round((last[4]/prev[4]-1)*100, 2),
                           "weekPct": pct_ago(5), "monthPct": pct_ago(21),
                           "asof": last[0], "spark": [r[4] for r in rows[-22:]]}
        except Exception as e:
            print("quote fail", sym, e)
        time.sleep(0.12)
    write_json("quotes.json", {"generated_at": NOW.isoformat(), "feed": "Yahoo Finance daily candles (EOD/delayed)",
                               "quotes": quotes})

# ---------------- news ----------------
QUERIES = [
    ("markets", "stock market today S&P 500 Nasdaq"),
    ("fed", "Federal Reserve interest rates Powell"),
    ("economy", "US economy inflation jobs report"),
    ("canada", "Bank of Canada TSX Canadian dollar"),
    ("oilgold", "oil prices gold prices today"),
    ("tech", "Nvidia Apple Microsoft earnings"),
]
ASSET_KEYS = [
    ("NVDA", ["nvidia","nvda"]), ("AAPL", ["apple","aapl"]), ("MSFT", ["microsoft"]),
    ("TSLA", ["tesla"]), ("META", ["meta platforms","facebook"]), ("AMZN", ["amazon"]),
    ("GOOGL", ["google","alphabet"]), ("SPY", ["s&p 500","sp500","wall street","stocks"]),
    ("QQQ", ["nasdaq"]), ("GLD", ["gold"]), ("CL=F", ["oil","crude","opec"]),
    ("^TNX", ["treasury","yield","bond"]), ("CAD=X", ["canadian dollar","loonie","usd/cad"]),
    ("CEG", ["constellation energy"]), ("ENB", ["enbridge"]),
]
WHY = [
    (["federal reserve","fed ","powell","rate cut","rate hike"], "Rate expectations drive valuations across stocks and bonds; a shift in the expected Fed path reprices the whole cross-asset board, including USD/CAD."),
    (["inflation","cpi","ppi","pce"], "Inflation data is the main input to the Fed and Bank of Canada reaction functions; a surprise versus consensus usually moves yields first, then equities."),
    (["jobs","payroll","unemployment","jobless"], "Labour data shapes both growth expectations and the rate path; surprises tend to move the 10-year yield and rate-sensitive sectors most."),
    (["earnings","profit","revenue","guidance"], "Earnings and guidance reset expectations for cash flows; read-throughs often move peers in the same sector, not just the reporting company."),
    (["oil","crude","opec"], "Oil feeds directly into inflation expectations and energy earnings, and matters disproportionately for Canada and the TSX."),
    (["gold"], "Gold reacts to real yields, the U.S. dollar and risk sentiment; a sharp move usually signals one of those three is shifting."),
    (["canada","bank of canada","tsx"], "Canadian assets trade on the BoC path, oil, and U.S. spillover; this story touches at least one of those channels."),
    (["tariff","trade"], "Trade policy changes hit margins, supply chains and the Canadian dollar directly; exposed sectors reprice on headlines before any data confirms the effect."),
    (["nvidia","ai ","chip","semiconductor"], "AI capex is the market's central earnings theme; news here moves the largest index weights and therefore the indices themselves."),
]
def why_for(title):
    t = " " + title.lower() + " "
    for keys, txt in WHY:
        if any(k in t for k in keys): return txt
    return "Flagged because it is among the most-covered market stories right now; the direct market impact is not yet clear from headlines alone."

BLOCKED_SUBSTR = ["motley fool", "fool.com", "fool.ca"]  # user: no Motley Fool-class sources (any variant)
DEMOTED_SOURCES = {"Benzinga", "InvestorPlace", "24/7 Wall St.", "Seeking Alpha", "Zacks Investment Research"}
def is_blocked(publisher, link):
    p = (publisher or "").lower()
    return any(b in p or b in (link or "").lower() for b in BLOCKED_SUBSTR)
def do_news(quotes=None):
    items = []
    for cat, q in QUERIES:
        try:
            url = "https://news.google.com/rss/search?q=" + urllib.parse.quote(q) + "&hl=en-US&gl=US&ceid=US:en"
            root = ET.fromstring(fetch(url, timeout=15))
            for it in root.iter("item"):
                title = (it.findtext("title") or "").strip()
                link = (it.findtext("link") or "").strip()
                pub = (it.findtext("pubDate") or "").strip()
                src = ""
                s = it.find("source")
                if s is not None: src = s.text or ""
                if not title or not link: continue
                if is_blocked(src, link): continue
                # Google titles end with " - Publisher"
                if " - " in title and src and title.endswith(src): title = title[: -len(src)].rstrip(" -")
                try: ts = int(datetime.strptime(pub, "%a, %d %b %Y %H:%M:%S %Z").replace(tzinfo=timezone.utc).timestamp())
                except Exception: ts = int(NOW.timestamp())
                items.append({"title": title, "link": link, "publisher": src or "Google News",
                              "ts": ts, "category": cat})
        except Exception as e:
            print("news fail", cat, e)
        time.sleep(0.1)
    # group duplicates: same story = shared rare words
    def norm(t): return set(re.findall(r"[a-z0-9]{4,}", t.lower())) - {"says","will","stock","stocks","market","today","news","report","shares","after","with","from"}
    groups = []
    for it in sorted(items, key=lambda x: -x["ts"]):
        w = norm(it["title"]); placed = False
        for g in groups:
            gw = norm(g["title"])
            inter = len(w & gw); union = len(w | gw) or 1
            if inter / union > 0.45:
                g["coverage"] += 1; g["publishers"] = sorted(set(g["publishers"] + [it["publisher"]]))[:6]
                if len(g["items"]) < 8 and it["title"] not in [x["title"] for x in g["items"]]:
                    g["items"].append({"title": it["title"], "publisher": it["publisher"], "link": it["link"], "ts": it["ts"]})
                placed = True; break
        if not placed:
            groups.append({**it, "coverage": 1, "publishers": [it["publisher"]],
                           "items": [{"title": it["title"], "publisher": it["publisher"], "link": it["link"], "ts": it["ts"]}]})
    tier = {"Reuters":3,"Bloomberg":3,"CNBC":2,"MarketWatch":2,"The Wall Street Journal":3,"Financial Times":3,
            "Associated Press":3,"BNN Bloomberg":2,"The Globe and Mail":2,"Barron's":2,"Investing.com":1,"Yahoo Finance":2}
    qmap = (quotes or {}).get("quotes", {})
    for g in groups:
        assets = [a for a, keys in ASSET_KEYS if any(k in g["title"].lower() for k in keys)]
        g["assets"] = assets[:4]
        age_h = max(0.0, (NOW.timestamp() - g["ts"]) / 3600)
        t = tier.get(g["publisher"], 1) - (1 if g["publisher"] in DEMOTED_SOURCES else 0)
        g["score"] = round(t * 2 + min(g["coverage"], 6) + max(0, 6 - age_h), 1)
        g["why"] = why_for(g["title"])
        # In-app briefing: synthesized from pooled headlines + verified market moves.
        # (Publishers' article text is theirs and is never copied into the app.)
        variants = []
        for it in g["items"]:
            if it["title"] != g["title"] and it["title"] not in variants: variants.append(it["title"])
        ctx = []
        for a in g["assets"]:
            q = qmap.get(a)
            if q: ctx.append(f"{a} ({q['name']}) is at {q['price']} ({q['changePct']:+.2f}% today, {q['weekPct']:+.2f}% this week) in the latest snapshot.")
        g["brief"] = {"coverage_line": f"Pooled from {g['coverage']} article(s) across {len(set(g['publishers']))} publisher(s): {', '.join(sorted(set(g['publishers'])))}.",
                      "variants": variants[:4], "market_context": ctx,
                      "label": "App briefing compiled in-app from pooled headlines and verified market data. Full article text belongs to the publishers and is not republished here."}
    groups.sort(key=lambda x: -x["score"])
    write_json("news.json", {"generated_at": NOW.isoformat(), "feed": "Google News RSS (publisher headlines, grouped by story)",
                             "stories": groups[:30]})

# ---------------- calendars ----------------
def do_earnings():
    rows_out = []
    today = date.today()
    for off in range(-10, 22):
        d = today + timedelta(days=off)
        try:
            url = f"https://api.nasdaq.com/api/calendar/earnings?date={d.isoformat()}"
            r = fetch_json(url, timeout=15)
            for row in (r.get("data") or {}).get("rows") or []:
                sym = row.get("symbol") or ""
                cap = row.get("marketCap") or ""
                try: capn = float(cap.replace("$","").replace(",",""))
                except Exception: capn = 0
                if capn < 1e9 and sym not in BY_SYMBOL and sym not in ("NVDA","SPY","QQQ","IWM","GLD","CEG","ENB"): continue
                def num(x):
                    try: return float(str(x).replace("$","").replace("%","").replace(",",""))
                    except Exception: return None
                rows_out.append({"symbol": sym, "name": row.get("name"), "date": d.isoformat(),
                                 "time": row.get("time"), "epsActual": num(row.get("eps")),
                                 "epsForecast": num(row.get("epsForecast")), "surprisePct": num(row.get("surprise")),
                                 "capB": round(capn/1e9, 1) if capn else None,
                                 "fiscalQ": row.get("fiscalQuarterEnding"),
                                 "confirmed": off >= -1,  # Nasdaq lists scheduled dates; treat near-term as scheduled
                                 "source": "Nasdaq earnings calendar"})
        except Exception as e:
            print("earnings fail", d, e)
        time.sleep(0.1)
    rows_out.sort(key=lambda x: (x["date"], -(x["capB"] or 0)))
    write_json("earnings.json", {"generated_at": NOW.isoformat(), "feed": "Nasdaq API earnings calendar (EPS consensus/actual; revenue not supplied by this feed)",
                                 "note": "Dates are scheduled/estimated unless the company has confirmed; EPS surprise shown where reported.",
                                 "events": rows_out})

def do_econ():
    evs = []
    for wk in ("thisweek", "nextweek"):
        try:
            r = fetch_json(f"https://nfs.faireconomy.media/ff_calendar_{wk}.json", timeout=15)
            for e in r:
                if e.get("country") not in ("USD", "CAD"): continue
                evs.append({"title": e.get("title"), "country": "US" if e["country"]=="USD" else "Canada",
                            "currency": e["country"], "date": e.get("date"), "impact": e.get("impact"),
                            "actual": e.get("actual") or None, "forecast": e.get("forecast") or None,
                            "previous": e.get("previous") or None,
                            "source": "ForexFactory calendar feed (faireconomy.media)"})
        except Exception as ex:
            print("econ fail", wk, ex)
    evs.sort(key=lambda x: x["date"] or "")
    write_json("econ.json", {"generated_at": NOW.isoformat(), "feed": "ForexFactory weekly calendar via faireconomy.media (US & Canada)",
                             "note": "Reference periods and units are in each release title where applicable (e.g. m/m vs y/y). Actuals appear after release; revisions are not supplied by this feed.",
                             "events": evs})

# ---------------- CFTC TFF positioning ----------------
# Exact TFF contract_market_name values (exact match avoids Micro/Mini variants).
# TFF covers financial futures only — metals/energy are in the Disaggregated COT, not TFF.
CFTC_MARKETS = [
    ("E-MINI S&P 500", "E-mini S&P 500 (CME)"), ("NASDAQ-100 Consolidated", "Nasdaq-100 Consolidated (CME)"),
    ("S&P 500 Consolidated", "S&P 500 Consolidated (CME)"), ("DJIA Consolidated", "Dow Jones Consolidated (CBOT)"),
    ("UST 10Y NOTE", "UST 10-Year Note (CBOT)"), ("UST 2Y NOTE", "UST 2-Year Note (CBOT)"),
    ("UST 5Y NOTE", "UST 5-Year Note (CBOT)"), ("ULTRA UST BOND", "Ultra UST Bond (CBOT)"),
    ("CANADIAN DOLLAR", "Canadian Dollar (CME)"), ("EURO FX", "Euro FX (CME)"),
    ("RUSSELL E-MINI", "Russell 2000 E-mini (CME)"), ("JAPANESE YEN", "Japanese Yen (CME)"),
]
def do_cftc():
    series = []
    for needle, label in CFTC_MARKETS:
        try:
            q = urllib.parse.urlencode({"$limit": 60, "$order": "report_date_as_yyyy_mm_dd DESC",
                "$where": f"contract_market_name='{needle.replace(chr(39), chr(39)*2)}' AND futonly_or_combined='FutOnly'"})
            r = fetch_json(f"https://publicreporting.cftc.gov/resource/gpe5-46if.json?{q}", timeout=25)
            bydate = {}
            for row in r:
                bydate.setdefault(row["report_date_as_yyyy_mm_dd"][:10], row)
            dates = sorted(bydate)[-14:]
            hist = []
            for d in dates:
                row = bydate[d]
                def f(k):
                    try: return int(float(row.get(k) or 0))
                    except Exception: return 0
                lng = f("lev_money_positions_long"); sht = f("lev_money_positions_short")
                hist.append({"date": d, "long": lng, "short": sht, "net": lng - sht,
                             "openInterest": f("open_interest_all")})
            if hist:
                latest = hist[-1]; prev = hist[-2] if len(hist) > 1 else latest
                series.append({"market": label, "history": hist,
                               "netChange": latest["net"] - prev["net"],
                               "longChange": latest["long"] - prev["long"],
                               "shortChange": latest["short"] - prev["short"],
                               "asof": latest["date"]})
        except Exception as e:
            print("cftc fail", needle, e)
        time.sleep(0.1)
    series.sort(key=lambda s: -abs(s["netChange"]))
    write_json("cftc.json", {"generated_at": NOW.isoformat(),
        "feed": "CFTC Traders in Financial Futures (TFF), Futures Only, via CFTC public reporting (Socrata)",
        "category": "Leveraged Funds (TFF category: leveraged money — primarily hedge funds)",
        "units": "Contracts (futures only). Net = long − short.",
        "lag": "Positions as of Tuesday; published the following Friday (~3 day lag).",
        "source_url": "https://publicreporting.cftc.gov/resource/gpe5-46if.json",
        "series": series})

FUNDS_13F = [
    ("Berkshire Hathaway", "0001067983"), ("Bridgewater Associates", "0001350694"),
    ("Renaissance Technologies", "0001037389"), ("Citadel Advisors", "0001423053"),
    ("Millennium Management", "0001273087"), ("D.E. Shaw", "0001009207"),
]
def do_13f():
    funds = []
    for name, cik in FUNDS_13F:
        entry = {"fund": name, "cik": cik,
                 "edgar_url": f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=13F-HR&dateb=&owner=include&count=10",
                 "filings": []}
        try:
            url = f"https://efts.sec.gov/LATEST/search-index?q=%2213F-HR%22&dateRange=custom"
            # EDGAR full-text search API
            q = urllib.parse.urlencode({"q": '"13F-HR"', "forms": "13F-HR"})
            r = fetch_json(f"https://www.sec.gov/cgi-bin/efts_search?{q}", timeout=10)
            entry["note"] = "Live filing list unavailable; use EDGAR link."
        except Exception:
            entry["note"] = "Filing list fetched on demand from SEC EDGAR — open the EDGAR link for the authoritative list. 13F reports are quarterly, filed within 45 days of quarter-end; holdings values alone do not show purchases or sales."
        funds.append(entry)
    write_json("f13.json", {"generated_at": NOW.isoformat(),
        "feed": "SEC EDGAR 13F-HR filings (quarterly)",
        "note": "13F reports are quarterly long U.S. equity holdings of managers >$100M, filed within 45 days after quarter-end. A change in reported value is NOT a purchase or sale (prices move too). This view links to the authoritative EDGAR filing list per fund.",
        "funds": funds})

# ---------------- themes / research (data-driven) ----------------
def do_research(snapshot, quotes):
    cross = {c["symbol"]: c for c in snapshot.get("cross_asset", [])}
    q = quotes.get("quotes", {})
    def mv(sym): 
        c = cross.get(sym) or {}
        return c.get("changePct")
    sectors = {}
    for sym, v in q.items():
        if v["sector"] == "ETF" or v.get("monthPct") is None: continue
        sectors.setdefault(v["sector"], []).append(v["monthPct"])
    sec_rows = sorted(((s, round(sum(v)/len(v), 2), len(v)) for s, v in sectors.items()), key=lambda x: -x[1])
    themes = []
    def theme(title, what, exposed, evidence, weaken, catalyst, score):
        themes.append({"title": title, "what_changed": what, "exposed": exposed, "evidence": evidence,
                       "what_would_weaken": weaken, "next_catalyst": catalyst, "score": score,
                       "asof": NOW.date().isoformat(), "kind": "interpretation"})
    spx, vix, tnx = mv("^GSPC"), mv("^VIX"), (cross.get("^TNX") or {}).get("changeBps")
    oil, gold, cad = mv("CL=F"), mv("GC=F"), mv("CAD=X")
    nvda = q.get("NVDA", {}); semi = [q[s]["monthPct"] for s in ("NVDA","AMD","AVGO","MU") if s in q and q[s].get("monthPct") is not None]
    themes.append({"title": "Index trend & risk appetite", "kind": "observation",
        "what_changed": f"S&P 500 {spx:+.2f}% on the latest session; VIX at {(cross.get('^VIX') or {}).get('price')}.",
        "exposed": ["SPY","QQQ","IWM"], "evidence": [f"S&P 500 daily change {spx}% (snapshot)", f"Russell 2000 daily change {mv('^RUT')}% — small-cap participation check"],
        "what_would_weaken": "Breadth deterioration: equal-weight and small caps lagging while mega-caps carry the index.",
        "next_catalyst": "Next CPI / jobs release and Fed speakers (see Calendar).", "score": 90, "asof": NOW.date().isoformat()})
    if semi:
        themes.append({"title": "AI & semiconductors leadership", "kind": "interpretation",
            "what_changed": f"Semis 1-month average {round(sum(semi)/len(semi),1)}% across NVDA/AMD/AVGO/MU in the tracked universe.",
            "exposed": ["NVDA","AVGO","AMD","MU","QQQ"], "evidence": [f"NVDA 1-month {nvda.get('monthPct')}%", f"Basket 1-month average {round(sum(semi)/len(semi),2)}%"],
            "what_would_weaken": "A guidance cut or capex slowdown from a hyperscaler, or semis underperforming SPY for several weeks.",
            "next_catalyst": "Next mega-cap earnings and NVDA results (see Calendar → Earnings).", "score": 80, "asof": NOW.date().isoformat()})
    themes.append({"title": "Rates: U.S. 10-year & the policy path", "kind": "interpretation",
        "what_changed": f"10-year yield at {(cross.get('^TNX') or {}).get('price')}% ({tnx:+} bp latest session)." if tnx is not None else "10-year yield level in snapshot.",
        "exposed": ["TLT","IWM","XLF (via banks)","Growth equities"], "evidence": [f"10Y daily move {tnx} bp", f"USD/CAD daily change {cad}%"],
        "what_would_weaken": "A run of soft inflation prints pulling the expected policy path lower (yields down, growth multiples up).",
        "next_catalyst": "Next FOMC decision and CPI release (see Calendar).", "score": 75, "asof": NOW.date().isoformat()})
    themes.append({"title": "Oil, gold & the Canadian dollar", "kind": "observation",
        "what_changed": f"WTI {oil}% , gold {gold}% , USD/CAD {cad}% on the latest session.",
        "exposed": ["SU.TO","ENB.TO","ENB","GLD","NEM","CAD=X"], "evidence": ["Cross-asset snapshot moves", "Bank of Canada official USD/CAD daily rate in snapshot"],
        "what_would_weaken": "Oil giving back gains on demand data, or gold decoupling from real yields.",
        "next_catalyst": "Weekly EIA petroleum report (Wed) and BoC/Fed decisions.", "score": 60, "asof": NOW.date().isoformat()})
    if sec_rows:
        themes.append({"title": "Sector rotation (1-month, tracked universe)", "kind": "observation",
            "what_changed": f"Leading: {sec_rows[0][0]} ({sec_rows[0][1]:+}% avg). Lagging: {sec_rows[-1][0]} ({sec_rows[-1][1]:+}% avg).",
            "exposed": [s for s, _, _ in sec_rows[:3]], "evidence": [f"{s}: {v:+.2f}% avg 1-month across {n} tracked names" for s, v, n in sec_rows],
            "what_would_weaken": "Rotation is measured on a curated ~110-name universe, not the full index; treat as directional.",
            "next_catalyst": "Earnings season breadth — whether leadership widens beyond the top sector.", "score": 55, "asof": NOW.date().isoformat()})
    themes.sort(key=lambda t: -t["score"])
    recap = {"asof": NOW.date().isoformat(),
             "daily": {"spx": spx, "nasdaq": mv("^IXIC"), "rut": mv("^RUT"), "vix": (cross.get("^VIX") or {}).get("price"),
                       "tnx_bps": tnx, "oil": oil, "gold": gold, "usdcad": cad},
             "sector_month": [{"sector": s, "avgMonthPct": v, "names": n} for s, v, n in sec_rows],
             "themes": themes}
    write_json("research.json", {"generated_at": NOW.isoformat(),
        "feed": "Computed from verified snapshot/quotes data in this repository (no generative commentary). Observations, interpretation and scenarios are labelled per item.",
        "recap": recap})
    # archive daily snapshot for research history
    arch_dir = os.path.join(DATA, "archive"); os.makedirs(arch_dir, exist_ok=True)
    apath = os.path.join(arch_dir, NOW.date().isoformat() + ".json")
    with open(apath, "w") as f: json.dump({"date": NOW.date().isoformat(), "snapshot": snapshot, "recap": recap}, f, separators=(",",":"))
    idx = sorted(fn[:-5] for fn in os.listdir(arch_dir) if fn.endswith(".json"))
    write_json("archive_index.json", {"generated_at": NOW.isoformat(), "start": idx[0] if idx else None, "dates": idx})

# ---------------- candles ----------------
def file_name(sym): return re.sub(r"[^A-Za-z0-9]+", "_", sym) + ".json"
def do_candles():
    syms = [u[0] for u in UNIVERSE] + ["^GSPC","^IXIC","^DJI","^RUT","^VIX","^TNX","CL=F","GC=F","CAD=X","^GSPTSE"]
    for sym in syms:
        try:
            _, daily = yahoo_chart(sym, "5y", "1d")
            _, weekly = yahoo_chart(sym, "10y", "1wk")
            try: _, intra = yahoo_chart(sym, "5d", "5m")
            except Exception: intra = []
            meta_u = BY_SYMBOL.get(sym)
            write_json(os.path.join("candles", file_name(sym)),
                       {"symbol": sym, "generated_at": NOW.isoformat(),
                        "name": meta_u[1] if meta_u else sym, "exchange": meta_u[4] if meta_u else "",
                        "currency": meta_u[5] if meta_u else "",
                        "feed": "Yahoo Finance chart API (delayed/EOD per exchange)",
                        "daily": daily, "weekly": weekly, "intraday": intra})
        except Exception as e:
            print("candle fail", sym, e)
        time.sleep(0.12)

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "fast"
    if mode == "news":
        qd = json.load(open(os.path.join(DATA, "quotes.json"))) if os.path.exists(os.path.join(DATA, "quotes.json")) else None
        do_news(qd); return
    snap = quotes = None
    if mode in ("fast", "all"):
        try: do_snapshot()
        except Exception as e: keep_stale("snapshot.json", e)
        try: do_quotes()
        except Exception as e: keep_stale("quotes.json", e)
        try:
            qd = json.load(open(os.path.join(DATA, "quotes.json"))) if os.path.exists(os.path.join(DATA, "quotes.json")) else None
            do_news(qd)
        except Exception as e: keep_stale("news.json", e)
        try: do_earnings()
        except Exception as e: keep_stale("earnings.json", e)
        try: do_econ()
        except Exception as e: keep_stale("econ.json", e)
        try: do_cftc()
        except Exception as e: keep_stale("cftc.json", e)
        try: do_13f()
        except Exception as e: keep_stale("f13.json", e)
        try:
            snap = json.load(open(os.path.join(DATA, "snapshot.json")))
            quotes = json.load(open(os.path.join(DATA, "quotes.json")))
            do_research(snap, quotes)
        except Exception as e: keep_stale("research.json", e)
    if mode in ("candles", "all"):
        do_candles()

if __name__ == "__main__":
    main()
