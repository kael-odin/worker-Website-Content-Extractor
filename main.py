#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CafeScraper worker: Website Content Extractor. Entry: main.py. Uses CafeSDK for params, logging, result push."""
import asyncio
import os

from sdk import CafeSDK
from crawler_c4ai import run_crawler

RESULT_TABLE_HEADERS = [
    {"label": "URL", "key": "url", "format": "text"},
    {"label": "Title", "key": "title", "format": "text"},
    {"label": "Depth", "key": "depth", "format": "integer"},
    {"label": "Status Code", "key": "statusCode", "format": "integer"},
    {"label": "Markdown", "key": "markdown", "format": "text"},
    {"label": "HTML", "key": "html", "format": "text"},
    {"label": "Text", "key": "text", "format": "text"},
    {"label": "Excerpt", "key": "excerpt", "format": "text"},
    {"label": "Internal Links", "key": "links_internal", "format": "array"},
    {"label": "External Links", "key": "links_external", "format": "array"},
]
HEADER_KEYS = [h["key"] for h in RESULT_TABLE_HEADERS]


class _CafeLogAdapter:
    def debug(self, msg: str, exc_info: bool = False):
        CafeSDK.Log.debug(msg)

    def info(self, msg: str):
        CafeSDK.Log.info(msg)

    def warn(self, msg: str):
        CafeSDK.Log.warn(msg)

    def warning(self, msg: str):
        CafeSDK.Log.warn(msg)

    def error(self, msg: str):
        CafeSDK.Log.error(msg)

    def exception(self, msg: str):
        import traceback
        CafeSDK.Log.error(f"{msg}\n{traceback.format_exc()}")


def _row_for_push(row: dict) -> dict:
    return {k: row.get(k) if isinstance(row.get(k), (list, dict, str, int, float, bool, type(None))) else str(row.get(k)) for k in HEADER_KEYS}


DEFAULT_INPUT = {
    "maxPages": 50,
    "maxDepth": 2,
    "concurrency": 5,
    "requestTimeoutSecs": 60,
    "extractMode": "markdown",
    "waitUntil": "domcontentloaded",
    "sameDomainOnly": True,
    "cleanContent": True,
    "headless": True,
}


async def run():
    try:
        raw = CafeSDK.Parameter.get_input_json_dict() or {}
        input_json_dict = {**DEFAULT_INPUT, **{k: v for k, v in raw.items() if k != "version"}}
        
        # Handle startUrls format - 多种格式兼容
        start_urls = input_json_dict.get("startUrls") or []
        
        # 格式1: [{"url": "..."}] - 标准格式
        # 格式2: [{"string": "..."}] - Cafe stringList格式
        # 格式3: ["...", "..."] - 字符串数组
        # 格式4: 单个 "url" 字段 - Cafe平台可能单独传入
        
        if start_urls and isinstance(start_urls, list):
            if isinstance(start_urls[0], dict):
                if "string" in start_urls[0]:
                    # 格式2: Cafe stringList
                    start_urls = [{"url": s.get("string", "")} for s in start_urls if s.get("string")]
                # 格式1: 已经是标准格式，保持不变
            elif isinstance(start_urls[0], str):
                # 格式3: 字符串数组
                start_urls = [{"url": u} for u in start_urls]
        
        # 格式4: 如果startUrls为空但有单独的url字段（Cafe平台可能这样传）
        if not start_urls and "url" in input_json_dict:
            single_url = input_json_dict["url"]
            if single_url and isinstance(single_url, str):
                start_urls = [{"url": single_url}]
                CafeSDK.Log.info(f"Using single URL from 'url' field: {single_url}")
        
        input_json_dict["startUrls"] = start_urls
        
        if not start_urls:
            CafeSDK.Log.warn("No valid startUrls provided!")
            return
        
        CafeSDK.Log.debug(f"params: {input_json_dict}")
        
        # Check for platform CDP browser
        auth = os.environ.get("PROXY_AUTH")
        is_cafe_env = bool(auth)
        browser_cdp_url = f"ws://{auth}@chrome-ws-inner.cafescraper.com" if auth else None
        
        if browser_cdp_url:
            CafeSDK.Log.info("CafeScraper cloud environment detected")
            CafeSDK.Log.info("Connecting to fingerprint browser (CDP)")
        else:
            CafeSDK.Log.info("Local development mode")
            CafeSDK.Log.info("Using local browser")
        
        CafeSDK.Result.set_table_header(RESULT_TABLE_HEADERS)
        
        def push_data(row: dict):
            CafeSDK.Result.push_data(_row_for_push(row))
        
        await run_crawler(
            input_json_dict,
            browser_cdp_url=browser_cdp_url,
            log=_CafeLogAdapter(),
            push_data=push_data,
        )
        CafeSDK.Log.info("Run completed successfully")
    except Exception as e:
        import traceback
        CafeSDK.Log.error(f"Run failed: {e}")
        CafeSDK.Log.error(traceback.format_exc())
        CafeSDK.Result.push_data({"error": str(e), "error_code": "500", "status": "failed"})
        raise


if __name__ == "__main__":
    asyncio.run(run())
