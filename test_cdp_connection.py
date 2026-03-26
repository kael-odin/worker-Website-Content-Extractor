#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CDP Browser Connection Test - Simplified
测试CDP浏览器连接功能
"""
import asyncio
import os
import sys

# 设置环境变量而不是包装stdout
os.environ['PYTHONIOENCODING'] = 'utf-8'

from crawler_c4ai import run_crawler


results_list = []
logs_list = []


class MockLogger:
    def debug(self, msg: str): logs_list.append(f"[DEBUG] {msg}")
    def info(self, msg: str): logs_list.append(f"[INFO] {msg}")
    def warn(self, msg: str): logs_list.append(f"[WARN] {msg}")
    def warning(self, msg: str): self.warn(msg)
    def error(self, msg: str): logs_list.append(f"[ERROR] {msg}")
    def exception(self, msg: str): logs_list.append(f"[ERROR] {msg}")


async def test_local_browser():
    """测试本地浏览器"""
    print("=" * 50)
    print("TEST: Local Browser (No CDP)")
    print("=" * 50)
    
    results_list.clear()
    logs_list.clear()
    
    def push_data(row):
        results_list.append(row)
    
    try:
        await run_crawler(
            {"startUrls": [{"url": "https://example.com"}], "maxPages": 1, "maxDepth": 0},
            browser_cdp_url=None,
            log=MockLogger(),
            push_data=push_data
        )
        
        success = len(results_list) > 0
        print(f"Result: {'PASS' if success else 'FAIL'}")
        print(f"Pages crawled: {len(results_list)}")
        return success
        
    except Exception as e:
        print(f"FAIL: {e}")
        return False


async def main():
    print("#" * 50)
    print("# CDP CONNECTION TEST")
    print("#" * 50)
    
    # 测试本地浏览器
    local_ok = await test_local_browser()
    
    # CDP测试需要在云端环境或有Chrome调试端口
    print("\n" + "=" * 50)
    print("CDP Browser Test")
    print("=" * 50)
    print("CDP connection requires:")
    print("  1. Cafe cloud environment (PROXY_AUTH env var)")
    print("  2. OR local Chrome with --remote-debugging-port")
    print("\nTo test CDP locally:")
    print('  chrome.exe --remote-debugging-port=9222')
    print('  Then set env: PROXY_AUTH=ws://localhost:9222')
    
    # 检查是否有Cafe环境变量
    auth = os.environ.get("PROXY_AUTH")
    if auth:
        print(f"\nCafe environment detected: PROXY_AUTH exists")
        cdp_url = f"ws://{auth}@chrome-ws-inner.cafescraper.com"
        print(f"Testing CDP connection...")
        
        results_list.clear()
        logs_list.clear()
        
        def push_data(row):
            results_list.append(row)
        
        try:
            await run_crawler(
                {"startUrls": [{"url": "https://example.com"}], "maxPages": 1, "maxDepth": 0},
                browser_cdp_url=cdp_url,
                log=MockLogger(),
                push_data=push_data
            )
            cdp_ok = len(results_list) > 0
            print(f"Result: {'PASS' if cdp_ok else 'FAIL'}")
        except Exception as e:
            print(f"FAIL: {e}")
            cdp_ok = False
    else:
        print("No CDP environment detected, skipping CDP test")
        cdp_ok = True  # 跳过不算失败
    
    # Summary
    print("\n" + "#" * 50)
    print("# SUMMARY")
    print("#" * 50)
    print(f"Local Browser: {'PASS' if local_ok else 'FAIL'}")
    print(f"CDP Browser: {'PASS' if cdp_ok else 'FAIL/SKIP'}")
    
    return local_ok and cdp_ok


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
