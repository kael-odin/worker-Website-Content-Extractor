# Website Content Extractor

CafeScraper Worker: crawls start URLs and extracts page content (markdown, HTML, or text) using **[Crawl4AI](https://github.com/unclecode/crawl4ai)**. Connects to the platform’s **remote fingerprint browser via CDP** only — on CafeScraper, local Chromium is not available and must not be used.

## Requirements

- **On CafeScraper:** The platform sets `PROXY_AUTH`; the worker connects to `ws://{PROXY_AUTH}@chrome-ws-inner.cafescraper.com`. If `PROXY_AUTH` is missing, the run fails with a clear error (no attempt to launch local Chromium).
- **Local testing:** Set `LOCAL_DEV=1` and have Chromium installed (e.g. `playwright install chromium`). Only then will the worker use a local browser.

References: [Crawl4AI BrowserConfig (CDP)](https://docs.crawl4ai.com/api/parameters/), [CafeScraper – Why Use Playwright](https://docs.cafescraper.com/why-use-playwright).

## Layout

| File | Role |
|------|------|
| `main.py` | Entry: input via CafeSDK, validation, CDP check, then crawler. Uses `crawler_c4ai` when crawl4ai is installed, else `scraper`. |
| `crawler_c4ai.py` | Crawl4AI crawler: `BrowserConfig(browser_mode="custom", cdp_url=...)` when CDP URL is set; enforces CDP or `LOCAL_DEV`. |
| `scraper.py` | Fallback: pure Playwright crawler, same CDP-only rule. |
| `input_schema.json` | CafeScraper input form. |
| `sdk.py`, `sdk_pb2*.py` | CafeScraper gRPC SDK. |

## Run

```bash
pip install -r requirements.txt
# On CafeScraper: PROXY_AUTH is set by the platform; no extra steps.
# Local only:
export LOCAL_DEV=1
playwright install chromium
python main.py
```

## Input (main)

| Field | Description |
|-------|-------------|
| `startUrls` | Start URLs (required). requestList `[{"url":"..."}]` or stringList `[{"string":"..."}]`. |
| `maxPages` | Max pages to crawl (1–10000, default 50). |
| `maxDepth` | Max link depth (0–10, default 2). |
| `extractMode` | `markdown` \| `html` \| `text`. |
| `crawlMode` | `full` \| `discover_only` (links only). |
| `waitUntil` | `domcontentloaded` \| `load` \| `networkidle`. |
| `waitForSelector` | CSS selector to wait for before extraction. |
| `cssSelector` | Extract only this region. |

Output: one row per page with `url`, `success`, `content`, `title`, `meta_description`, `content_excerpt`, `links_internal_count`, `links_external_count`, `extracted_at`, etc.
