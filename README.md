# Market Tracker

A mobile-first daily stock market & economy tracker for a Canadian investor in Ottawa:
pre-market briefing, cross-asset board, interactive charts (incl. the 200-week SMA),
economic + earnings calendar, persistent watchlists, market heatmap, ranked market
themes, and CFTC leveraged-fund positioning — all as a static app on GitHub Pages.

**Live app:** https://sullybrown-design.github.io/market-tracker/
**Repo:** https://github.com/sullybrown-design/market-tracker

Open the live URL on iPhone Safari → Share → **Add to Home Screen** for the app icon
and full-screen standalone mode.

## How it works

There is no server and no API key anywhere. A GitHub Actions job
(`.github/workflows/ingest.yml`) runs `scripts/ingest.py` (Python stdlib only):

- **Fast refresh** (~every 20 min, Mon–Fri trading hours UTC): cross-asset snapshot,
  universe quotes, grouped headlines, earnings calendar, economic calendar, CFTC
  positioning, 13F fund list, data-driven themes/recap, and a dated archive snapshot.
- **Daily candle refresh** (22:30 UTC weekdays): per-symbol daily (5y), weekly (10y —
  enough for a true 200-week SMA) and intraday (5d, 5m) candle files.

Each dataset is its own JSON file under `data/`. If a provider fails, the previous
good file is kept (never blanked) and the failure is logged in `data/status.json`.
The frontend caches the last successful snapshot on-device and labels it stale when
offline or old. Quotes are **delayed / end-of-day** per exchange rules — this app has
no real-time streaming entitlement, and the UI says so wherever it matters.

## Data sources (all verified live on 2026-11-25)

| Data | Source | Notes |
|---|---|---|
| Quotes, candles, heatmap | Yahoo Finance chart API | Delayed/EOD. Curated ~110-name universe, not the full S&P 500 |
| USD/CAD official rate | Bank of Canada Valet API | Daily indicative rate, shown alongside the intraday quote |
| Headlines | Google News RSS | Grouped by story; "why it matters" is labelled commentary |
| Earnings | Nasdaq API | EPS est/actual/surprise. Revenue is **not** in this feed and is shown as unavailable |
| Economic calendar | ForexFactory feed via faireconomy.media | US & Canada, current week. Revisions not supplied |
| Positioning | CFTC Traders in Financial Futures (Socrata API) | Leveraged Funds, futures only, Tue positions published Fri |
| 13F | SEC EDGAR | Quarterly; the app links to the authoritative filing lists |

## Maintenance

- **Run ingestion by hand:** Actions tab → "Ingest market data" → Run workflow
  (mode: fast / candles / all). Locally: `python3 scripts/ingest.py fast|candles|all`
- **Add a ticker to the universe:** add a row to `scripts/universe.py`
  (symbol, name, sector, approx. market cap $B, exchange, currency), then run a
  candles + fast ingestion. TSX listings use the `.TO` suffix (e.g. `ENB.TO` = TSX/CAD,
  `ENB` = NYSE/USD).
- **Watchlists** live in the browser's localStorage per device. Use Export/Import in
  the Watchlists tab to back them up or move them.
- **Deploy:** any push to `main` runs `.github/workflows/pages.yml` and redeploys
  GitHub Pages (source must stay set to "GitHub Actions" in repo Settings → Pages).
- **Archive:** one snapshot per day lands in `data/archive/YYYY-MM-DD.json`; the
  Research → Archive tab reads them. History starts at launch (2026-11-25) and is
  never backfilled.

## Known limitations

- No real-time quotes (would need a paid entitlement + a key-holding backend; the
  frontend is static by design so keys never ship to the browser).
- Market open/closed status is schedule-based (9:30–16:00 ET) and does not model
  exchange holidays.
- Economic calendar covers the current week only (the feed's next-week file was not
  published at verification time); earnings cover roughly −10/+21 days.
- CFTC TFF covers financial futures only; metals/energy positioning lives in the
  CFTC Disaggregated COT report, which is not yet wired in.
- 13F view links to EDGAR rather than restating holdings — a change in reported
  value is not a purchase or sale.
