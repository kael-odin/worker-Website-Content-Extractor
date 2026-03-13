from __future__ import annotations

from typing import Any, AsyncIterator, List, Optional

from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig


def _extract_content(result: Any, extract_mode: str) -> Optional[str]:
    if extract_mode == "html":
        return getattr(result, "cleaned_html", None) or getattr(result, "html", None)

    if extract_mode == "text":
        return (
            getattr(result, "text", None)
            or getattr(result, "cleaned_text", None)
            or _extract_content(result, "markdown")
        )

    markdown_obj = getattr(result, "markdown", None)
    if markdown_obj is None:
        return None
    return getattr(markdown_obj, "raw_markdown", None) or str(markdown_obj)


async def crawl_urls(
    start_urls: List[str],
    max_pages: int,
    max_depth: int,
    concurrency: int,
    request_timeout_secs: int,
    headless: bool,
    proxy_url: Optional[str],
    extract_mode: str,
) -> AsyncIterator[dict]:
    browser_config = BrowserConfig(
        headless=headless,
        proxy=proxy_url,
    )
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        stream=True,
        semaphore_count=concurrency,
        page_timeout=int(request_timeout_secs * 1000),
    )

    _ = max_depth  # Depth handling is managed by crawl4ai strategies; keep for future expansion.

    async with AsyncWebCrawler(config=browser_config) as crawler:
        stream = await crawler.arun_many(start_urls, config=run_config)

        processed = 0
        if hasattr(stream, "__aiter__"):
            async for result in stream:
                processed += 1
                yield {
                    "url": getattr(result, "url", None),
                    "success": getattr(result, "success", None),
                    "status_code": getattr(result, "status_code", None),
                    "error_message": getattr(result, "error_message", None),
                    "content": _extract_content(result, extract_mode),
                }
                if processed >= max_pages:
                    break
        else:
            for result in stream:
                processed += 1
                yield {
                    "url": getattr(result, "url", None),
                    "success": getattr(result, "success", None),
                    "status_code": getattr(result, "status_code", None),
                    "error_message": getattr(result, "error_message", None),
                    "content": _extract_content(result, extract_mode),
                }
                if processed >= max_pages:
                    break
