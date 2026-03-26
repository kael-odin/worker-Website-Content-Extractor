#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Website Content Extractor using Crawl4AI.
Crawls URLs and extracts page content in multiple formats.
"""
import os
import sys
import io

# Fix Windows GBK encoding for rich/crawl4ai output
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import asyncio
import re
from typing import Any, Callable, Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.content_scraping_strategy import ContentScrapingStrategy


def normalize_input(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize and validate input parameters."""
    # Start URLs
    start_urls = raw.get("startUrls") or []
    if isinstance(start_urls, str):
        start_urls = [{"url": start_urls}]
    elif isinstance(start_urls, list) and start_urls:
        if isinstance(start_urls[0], str):
            start_urls = [{"url": u} for u in start_urls]
    start_urls = [u.get("url", "") for u in start_urls if u.get("url")]
    
    # Max pages - 使用 None 作为哨兵值，正确处理0
    max_pages = raw.get("maxPages")
    if max_pages is None:
        max_pages = 50
    else:
        max_pages = int(max_pages)
    max_pages = max(1, min(max_pages, 10000))
    
    # Max depth
    max_depth = raw.get("maxDepth")
    if max_depth is None:
        max_depth = 2
    else:
        max_depth = int(max_depth)
    max_depth = max(0, min(max_depth, 10))
    
    # Concurrency
    concurrency = raw.get("concurrency")
    if concurrency is None:
        concurrency = 5
    else:
        concurrency = int(concurrency)
    concurrency = max(1, min(concurrency, 50))
    
    # Timeout
    timeout = raw.get("requestTimeoutSecs")
    if timeout is None:
        timeout = 60
    else:
        timeout = int(timeout)
    timeout = max(5, min(timeout, 600))
    
    # Extract mode
    extract_mode = raw.get("extractMode", "markdown") or "markdown"
    if extract_mode not in ("markdown", "html", "text"):
        extract_mode = "markdown"
    
    # Wait until
    wait_until = raw.get("waitUntil", "domcontentloaded") or "domcontentloaded"
    if wait_until not in ("domcontentloaded", "load", "networkidle"):
        wait_until = "domcontentloaded"
    
    # Other options
    same_domain = bool(raw.get("sameDomainOnly", True))
    clean_content = bool(raw.get("cleanContent", True))
    include_raw = bool(raw.get("includeRawContent", False))
    max_chars = int(raw.get("maxContentChars", 0) or 0)
    excerpt_chars = int(raw.get("contentExcerptChars", 300) or 300)
    max_retries = int(raw.get("maxRetries", 2) or 2)
    headless = bool(raw.get("headless", True))
    use_proxy = bool(raw.get("useProxy", False))
    
    # Patterns
    include_patterns = raw.get("includePatterns") or []
    if isinstance(include_patterns, str):
        include_patterns = [include_patterns]
    exclude_patterns = raw.get("excludePatterns") or []
    if isinstance(exclude_patterns, str):
        exclude_patterns = [exclude_patterns]
    
    # Selectors
    wait_for_selector = raw.get("waitForSelector") or ""
    css_selector = raw.get("cssSelector") or ""
    
    # Crawl mode
    crawl_mode = raw.get("crawlMode", "full") or "full"
    include_links = bool(raw.get("includeLinkUrls", False))
    
    return {
        "start_urls": start_urls,
        "max_pages": max_pages,
        "max_depth": max_depth,
        "concurrency": concurrency,
        "timeout": timeout,
        "extract_mode": extract_mode,
        "wait_until": wait_until,
        "same_domain": same_domain,
        "clean_content": clean_content,
        "include_raw": include_raw,
        "max_chars": max_chars,
        "excerpt_chars": excerpt_chars,
        "max_retries": max_retries,
        "headless": headless,
        "use_proxy": use_proxy,
        "include_patterns": include_patterns,
        "exclude_patterns": exclude_patterns,
        "wait_for_selector": wait_for_selector,
        "css_selector": css_selector,
        "crawl_mode": crawl_mode,
        "include_links": include_links,
    }


def matches_patterns(url: str, patterns: List[str], default: bool = True) -> bool:
    """Check if URL matches any of the regex patterns.
    
    Args:
        url: URL to check
        patterns: List of regex patterns
        default: Return value when patterns is empty (True for include, False for exclude)
    """
    if not patterns:
        return default
    for pattern in patterns:
        try:
            if re.search(pattern, url):
                return True
        except re.error:
            continue
    return False


def get_domain(url: str) -> str:
    """Extract domain from URL."""
    parsed = urlparse(url)
    return parsed.netloc.lower()


