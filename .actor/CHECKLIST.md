# Actor 上传前检查清单（一致性已核对）

- **input_schema.json** ↔ **config.py**：所有字段一一对应，别名与类型一致；extractMode、waitUntil、crawlMode 已用 Literal 与 schema enum 对齐。
- **main.py**：向 crawl_urls 传入全部 ActorInput 参数；runSummary 含 failedUrls；早期错误分支调用 _set_run_summary 使用默认 failed_urls=None。
- **crawler.py**：接收并处理 crawl_mode、include_link_urls；full/discover_only 输出形状与文档一致；_link_urls 与 discover 输出含 links_internal/links_external。
- **output_schema.json**：description 已注明 runSummary 含 failedUrls。
- **dataset_schema.json**：已声明 links_internal、links_external（可选数组）；additionalProperties: true 兼容两种模式。
- **actor.json**：name、title、description、input/output/storages、dockerfile 路径正确。
- **Dockerfile**：基于 apify/actor-python:3.11，安装依赖并执行 crawl4ai-setup，CMD 为 python -m crawl4ai_actor.main。
- **README.md**：含 crawlMode、includeLinkUrls、failedUrls、示例与选项表。
- **项目说明与使用指南.md**：与当前功能一致。
- **tests**：test_config 覆盖 crawlMode/includeLinkUrls；ux_matrix _base_input 含全部 crawl_urls 参数。
- **.dockerignore**：已排除脚本生成文件，减小镜像上下文。

最后验证：`pytest tests/` 全部通过。
