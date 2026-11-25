# Sully's TradingView "Red List 1.0", transcribed from his screenshots 2026-11-25.
# Each item: (TradingView label, Yahoo symbol, name, exchange, currency).
# Yahoo symbols were verified against the chart API on 2026-11-25 (168/173 OK).
REDLIST = [
 ("Indices & futures", [
  ("SPX","^GSPC","S&P 500 Index","CBOE","USD"),("NDQ","^NDX","Nasdaq 100 Index","CBOE","USD"),
  ("DJI","^DJI","Dow Jones Industrial Average","CBOE","USD"),("RUT","^RUT","Russell 2000 Index","CBOE","USD"),
  ("ES1!","ES=F","S&P 500 E-mini Futures","CME","USD"),("NQ1!","NQ=F","Nasdaq 100 E-mini Futures","CME","USD"),
  ("RTY1!","RTY=F","Russell 2000 E-mini Futures","CME","USD"),("DJIA1!","YM=F","Dow E-mini Futures","CBOT","USD"),
  ("HSI","^HSI","Hang Seng Index","HKEX","HKD"),("NIKKEI","^N225","Nikkei 225","OSE","JPY"),
  ("KOSPI","^KS11","KOSPI Composite Index","KRX","KRW"),
 ]),
 ("Volatility & dollar", [
  ("VIX","^VIX","Volatility S&P 500 Index","CBOE","USD"),("UVXY","UVXY","ProShares Ultra VIX Short-Term Futures ETF","NYSEArca","USD"),
  ("VIXY","VIXY","ProShares VIX Short-Term Futures ETF","NYSEArca","USD"),("SVIX","SVIX","-1x Short VIX Futures ETF","NYSEArca","USD"),
  ("DXY","DX-Y.NYB","U.S. Dollar Currency Index","ICE","USD"),
 ]),
 ("Rates & bonds", [
  ("US10Y","^TNX","US 10Y Yield (%)","CBOE","%"),("US30Y","^TYX","US 30Y Yield (%)","CBOE","%"),
  ("US05Y","^FVX","US 5Y Yield (%)","CBOE","%"),("US30","ZB=F","US 30Y T-Bond Futures","CBOT","USD"),
  ("TLT","TLT","iShares 20+ Year Treasury Bond ETF","NASDAQ","USD"),
 ]),
 ("Energy & commodities", [
  ("BRN1!","BZ=F","Brent Crude Futures","ICE","USD"),("OILUSD","CL=F","WTI Crude Futures","NYMEX","USD"),
  ("GC1!","GC=F","Gold Futures","COMEX","USD"),("SILVER","SI=F","Silver Futures (TV: spot CFD)","COMEX","USD"),
  ("WEAT","WEAT","Teucrium Wheat Fund","NYSEArca","USD"),("CORN","CORN","Teucrium Corn Fund","NYSEArca","USD"),
  ("OXY","OXY","Occidental Petroleum","NYSE","USD"),("OIL","OIL.NS","Oil India Limited","NSE","INR"),
 ]),
 ("FX", [
  ("CADUSD","CADUSD=X","Canadian Dollar / U.S. Dollar","FX","USD"),("EURUSD","EURUSD=X","Euro / U.S. Dollar","FX","USD"),
  ("USDJPY","JPY=X","U.S. Dollar / Japanese Yen","FX","JPY"),("USDCAD","CAD=X","U.S. Dollar / Canadian Dollar","FX","CAD"),
  ("NZDUSD","NZDUSD=X","New Zealand Dollar / U.S. Dollar","FX","USD"),
 ]),
 ("Index & leveraged ETFs", [
  ("SPY","SPY","SPDR S&P 500 ETF Trust","NYSEArca","USD"),("QQQ","QQQ","Invesco QQQ Trust","NASDAQ","USD"),
  ("IWM","IWM","iShares Russell 2000 ETF","NYSEArca","USD"),("RSP","RSP","Invesco S&P 500 Equal Weight ETF","NYSEArca","USD"),
  ("SMH","SMH","VanEck Semiconductor ETF","NASDAQ","USD"),("XLE","XLE","Energy Select Sector SPDR","NYSEArca","USD"),
  ("GLD","GLD","SPDR Gold Shares","NYSEArca","USD"),("GBTC","GBTC","Grayscale Bitcoin Trust","NYSEArca","USD"),
  ("SPXL","SPXL","Direxion Daily S&P 500 Bull 3X","NYSEArca","USD"),("TQQQ","TQQQ","ProShares UltraPro QQQ","NASDAQ","USD"),
  ("SQQQ","SQQQ","ProShares UltraPro Short QQQ","NASDAQ","USD"),("SARK","SARK","Tradr 1X Short Innovation Daily ETF","NASDAQ","USD"),
  ("ARKK","ARKK","ARK Innovation ETF","NYSEArca","USD"),("ARKX","ARKX","ARK Space & Defense Innovation ETF","NYSEArca","USD"),
  ("VFV","VFV.TO","Vanguard S&P 500 Index ETF","TSX","CAD"),("ZQQ","ZQQ.TO","BMO Nasdaq 100 Equity Hedged ETF","TSX","CAD"),
  ("ETHY.B","ETHY.TO","Purpose Ether Yield ETF","TSX","CAD"),
 ]),
 ("Mega-cap tech", [
  ("AAPL","AAPL","Apple","NASDAQ","USD"),("MSFT","MSFT","Microsoft","NASDAQ","USD"),
  ("NVDA","NVDA","NVIDIA","NASDAQ","USD"),("AMZN","AMZN","Amazon","NASDAQ","USD"),
  ("GOOG","GOOG","Alphabet Class C","NASDAQ","USD"),("GOOGL","GOOGL","Alphabet Class A","NASDAQ","USD"),
  ("META","META","Meta Platforms","NASDAQ","USD"),("TSLA","TSLA","Tesla","NASDAQ","USD"),
  ("AVGO","AVGO","Broadcom","NASDAQ","USD"),("ORCL","ORCL","Oracle","NYSE","USD"),
 ]),
 ("Semiconductors", [
  ("AMD","AMD","Advanced Micro Devices","NASDAQ","USD"),("TSM","TSM","Taiwan Semiconductor (ADR)","NYSE","USD"),
  ("MRVL","MRVL","Marvell Technology","NASDAQ","USD"),("MU","MU","Micron Technology","NASDAQ","USD"),
  ("INTC","INTC","Intel","NASDAQ","USD"),("QCOM","QCOM","Qualcomm","NASDAQ","USD"),
  ("ARM","ARM","Arm Holdings (ADR)","NASDAQ","USD"),("LRCX","LRCX","Lam Research","NASDAQ","USD"),
  ("TER","TER","Teradyne","NASDAQ","USD"),("SKHY","000660.KS","SK hynix","KRX","KRW"),
 ]),
 ("Software, AI & cybersecurity", [
  ("APP","APP","AppLovin","NASDAQ","USD"),("SMCI","SMCI","Super Micro Computer","NASDAQ","USD"),
  ("ADBE","ADBE","Adobe","NASDAQ","USD"),("CRM","CRM","Salesforce","NYSE","USD"),
  ("NOW","NOW","ServiceNow","NYSE","USD"),("WDAY","WDAY","Workday","NASDAQ","USD"),
  ("DDOG","DDOG","Datadog","NASDAQ","USD"),("GTLB","GTLB","GitLab","NASDAQ","USD"),
  ("SNOW","SNOW","Snowflake","NYSE","USD"),("PLTR","PLTR","Palantir Technologies","NASDAQ","USD"),
  ("POET","POET","POET Technologies","NASDAQ","USD"),("OKTA","OKTA","Okta","NASDAQ","USD"),
  ("FTNT","FTNT","Fortinet","NASDAQ","USD"),("CRWD","CRWD","CrowdStrike","NASDAQ","USD"),
  ("PANW","PANW","Palo Alto Networks","NASDAQ","USD"),("S","S","SentinelOne","NYSE","USD"),
 ]),
 ("Fintech & financials", [
  ("NU","NU","Nu Holdings","NYSE","USD"),("SOFI","SOFI","SoFi Technologies","NASDAQ","USD"),
  ("AFRM","AFRM","Affirm Holdings","NASDAQ","USD"),("COIN","COIN","Coinbase Global","NASDAQ","USD"),
  ("BX","BX","Blackstone","NYSE","USD"),("V","V","Visa","NYSE","USD"),
  ("GS","GS","Goldman Sachs","NYSE","USD"),("BAC","BAC","Bank of America","NYSE","USD"),
  ("JPM","JPM","JPMorgan Chase","NYSE","USD"),("GSY","GSY.TO","goeasy Ltd.","TSX","CAD"),
 ]),
 ("Crypto & crypto-linked", [
  ("BTCUSDT","BTC-USD","Bitcoin / USD","Crypto","USD"),("ETHUSDT","ETH-USD","Ethereum / USD","Crypto","USD"),
  ("XRPUSDT","XRP-USD","XRP / USD","Crypto","USD"),("DOGEUSD","DOGE-USD","Dogecoin / USD","Crypto","USD"),
  ("LTCUSDT.P","LTC-USD","Litecoin / USD","Crypto","USD"),("KASUSDT","KAS-USD","Kaspa / USD","Crypto","USD"),
  ("AXSUSDT","AXS-USD","Axie Infinity / USD","Crypto","USD"),("PYRUSDT","PYR-USD","Vulcan Forged PYR / USD","Crypto","USD"),
  ("SOLBTC","SOL-BTC","Solana / Bitcoin","Crypto","BTC"),("USDTUSD","USDT-USD","Tether / USD","Crypto","USD"),
  ("USDDUSDT","USDD-USD","USDD / USD","Crypto","USD"),
  ("MARA","MARA","MARA Holdings","NASDAQ","USD"),("RIOT","RIOT","Riot Platforms","NASDAQ","USD"),
  ("CLSK","CLSK","CleanSpark","NASDAQ","USD"),("HUT","HUT","Hut 8","NASDAQ","USD"),
  ("BTBT","BTBT","Bit Digital","NASDAQ","USD"),("ARBK","ARBK","Argo Blockchain (NASDAQ)","NASDAQ","USD"),
 ]),
 ("Power & energy transition", [
  ("CEG","CEG","Constellation Energy","NASDAQ","USD"),("NRG","NRG","NRG Energy","NYSE","USD"),
  ("VST","VST","Vistra","NYSE","USD"),("OKLO","OKLO","Oklo","NYSE","USD"),
 ]),
 ("Industrials & transport", [
  ("ETN","ETN","Eaton Corporation","NYSE","USD"),("TT","TT","Trane Technologies","NYSE","USD"),
  ("NOVT","NOVT","Novanta","NASDAQ","USD"),("MOG.A","MOG-A","Moog Inc. Class A","NYSE","USD"),
  ("HWM","HWM","Howmet Aerospace","NYSE","USD"),("STLD","STLD","Steel Dynamics","NASDAQ","USD"),
  ("NUE","NUE","Nucor","NYSE","USD"),("CHRW","CHRW","C.H. Robinson","NASDAQ","USD"),
  ("LSTR","LSTR","Landstar System","NASDAQ","USD"),("UAL","UAL","United Airlines","NASDAQ","USD"),
  ("BLDR","BLDR","Builders FirstSource","NYSE","USD"),("ADNT","ADNT","Adient","NYSE","USD"),
  ("CTAS","CTAS","Cintas","NASDAQ","USD"),("F","F","Ford Motor","NYSE","USD"),
  ("RCL","RCL","Royal Caribbean Cruises","NYSE","USD"),
 ]),
 ("Health & biotech", [
  ("GILD","GILD","Gilead Sciences","NASDAQ","USD"),("LLY","LLY","Eli Lilly","NYSE","USD"),
  ("UNH","UNH","UnitedHealth Group","NYSE","USD"),("PFE","PFE","Pfizer","NYSE","USD"),
  ("VBIO","VBIO","Valion Bio","OTC","USD"),("RKV","RKV.V","Rakovina Therapeutics","TSXV","CAD"),
 ]),
 ("Consumer, media & speculative", [
  ("EBAY","EBAY","eBay","NASDAQ","USD"),("COST","COST","Costco","NASDAQ","USD"),
  ("HD","HD","Home Depot","NYSE","USD"),("TGT","TGT","Target","NYSE","USD"),
  ("DIS","DIS","Walt Disney","NYSE","USD"),("SBUX","SBUX","Starbucks","NASDAQ","USD"),
  ("MCD","MCD","McDonald's","NYSE","USD"),("NKE","NKE","Nike","NYSE","USD"),
  ("EL","EL","Estée Lauder","NYSE","USD"),("ELF","ELF","e.l.f. Beauty","NYSE","USD"),
  ("CELH","CELH","Celsius Holdings","NASDAQ","USD"),("BRBR","BRBR","BellRing Brands","NYSE","USD"),
  ("CHWY","CHWY","Chewy","NYSE","USD"),("DKNG","DKNG","DraftKings","NASDAQ","USD"),
  ("AMC","AMC","AMC Entertainment","NYSE","USD"),("GME","GME","GameStop","NYSE","USD"),
  ("PTON","PTON","Peloton Interactive","NASDAQ","USD"),("CVNA","CVNA","Carvana","NYSE","USD"),
  ("UBER","UBER","Uber Technologies","NYSE","USD"),("WDFC","WDFC","WD-40 Company","NASDAQ","USD"),
  ("NOK","NOK","Nokia (ADR)","NYSE","USD"),("RDDT","RDDT","Reddit","NYSE","USD"),
  ("PINS","PINS","Pinterest","NYSE","USD"),("SNAP","SNAP","Snap Inc.","NYSE","USD"),
  ("DJT","DJT","Trump Media & Technology","NASDAQ","USD"),("TLRY","TLRY","Tilray Brands","NASDAQ","USD"),
  ("NIO","NIO","NIO Inc. (ADR)","NYSE","USD"),("RIVN","RIVN","Rivian Automotive","NASDAQ","USD"),
  ("SERV","SERV","Serve Robotics","NASDAQ","USD"),("AUR","AUR","Aurora Innovation","NASDAQ","USD"),
  ("QUBT","QUBT","Quantum Computing Inc.","NASDAQ","USD"),("ASTS","ASTS","AST SpaceMobile","NASDAQ","USD"),
  ("SOUN","SOUN","SoundHound AI","NASDAQ","USD"),("CRNC","CRNC","Cerence","NASDAQ","USD"),
  ("KEEL","KEEL","Keel Infrastructure","NASDAQ","USD"),("WKSP","WKSP","Worksport","NASDAQ","USD"),
  ("RUM","RUM","Rumble (RUM Group)","NASDAQ","USD"),
 ]),
]
# On his list but with no usable Yahoo Finance feed (verified 2026-11-25) — shown greyed in the app.
UNAVAILABLE = [
 ("BTC.D","Bitcoin dominance % — a TradingView stat, no Yahoo feed"),
 ("BTCUSD/NVDA","Custom spread — not a tradable symbol"),
 ("BLX/NVDA","Custom spread — not a tradable symbol"),
 ("SPCX","SpaceX — not publicly traded"),
 ("US01Y / US03Y","1Y and 3Y yields — no clean Yahoo yield feed (5Y/10Y/30Y are covered)"),
 ("CSCP","CIBC Sustainable Canadian ETF — no Yahoo feed found"),
 ("IMXUSDT","Immutable — no Yahoo crypto feed found"),
 ("OIL1! / ESM2026 / USDEUR","Duplicates of the Brent / S&P futures / EURUSD entries already listed"),
]
def all_symbols():
    seen, out = set(), []
    for _cat, items in REDLIST:
        for _tv, sym, _n, _e, _c in items:
            if sym not in seen: seen.add(sym); out.append(sym)
    return out
META = {}
for _cat, _items in REDLIST:
    for _tv, _sym, _name, _exch, _cur in _items:
        META.setdefault(_sym, (_name, _exch, _cur, _cat))
