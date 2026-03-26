#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Test Suite for Website Content Extractor Worker
全量测试套件 - 覆盖所有功能点、边界条件、异常场景
"""
import asyncio
import json
import time
import traceback
from typing import Dict, List, Any, Tuple
from crawler_c4ai import run_crawler, normalize_input, matches_patterns

# Test result tracking
test_results: List[Dict[str, Any]] = []
passed = 0
failed = 0


class MockLogger:
    """Mock logger for testing"""
    def __init__(self):
        self.logs = []
    
    def debug(self, msg: str): self.logs.append(("DEBUG", msg))
    def info(self, msg: str): self.logs.append(("INFO", msg))
    def warn(self, msg: str): self.logs.append(("WARN", msg))
    def warning(self, msg: str): self.logs.append(("WARN", msg))
    def error(self, msg: str): self.logs.append(("ERROR", msg))
    def exception(self, msg: str): self.logs.append(("ERROR", f"{msg}\n{traceback.format_exc()}"))


def record_test(name: str, success: bool, details: str = "", duration: float = 0):
    """Record test result"""
    global passed, failed
    result = {
        "name": name,
        "success": success,
        "details": details,
        "duration_sec": round(duration, 2)
    }
    test_results.append(result)
    if success:
        passed += 1
        print(f"✅ PASS: {name} ({duration:.2f}s)")
    else:
        failed += 1
        print(f"❌ FAIL: {name} ({duration:.2f}s)")
        print(f"   Details: {details}")


# ============================================
# Unit Tests - 测试独立函数
# ============================================

def test_matches_patterns():
    """测试URL模式匹配函数"""
    print("\n" + "="*60)
    print("UNIT TESTS: matches_patterns()")
    print("="*60)
    
    # Test 1: Empty patterns - include模式（空列表应该返回True）
    start = time.time()
    result = matches_patterns("https://example.com/page", [], default=True)
    success = result == True
    record_test("matches_patterns: 空include模式应返回True", success, f"got {result}", time.time()-start)
    
    # Test 2: Empty patterns - exclude模式（空列表应该返回False）
    start = time.time()
    result = matches_patterns("https://example.com/page", [], default=False)
    success = result == False
    record_test("matches_patterns: 空exclude模式应返回False", success, f"got {result}", time.time()-start)
    
    # Test 3: 匹配单个模式
    start = time.time()
    result = matches_patterns("https://example.com/blog/post-1", [r"/blog/"])
    success = result == True
    record_test("matches_patterns: 单个匹配模式", success, f"got {result}", time.time()-start)
    
    # Test 4: 不匹配任何模式
    start = time.time()
    result = matches_patterns("https://example.com/about", [r"/blog/", r"/news/"])
    success = result == False
    record_test("matches_patterns: 无匹配模式", success, f"got {result}", time.time()-start)
    
    # Test 5: 匹配多个模式中的一个
    start = time.time()
    result = matches_patterns("https://example.com/news/article", [r"/blog/", r"/news/"])
    success = result == True
    record_test("matches_patterns: 匹配多个模式之一", success, f"got {result}", time.time()-start)
    
    # Test 6: 无效正则表达式
    start = time.time()
    result = matches_patterns("https://example.com/page", [r"[invalid(", r"/valid/"])
    success = result == False  # 第一个无效被跳过，第二个不匹配
    record_test("matches_patterns: 无效正则跳过", success, f"got {result}", time.time()-start)
    
    # Test 7: 复杂正则模式
    start = time.time()
    result = matches_patterns("https://example.com/products/123", [r"/products/\d+"])
    success = result == True
    record_test("matches_patterns: 复杂正则模式", success, f"got {result}", time.time()-start)


def test_normalize_input():
    """测试输入规范化函数"""
    print("\n" + "="*60)
    print("UNIT TESTS: normalize_input()")
    print("="*60)
    
    # Test 1: 默认值填充
    start = time.time()
    result = normalize_input({"startUrls": [{"url": "https://example.com"}]})
    checks = [
        result["max_pages"] == 50,
        result["max_depth"] == 2,
        result["concurrency"] == 5,
        result["timeout"] == 60,
        result["extract_mode"] == "markdown",
    ]
    success = all(checks)
    record_test("normalize_input: 默认值填充", success, str(result), time.time()-start)
    
    # Test 2: 边界值约束 - max_pages
    start = time.time()
    result = normalize_input({"startUrls": [{"url": "https://example.com"}], "maxPages": 99999})
    success = result["max_pages"] == 10000  # 应被限制到最大值
    record_test("normalize_input: max_pages上限约束", success, f"got {result['max_pages']}", time.time()-start)
    
    start = time.time()
    result = normalize_input({"startUrls": [{"url": "https://example.com"}], "maxPages": -100})
    success = result["max_pages"] == 1  # 应被限制到最小值
    record_test("normalize_input: max_pages负数约束", success, f"got {result['max_pages']}", time.time()-start)
    
    start = time.time()
    result = normalize_input({"startUrls": [{"url": "https://example.com"}], "maxPages": 0})
    success = result["max_pages"] == 1  # 0也被限制到最小值1
    record_test("normalize_input: max_pages=0约束", success, f"got {result['max_pages']}", time.time()-start)
    
    # Test 3: 边界值约束 - max_depth
    start = time.time()
    result = normalize_input({"startUrls": [{"url": "https://example.com"}], "maxDepth": 99})
    success = result["max_depth"] == 10
    record_test("normalize_input: max_depth上限约束", success, f"got {result['max_depth']}", time.time()-start)
    
    start = time.time()
    result = normalize_input({"startUrls": [{"url": "https://example.com"}], "maxDepth": -1})
    success = result["max_depth"] == 0
    record_test("normalize_input: max_depth下限约束", success, f"got {result['max_depth']}", time.time()-start)
    
    # Test 4: startUrls格式转换 - 字符串列表
    start = time.time()
    result = normalize_input({"startUrls": ["https://a.com", "https://b.com"]})
    success = result["start_urls"] == ["https://a.com", "https://b.com"]
    record_test("normalize_input: startUrls字符串列表转换", success, f"got {result['start_urls']}", time.time()-start)
    
    # Test 5: startUrls格式转换 - 单个字符串
    start = time.time()
    result = normalize_input({"startUrls": "https://example.com"})
    success = result["start_urls"] == ["https://example.com"]
    record_test("normalize_input: startUrls单字符串转换", success, f"got {result['start_urls']}", time.time()-start)
    
    # Test 6: extract_mode无效值处理
    start = time.time()
    result = normalize_input({"startUrls": [{"url": "https://example.com"}], "extractMode": "invalid"})
    success = result["extract_mode"] == "markdown"  # 应回退到默认值
    record_test("normalize_input: extract_mode无效值处理", success, f"got {result['extract_mode']}", time.time()-start)
    
    # Test 7: waitUntil无效值处理
    start = time.time()
    result = normalize_input({"startUrls": [{"url": "https://example.com"}], "waitUntil": "invalid"})
    success = result["wait_until"] == "domcontentloaded"
    record_test("normalize_input: waitUntil无效值处理", success, f"got {result['wait_until']}", time.time()-start)
    
    # Test 8: 空startUrls处理
    start = time.time()
    result = normalize_input({"startUrls": []})
    success = result["start_urls"] == []
    record_test("normalize_input: 空startUrls处理", success, f"got {result['start_urls']}", time.time()-start)
    
    # Test 9: patterns格式转换
    start = time.time()
    result = normalize_input({
        "startUrls": [{"url": "https://example.com"}],
        "includePatterns": "/blog/",
        "excludePatterns": "/admin/"
    })
    success = result["include_patterns"] == ["/blog/"] and result["exclude_patterns"] == ["/admin/"]
    record_test("normalize_input: patterns字符串转列表", success, f"include={result['include_patterns']}, exclude={result['exclude_patterns']}", time.time()-start)


# ============================================
# Integration Tests - 集成测试（真实爬取）
# ============================================

async def test_single_url_crawl():
    """测试单URL抓取"""
    print("\n" + "="*60)
    print("INTEGRATION TESTS: 单URL抓取")
    print("="*60)
    
    results = []
    def push_data(row):
        results.append(row)
    
    log = MockLogger()
    
    # Test: 抓取example.com（稳定测试站点）
    start = time.time()
    try:
        await run_crawler(
            {"startUrls": [{"url": "https://example.com"}], "maxPages": 1, "maxDepth": 0},
            log=log,
            push_data=push_data
        )
        success = len(results) > 0 and results[0].get("url") == "https://example.com"
        details = f"抓取到{len(results)}条结果" if success else "无结果"
    except Exception as e:
        success = False
        details = f"异常: {str(e)}"
    record_test("单URL抓取: example.com", success, details, time.time()-start)
    
    return results


async def test_extract_modes():
    """测试三种提取模式"""
    print("\n" + "="*60)
    print("INTEGRATION TESTS: 提取模式")
    print("="*60)
    
    for mode in ["markdown", "html", "text"]:
        results = []
        def push_data(row):
            results.append(row)
        
        log = MockLogger()
        start = time.time()
        try:
            await run_crawler(
                {"startUrls": [{"url": "https://example.com"}], "maxPages": 1, "maxDepth": 0, "extractMode": mode},
                log=log,
                push_data=push_data
            )
            has_content = len(results) > 0 and bool(results[0].get(mode))
            success = has_content
            details = f"{mode}内容长度: {len(results[0].get(mode, '')) if results else 0}"
        except Exception as e:
            success = False
            details = f"异常: {str(e)}"
        record_test(f"提取模式: {mode}", success, details, time.time()-start)


async def test_depth_crawling():
    """测试深度爬取"""
    print("\n" + "="*60)
    print("INTEGRATION TESTS: 深度爬取")
    print("="*60)
    
    results = []
    def push_data(row):
        results.append(row)
    
    log = MockLogger()
    
    # Test: 深度2爬取
    start = time.time()
    try:
        await run_crawler(
            {"startUrls": [{"url": "https://books.toscrape.com/"}], "maxPages": 10, "maxDepth": 2, "sameDomainOnly": True},
            log=log,
            push_data=push_data
        )
        depths = [r.get("depth", 0) for r in results]
        max_found_depth = max(depths) if depths else 0
        success = len(results) > 1 and max_found_depth >= 1
        details = f"抓取{len(results)}页, 最大深度{max_found_depth}"
    except Exception as e:
        success = False
        details = f"异常: {str(e)}"
    record_test("深度爬取: maxDepth=2", success, details, time.time()-start)


async def test_pattern_filtering():
    """测试URL模式过滤"""
    print("\n" + "="*60)
    print("INTEGRATION TESTS: URL模式过滤")
    print("="*60)
    
    # Test: include模式 - 起始URL会被处理，发现的链接需要匹配模式
    results = []
    def push_data(row):
        results.append(row)
    
    log = MockLogger()
    start = time.time()
    try:
        await run_crawler(
            {
                "startUrls": [{"url": "https://books.toscrape.com/"}],
                "maxPages": 10,
                "maxDepth": 1,
                "includePatterns": [r"catalogue/"],
                "sameDomainOnly": True
            },
            log=log,
            push_data=push_data
        )
        # 起始URL(depth=0)不受includePatterns限制
        # depth>0的链接需要匹配模式
        start_url = "https://books.toscrape.com/"
        has_start = any(r.get("url") == start_url for r in results)
        depth_gt_0_match = all(
            "catalogue/" in r.get("url", "") for r in results if r.get("depth", 0) > 0
        )
        success = has_start and depth_gt_0_match and len(results) > 1
        details = f"包含起始URL: {has_start}, depth>0都匹配模式: {depth_gt_0_match}, 共{len(results)}条"
    except Exception as e:
        success = False
        details = f"异常: {str(e)}"
    record_test("模式过滤: includePatterns", success, details, time.time()-start)
    
    # Test: exclude模式
    results2 = []
    def push_data2(row):
        results2.append(row)
    
    log2 = MockLogger()
    start = time.time()
    try:
        await run_crawler(
            {
                "startUrls": [{"url": "https://books.toscrape.com/"}],
                "maxPages": 10,
                "maxDepth": 1,
                "excludePatterns": [r"catalogue/"],
                "sameDomainOnly": True
            },
            log=log2,
            push_data=push_data2
        )
        # depth>0的链接不应该包含被排除的模式
        depth_gt_0_exclude = all(
            "catalogue/" not in r.get("url", "") for r in results2 if r.get("depth", 0) > 0
        )
        success = depth_gt_0_exclude and len(results2) > 0
        details = f"depth>0都不匹配exclude模式: {depth_gt_0_exclude}, 共{len(results2)}条"
    except Exception as e:
        success = False
        details = f"异常: {str(e)}"
    record_test("模式过滤: excludePatterns", success, details, time.time()-start)


async def test_same_domain_restriction():
    """测试同域名限制"""
    print("\n" + "="*60)
    print("INTEGRATION TESTS: 同域名限制")
    print("="*60)
    
    results = []
    def push_data(row):
        results.append(row)
    
    log = MockLogger()
    start = time.time()
    try:
        await run_crawler(
            {"startUrls": [{"url": "https://example.com/"}], "maxPages": 5, "maxDepth": 1, "sameDomainOnly": True},
            log=log,
            push_data=push_data
        )
        from urllib.parse import urlparse
        domains = set(urlparse(r.get("url", "")).netloc for r in results)
        only_start_domain = domains == {"example.com"}
        success = only_start_domain
        details = f"发现域名: {domains}"
    except Exception as e:
        success = False
        details = f"异常: {str(e)}"
    record_test("同域名限制: sameDomainOnly=True", success, details, time.time()-start)


async def test_content_options():
    """测试内容处理选项"""
    print("\n" + "="*60)
    print("INTEGRATION TESTS: 内容处理选项")
    print("="*60)
    
    # Test: maxContentChars截断
    results = []
    def push_data(row):
        results.append(row)
    
    log = MockLogger()
    start = time.time()
    try:
        await run_crawler(
            {
                "startUrls": [{"url": "https://example.com"}],
                "maxPages": 1,
                "maxDepth": 0,
                "maxContentChars": 100
            },
            log=log,
            push_data=push_data
        )
        content = results[0].get("markdown", "") if results else ""
        success = len(content) <= 100
        details = f"内容长度: {len(content)}"
    except Exception as e:
        success = False
        details = f"异常: {str(e)}"
    record_test("内容截断: maxContentChars=100", success, details, time.time()-start)
    
    # Test: contentExcerptChars摘要
    results2 = []
    def push_data2(row):
        results2.append(row)
    
    log2 = MockLogger()
    start = time.time()
    try:
        await run_crawler(
            {
                "startUrls": [{"url": "https://example.com"}],
                "maxPages": 1,
                "maxDepth": 0,
                "contentExcerptChars": 50
            },
            log=log2,
            push_data=push_data2
        )
        excerpt = results2[0].get("excerpt", "") if results2 else ""
        success = len(excerpt) == 50
        details = f"摘要长度: {len(excerpt)}"
    except Exception as e:
        success = False
        details = f"异常: {str(e)}"
    record_test("内容摘要: contentExcerptChars=50", success, details, time.time()-start)
    
    # Test: includeRawContent
    results3 = []
    def push_data3(row):
        results3.append(row)
    
    log3 = MockLogger()
    start = time.time()
    try:
        await run_crawler(
            {
                "startUrls": [{"url": "https://example.com"}],
                "maxPages": 1,
                "maxDepth": 0,
                "includeRawContent": True
            },
            log=log3,
            push_data=push_data3
        )
        has_raw = "rawContent" in results3[0] if results3 else False
        success = has_raw
        details = f"包含rawContent: {has_raw}"
    except Exception as e:
        success = False
        details = f"异常: {str(e)}"
    record_test("原始内容: includeRawContent=True", success, details, time.time()-start)


async def test_crawl_modes():
    """测试抓取模式"""
    print("\n" + "="*60)
    print("INTEGRATION TESTS: 抓取模式")
    print("="*60)
    
    # Test: discover_only模式
    results = []
    def push_data(row):
        results.append(row)
    
    log = MockLogger()
    start = time.time()
    try:
        await run_crawler(
            {
                "startUrls": [{"url": "https://example.com"}],
                "maxPages": 1,
                "maxDepth": 0,
                "crawlMode": "discover_only"
            },
            log=log,
            push_data=push_data
        )
        has_no_content = not results[0].get("markdown") if results else True
        has_links = "links_internal" in results[0] if results else False
        success = has_no_content and has_links
        details = f"无markdown内容: {has_no_content}, 包含链接: {has_links}"
    except Exception as e:
        success = False
        details = f"异常: {str(e)}"
    record_test("抓取模式: discover_only", success, details, time.time()-start)
    
    # Test: includeLinkUrls
    results2 = []
    def push_data2(row):
        results2.append(row)
    
    log2 = MockLogger()
    start = time.time()
    try:
        await run_crawler(
            {
                "startUrls": [{"url": "https://example.com"}],
                "maxPages": 1,
                "maxDepth": 0,
                "crawlMode": "full",
                "includeLinkUrls": True
            },
            log=log2,
            push_data=push_data2
        )
        has_links = "links_internal" in results2[0] if results2 else False
        has_content = bool(results2[0].get("markdown")) if results2 else False
        success = has_links and has_content
        details = f"包含链接: {has_links}, 包含内容: {has_content}"
    except Exception as e:
        success = False
        details = f"异常: {str(e)}"
    record_test("抓取模式: full + includeLinkUrls", success, details, time.time()-start)


async def test_error_handling():
    """测试错误处理"""
    print("\n" + "="*60)
    print("INTEGRATION TESTS: 错误处理")
    print("="*60)
    
    # Test: 无效URL
    results = []
    def push_data(row):
        results.append(row)
    
    log = MockLogger()
    start = time.time()
    try:
        await run_crawler(
            {"startUrls": [{"url": "https://this-domain-does-not-exist-12345.com"}], "maxPages": 1, "maxDepth": 0, "requestTimeoutSecs": 10},
            log=log,
            push_data=push_data
        )
        # 应该优雅地处理错误，不崩溃
        success = True  # 没有抛出异常就算成功
        details = f"优雅处理无效URL, 日志条数: {len(log.logs)}"
    except Exception as e:
        success = False
        details = f"未优雅处理异常: {str(e)}"
    record_test("错误处理: 无效URL", success, details, time.time()-start)
    
    # Test: 空startUrls
    results2 = []
    def push_data2(row):
        results2.append(row)
    
    log2 = MockLogger()
    start = time.time()
    try:
        await run_crawler(
            {"startUrls": [], "maxPages": 1, "maxDepth": 0},
            log=log2,
            push_data=push_data2
        )
        success = len(results2) == 0  # 应该没有结果
        details = f"空URL处理正常, 结果数: {len(results2)}"
    except Exception as e:
        success = False
        details = f"异常: {str(e)}"
    record_test("错误处理: 空startUrls", success, details, time.time()-start)


async def test_wait_conditions():
    """测试等待条件"""
    print("\n" + "="*60)
    print("INTEGRATION TESTS: 等待条件")
    print("="*60)
    
    for wait_until in ["domcontentloaded", "load"]:
        results = []
        def push_data(row):
            results.append(row)
        
        log = MockLogger()
        start = time.time()
        try:
            await run_crawler(
                {
                    "startUrls": [{"url": "https://example.com"}],
                    "maxPages": 1,
                    "maxDepth": 0,
                    "waitUntil": wait_until
                },
                log=log,
                push_data=push_data
            )
            success = len(results) > 0
            details = f"waitUntil={wait_until}, 结果数: {len(results)}"
        except Exception as e:
            success = False
            details = f"异常: {str(e)}"
        record_test(f"等待条件: {wait_until}", success, details, time.time()-start)


async def test_css_selector():
    """测试CSS选择器提取"""
    print("\n" + "="*60)
    print("INTEGRATION TESTS: CSS选择器")
    print("="*60)
    
    results = []
    def push_data(row):
        results.append(row)
    
    log = MockLogger()
    start = time.time()
    try:
        # 使用有明确结构的网站
        await run_crawler(
            {
                "startUrls": [{"url": "https://example.com"}],
                "maxPages": 1,
                "maxDepth": 0,
                "cssSelector": "body"  # 提取body内容
            },
            log=log,
            push_data=push_data
        )
        success = len(results) > 0
        details = f"CSS选择器提取, 内容长度: {len(results[0].get('markdown', '')) if results else 0}"
    except Exception as e:
        success = False
        details = f"异常: {str(e)}"
    record_test("CSS选择器: cssSelector=body", success, details, time.time()-start)


# ============================================
# Boundary Tests - 边界条件测试
# ============================================

async def test_boundary_conditions():
    """测试边界条件"""
    print("\n" + "="*60)
    print("BOUNDARY TESTS: 边界条件")
    print("="*60)
    
    # Test: maxPages=1
    results = []
    def push_data(row):
        results.append(row)
    
    log = MockLogger()
    start = time.time()
    try:
        await run_crawler(
            {"startUrls": [{"url": "https://books.toscrape.com/"}], "maxPages": 1, "maxDepth": 2},
            log=log,
            push_data=push_data
        )
        success = len(results) == 1
        details = f"maxPages=1时结果数: {len(results)}"
    except Exception as e:
        success = False
        details = f"异常: {str(e)}"
    record_test("边界条件: maxPages=1", success, details, time.time()-start)
    
    # Test: maxDepth=0 - 只抓取首页
    results2 = []
    def push_data2(row):
        results2.append(row)
    
    log2 = MockLogger()
    start = time.time()
    try:
        await run_crawler(
            {"startUrls": [{"url": "https://example.com"}], "maxPages": 10, "maxDepth": 0},
            log=log2,
            push_data=push_data2
        )
        # maxDepth=0 应该只抓取首页，不跟随任何链接
        all_depth_0 = all(r.get("depth") == 0 for r in results2)
        success = len(results2) == 1 and all_depth_0
        details = f"maxDepth=0时结果数: {len(results2)}, 深度全为0: {all_depth_0}"
    except Exception as e:
        success = False
        details = f"异常: {str(e)}"
    record_test("边界条件: maxDepth=0", success, details, time.time()-start)
    
    # Test: 超短超时
    results3 = []
    def push_data3(row):
        results3.append(row)
    
    log3 = MockLogger()
    start = time.time()
    try:
        await run_crawler(
            {"startUrls": [{"url": "https://example.com"}], "maxPages": 1, "maxDepth": 0, "requestTimeoutSecs": 5},
            log=log3,
            push_data=push_data3
        )
        success = True  # 能完成就算成功
        details = f"超短超时处理正常"
    except Exception as e:
        success = False
        details = f"异常: {str(e)}"
    record_test("边界条件: requestTimeoutSecs=5", success, details, time.time()-start)


# ============================================
# Stress Tests - 压力测试
# ============================================

async def test_stress():
    """测试压力场景"""
    print("\n" + "="*60)
    print("STRESS TESTS: 压力测试")
    print("="*60)
    
    # Test: 多URL并发
    urls = [
        "https://example.com",
        "https://httpbin.org",
        "https://httpbin.org/html",
    ]
    results = []
    def push_data(row):
        results.append(row)
    
    log = MockLogger()
    start = time.time()
    try:
        await run_crawler(
            {"startUrls": [{"url": u} for u in urls], "maxPages": 5, "maxDepth": 0},
            log=log,
            push_data=push_data
        )
        success = len(results) >= len(urls)  # 至少每个URL一条
        details = f"多URL处理: 输入{len(urls)}, 输出{len(results)}"
    except Exception as e:
        success = False
        details = f"异常: {str(e)}"
    record_test("压力测试: 多URL并发", success, details, time.time()-start)


# ============================================
# Main Test Runner
# ============================================

async def run_all_tests():
    """运行所有测试"""
    print("\n" + "#"*60)
    print("# COMPREHENSIVE TEST SUITE - Website Content Extractor")
    print("#"*60)
    print(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    global_start = time.time()
    
    # Unit tests (同步)
    test_matches_patterns()
    test_normalize_input()
    
    # Integration tests (异步)
    await test_single_url_crawl()
    await test_extract_modes()
    await test_depth_crawling()
    await test_pattern_filtering()
    await test_same_domain_restriction()
    await test_content_options()
    await test_crawl_modes()
    await test_error_handling()
    await test_wait_conditions()
    await test_css_selector()
    
    # Boundary tests
    await test_boundary_conditions()
    
    # Stress tests
    await test_stress()
    
    total_time = time.time() - global_start
    
    # Summary
    print("\n" + "#"*60)
    print("# TEST SUMMARY")
    print("#"*60)
    print(f"总耗时: {total_time:.2f}秒")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    print(f"成功率: {passed/(passed+failed)*100:.1f}%")
    
    # Save results
    report = {
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
        "total_time_sec": round(total_time, 2),
        "passed": passed,
        "failed": failed,
        "success_rate": f"{passed/(passed+failed)*100:.1f}%",
        "tests": test_results
    }
    
    with open("test_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n详细报告已保存: test_report.json")
    
    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