async def run_crawler(
    input_dict: Dict[str, Any],
    *,
    browser_cdp_url: Optional[str] = None,
    log: Any = None,
    push_data: Optional[Callable[[Dict[str, Any]], Any]] = None,
) -> None:
    """Run the website content crawler."""
    if log is None:
        import logging
        _log = logging.getLogger("crawler")
        class _LogAdapter:
            def debug(self, msg): _log.debug(msg)
            def info(self, msg): _log.info(msg)
            def warn(self, msg): _log.warning(msg)
            def error(self, msg): _log.error(msg)
        log = _LogAdapter()
    
    if push_data is None:
        push_data = lambda x: None
    
    params = normalize_input(input_dict)
    log.info(f"Starting crawl with {len(params['start_urls'])} URLs, max_pages={params['max_pages']}, max_depth={params['max_depth']}")
    
    if not params["start_urls"]:
        log.warn("No start URLs provided")
        return
    
    # Track visited URLs and domains
    visited: Set[str] = set()
    start_domains: Set[str] = {get_domain(u) for u in params["start_urls"]}
    pages_count = 0
    log.info(f"Start domains: {start_domains}")
    
    # Browser config - 支持 CDP 连接
    if browser_cdp_url:
        log.info(f"Connecting to CDP browser: {browser_cdp_url[:30]}...")
        browser_config = BrowserConfig(
            cdp_url=browser_cdp_url,
            use_managed_browser=False,  # 使用外部 CDP 浏览器
            headless=params["headless"],
            verbose=False,
        )
    else:
        log.info("Using local browser")
        browser_config = BrowserConfig(
            headless=params["headless"],
            verbose=False,
        )
    
    # Crawler config
    crawler_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        wait_until=params["wait_until"],
        page_timeout=params["timeout"] * 1000,
        delay_before_return_html=2,
        mean_delay=0.5,
        max_range=1.5,
    )
    
    if params["wait_for_selector"]:
        crawler_config.wait_for = params["wait_for_selector"]
    
    if params["css_selector"]:
        crawler_config.css_selector = params["css_selector"]
    
    # Queue for BFS crawling
    queue: List[tuple] = [(url, 0) for url in params["start_urls"]]
    log.info(f"Queue initialized with {len(queue)} URLs")
    
    try:
        async with AsyncWebCrawler(config=browser_config) as crawler:
            log.info("Crawler initialized, starting crawl loop...")
            iteration = 0
            while queue and pages_count < params["max_pages"]:
                iteration += 1
                url, depth = queue.pop(0)
                log.info(f"Loop iteration {iteration}: url={url}, depth={depth}")
                
                if url in visited:
                    log.info(f"Skip: already visited")
                    continue
                if depth > params["max_depth"]:
                    log.info(f"Skip: depth {depth} > max_depth {params['max_depth']}")
                    continue
                
                # Check domain
                url_domain = get_domain(url)
                if params["same_domain"] and url_domain not in start_domains:
                    log.info(f"Skip: domain {url_domain} not in start_domains")
                    continue
                
                # Check patterns - 起始URL(depth=0)不应用include/exclude模式
                # 只对发现的链接应用模式过滤
                if depth > 0:
                    if not matches_patterns(url, params["include_patterns"], default=True):
                        log.info(f"Skip: doesn't match include_patterns")
                        continue
                    if matches_patterns(url, params["exclude_patterns"], default=False):
                        log.info(f"Skip: matches exclude_patterns")
                        continue
                
                visited.add(url)
                log.info(f"Crawling: {url} (depth={depth})")
                
                try:
                    result = await crawler.arun(
                        url=url,
                        config=crawler_config,
                    )
                    
                    if not result.success:
                        log.warn(f"Failed to crawl {url}: {result.error_message}")
                        continue
                    
                    pages_count += 1
                    
                    # Build output
                    output = {
                        "url": url,
                        "title": result.metadata.get("title", "") if result.metadata else "",
                        "depth": depth,
                        "statusCode": result.status_code or 200,
                    }
                    
                    # Content based on mode
                    if params["crawl_mode"] == "full":
                        if params["extract_mode"] == "markdown":
                            content = result.markdown or ""
                            output["markdown"] = content
                        elif params["extract_mode"] == "html":
                            content = result.cleaned_html or result.html or ""
                            output["html"] = content
                        else:  # text
                            # 优先使用 extracted_content，fallback 到 markdown 的纯文本
                            content = result.extracted_content or (result.markdown or "").replace("#", "").replace("*", "").replace("`", "")
                            output["text"] = content
                        
                        # Truncate if needed - 截断并更新到output
                        if params["max_chars"] > 0 and len(content) > params["max_chars"]:
                            truncated_content = content[:params["max_chars"]]
                            # 更新对应的输出字段
                            if params["extract_mode"] == "markdown":
                                output["markdown"] = truncated_content
                            elif params["extract_mode"] == "html":
                                output["html"] = truncated_content
                            else:
                                output["text"] = truncated_content
                            content = truncated_content
                        
                        # Excerpt
                        if params["excerpt_chars"] > 0 and content:
                            output["excerpt"] = content[:params["excerpt_chars"]]
                        
                        # Include raw content
                        if params["include_raw"]:
                            output["rawContent"] = result.html or ""
                        
                        # Include links
                        if params["include_links"]:
                            output["links_internal"] = result.links.get("internal", []) if result.links else []
                            output["links_external"] = result.links.get("external", []) if result.links else []
                    
                    else:  # discover_only mode
                        output["links_internal"] = result.links.get("internal", []) if result.links else []
                        output["links_external"] = result.links.get("external", []) if result.links else []
                    
                    # Push result
                    push_data(output)
                    log.info(f"Processed: {url}")
                    
                    # Discover new links
                    if depth < params["max_depth"] and result.links:
                        for link_type in ["internal", "external"]:
                            if link_type == "external" and params["same_domain"]:
                                continue
                            for link in result.links.get(link_type, []):
                                href = link.get("href", "") if isinstance(link, dict) else link
                                if href and href not in visited:
                                    if href.startswith("http"):
                                        queue.append((href, depth + 1))
                    
                except Exception as e:
                    log.error(f"Error crawling {url}: {e}")
                    continue
    except Exception as e:
        log.error(f"Failed to initialize crawler: {e}")
        raise
    
    log.info(f"Crawl completed. Processed {pages_count} pages.")
