from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ActorInput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    start_urls: List[str] = Field(alias="startUrls", min_length=1)
    max_pages: int = Field(default=50, alias="maxPages", ge=1, le=10000)
    max_depth: int = Field(default=2, alias="maxDepth", ge=0, le=10)
    concurrency: int = Field(default=5, ge=1, le=50)
    request_timeout_secs: int = Field(default=60, alias="requestTimeoutSecs", ge=5, le=600)
    headless: bool = True
    use_proxy: bool = Field(default=False, alias="useProxy")
    proxy_groups: Optional[List[str]] = Field(default=None, alias="proxyGroups")
    extract_mode: str = Field(default="markdown", alias="extractMode")
    max_results: int = Field(default=1000, alias="maxResults", ge=1, le=200000)
