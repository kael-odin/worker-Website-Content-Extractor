# 📄 Website Content Extractor

[English](#english) | [中文](#中文)

---

<a name="english"></a>

## English

### 🚀 Intelligent Web Content Extraction with Crawl4AI

A powerful CafeScraper worker that crawls websites and extracts page content in multiple formats (Markdown, HTML, or plain text) using the Crawl4AI library. Features configurable depth, wait conditions, CSS selectors, and comprehensive link discovery.

### ✨ Key Features

| Feature | Description |
|---------|-------------|
| 📄 **Multiple Output Formats** | Markdown, HTML, or plain text |
| 🔄 **Link Discovery** | Automatic internal/external link detection |
| 📏 **Depth Control** | Configurable crawl depth (0-10) |
| 🎯 **CSS Selectors** | Extract specific page regions |
| ⏳ **Smart Waiting** | Wait for selectors, dynamic content, network idle |
| 🔗 **Pattern Matching** | Include/exclude URL patterns with regex |
| 🧹 **Content Cleaning** | Remove navigation, normalize whitespace |
| 📊 **Content Excerpts** | Generate previews for quick scanning |

### 📋 Input Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `startUrls` | array | - | **Required.** Starting URLs |
| `maxPages` | integer | 50 | Max pages to process (1-10000) |
| `maxDepth` | integer | 2 | Max link depth (0-10) |
| `concurrency` | integer | 5 | Concurrent page tasks (1-50) |
| `requestTimeoutSecs` | integer | 60 | Timeout per page (5-600s) |
| `extractMode` | string | `markdown` | Output format: markdown/html/text |
| `waitUntil` | string | `domcontentloaded` | Load strategy |
| `waitForSelector` | string | - | CSS selector to wait for |
| `cssSelector` | string | - | Extract only this region |
| `sameDomainOnly` | boolean | true | Only follow same-domain links |
| `includePatterns` | array | [] | Regex patterns to include |
| `excludePatterns` | array | [] | Regex patterns to exclude |
| `cleanContent` | boolean | true | Clean and normalize content |
| `maxContentChars` | integer | 0 | Truncate content (0=unlimited) |
| `crawlMode` | string | `full` | full or discover_only |

### 📤 Output Fields

| Field | Description |
|-------|-------------|
| `url` | Page URL |
| `title` | Page title |
| `markdown` / `html` / `text` | Extracted content (based on mode) |
| `excerpt` | Content preview (300 chars) |
| `links_internal` | Internal links found |
| `links_external` | External links found |
| `depth` | Crawl depth |
| `statusCode` | HTTP status code |

### 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python main.py
```

### ⚙️ Configuration Examples

**Basic crawl:**
```json
{
  "startUrls": [{"url": "https://example.com"}],
  "maxPages": 50,
  "maxDepth": 2,
  "extractMode": "markdown"
}
```

**Extract specific region:**
```json
{
  "startUrls": [{"url": "https://blog.example.com"}],
  "cssSelector": "article",
  "waitForSelector": ".content",
  "extractMode": "markdown"
}
```

**Discover links only (no content):**
```json
{
  "startUrls": [{"url": "https://example.com"}],
  "crawlMode": "discover_only",
  "includeLinkUrls": true
}
```

---

<a name="中文"></a>

## 中文

### 🚀 使用 Crawl4AI 的智能网页内容提取

一款强大的 CafeScraper Worker，使用 Crawl4AI 库抓取网站并提取多种格式的页面内容（Markdown、HTML 或纯文本）。支持可配置的深度、等待条件、CSS 选择器和全面的链接发现。

### ✨ 核心功能

| 功能 | 说明 |
|------|------|
| 📄 **多种输出格式** | Markdown、HTML 或纯文本 |
| 🔄 **链接发现** | 自动检测内部/外部链接 |
| 📏 **深度控制** | 可配置爬取深度（0-10） |
| 🎯 **CSS 选择器** | 提取特定页面区域 |
| ⏳ **智能等待** | 等待选择器、动态内容、网络空闲 |
| 🔗 **模式匹配** | 使用正则表达式包含/排除 URL |
| 🧹 **内容清理** | 移除导航、规范化空白 |
| 📊 **内容摘要** | 生成预览便于快速浏览 |

### 📋 输入参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `startUrls` | array | - | **必填。** 起始 URL |
| `maxPages` | integer | 50 | 最大处理页面数（1-10000） |
| `maxDepth` | integer | 2 | 最大链接深度（0-10） |
| `concurrency` | integer | 5 | 并发页面任务（1-50） |
| `requestTimeoutSecs` | integer | 60 | 页面超时（5-600秒） |
| `extractMode` | string | `markdown` | 输出格式：markdown/html/text |
| `waitUntil` | string | `domcontentloaded` | 加载策略 |
| `waitForSelector` | string | - | 等待的 CSS 选择器 |
| `cssSelector` | string | - | 仅提取此区域 |
| `sameDomainOnly` | boolean | true | 仅跟踪同域名链接 |
| `includePatterns` | array | [] | 包含的正则模式 |
| `excludePatterns` | array | [] | 排除的正则模式 |
| `cleanContent` | boolean | true | 清理和规范化内容 |
| `maxContentChars` | integer | 0 | 截断内容（0=不限制） |
| `crawlMode` | string | `full` | full 或 discover_only |

### 📤 输出字段

| 字段 | 说明 |
|------|------|
| `url` | 页面 URL |
| `title` | 页面标题 |
| `markdown` / `html` / `text` | 提取的内容（根据模式） |
| `excerpt` | 内容预览（300字符） |
| `links_internal` | 发现的内部链接 |
| `links_external` | 发现的外部链接 |
| `depth` | 爬取深度 |
| `statusCode` | HTTP 状态码 |

### 🚀 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 本地运行
python main.py
```

### ⚙️ 配置示例

**基础爬取：**
```json
{
  "startUrls": [{"url": "https://example.com"}],
  "maxPages": 50,
  "maxDepth": 2,
  "extractMode": "markdown"
}
```

**提取特定区域：**
```json
{
  "startUrls": [{"url": "https://blog.example.com"}],
  "cssSelector": "article",
  "waitForSelector": ".content",
  "extractMode": "markdown"
}
```

**仅发现链接（无内容）：**
```json
{
  "startUrls": [{"url": "https://example.com"}],
  "crawlMode": "discover_only",
  "includeLinkUrls": true
}
```

---

## 🔧 Technical Details | 技术细节

| Item | Value |
|------|-------|
| Platform | CafeScraper |
| Runtime | Python 3.11+ |
| Library | Crawl4AI |
| Browser | Playwright (CDP) |
| Output Formats | Markdown, HTML, Text |

---

## 💡 Use Cases | 应用场景

| Scenario | Description |
|----------|-------------|
| 📚 **RAG Pipelines** | Extract content for AI knowledge bases |
| 📰 **Content Aggregation** | Collect articles and blog posts |
| 🔍 **SEO Analysis** | Analyze page structure and content |
| 📊 **Data Mining** | Extract structured data from websites |
| 🗂️ **Documentation** | Create documentation from web pages |

| 场景 | 说明 |
|------|------|
| 📚 **RAG 流程** | 为 AI 知识库提取内容 |
| 📰 **内容聚合** | 收集文章和博客帖子 |
| 🔍 **SEO 分析** | 分析页面结构和内容 |
| 📊 **数据挖掘** | 从网站提取结构化数据 |
| 🗂️ **文档生成** | 从网页创建文档 |

---

## 📜 License

MIT License © 2024 kael-odin

---

## ✅ Test Report | 测试报告

**Last Updated: 2026-03-26**

| Metric | Value |
|--------|-------|
| Total Tests | 41 |
| Passed | 41 |
| Failed | 0 |
| Success Rate | **100%** |
| Duration | 239.51s |

### Test Coverage | 测试覆盖

| Category | Tests | Status |
|----------|-------|--------|
| Unit Tests (matches_patterns) | 7 | ✅ All Pass |
| Unit Tests (normalize_input) | 12 | ✅ All Pass |
| Integration Tests (Single URL) | 1 | ✅ Pass |
| Integration Tests (Extract Modes) | 3 | ✅ All Pass |
| Integration Tests (Depth Crawling) | 1 | ✅ Pass |
| Integration Tests (Pattern Filtering) | 2 | ✅ All Pass |
| Integration Tests (Same Domain) | 1 | ✅ Pass |
| Integration Tests (Content Options) | 3 | ✅ All Pass |
| Integration Tests (Crawl Modes) | 2 | ✅ All Pass |
| Integration Tests (Error Handling) | 2 | ✅ All Pass |
| Integration Tests (Wait Conditions) | 2 | ✅ All Pass |
| Integration Tests (CSS Selector) | 1 | ✅ Pass |
| Boundary Tests | 3 | ✅ All Pass |
| Stress Tests | 1 | ✅ Pass |

### Run Tests | 运行测试

```bash
# Run comprehensive test suite
python comprehensive_test.py

# Run CDP connection test
python test_cdp_connection.py
```

---

## 🔗 Links

- [GitHub Repository](https://github.com/kael-odin/worker-website-content-extractor)
- [Crawl4AI Documentation](https://github.com/unclecode/crawl4ai)
- [Report Issues](https://github.com/kael-odin/worker-website-content-extractor/issues)
