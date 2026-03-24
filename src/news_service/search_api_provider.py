# -*- coding: utf-8 -*-
"""
===================================
搜索 API 提供者 - Search API Provider
===================================

保留原有的搜索 API 实现
支持 Tavily/SerpAPI/Bocha/Brave 等商业 API
"""

import os
import logging
from typing import List, Optional
from datetime import datetime, timedelta

from .base import NewsProvider, NewsItem

# 复用原有的搜索服务
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)


class SearchAPIProvider(NewsProvider):
    """
    搜索 API 提供者

    支持的商业 API：
    - Tavily: https://tavily.com（推荐，有免费额度）
    - SerpAPI: https://serpapi.com
    - Bocha: https://bocha.cn（中文优化）
    - Brave: https://brave.com/search/api
    """

    # API 类型配置
    API_TYPES = {
        'tavily': {
            'env_key': 'TAVILY_API_KEYS',
            'name': 'Tavily',
        },
        'serpapi': {
            'env_key': 'SERPAPI_API_KEYS',
            'name': 'SerpAPI',
        },
        'bocha': {
            'env_key': 'BOCHA_API_KEYS',
            'name': 'Bocha',
        },
        'brave': {
            'env_key': 'BRAVE_API_KEYS',
            'name': 'Brave',
        },
    }

    def __init__(self, api_type: str = 'tavily'):
        """
        初始化搜索 API 提供者

        Args:
            api_type: API 类型 (tavily/serpapi/bocha/brave)
        """
        if api_type not in self.API_TYPES:
            raise ValueError(f"Unknown API type: {api_type}")

        self.api_type = api_type
        self.api_config = self.API_TYPES[api_type]
        self.api_key = os.getenv(self.api_config['env_key'], '')

        logger.info(f"SearchAPIProvider initialized with API type: {api_type}")

    def get_name(self) -> str:
        return self.api_config['name']

    def is_available(self) -> bool:
        """检查 API Key 是否配置"""
        return bool(self.api_key)

    def search_stock_news(
        self,
        stock_code: str,
        stock_name: str = None,
        days: int = 3,
        limit: int = 10
    ) -> List[NewsItem]:
        """
        使用搜索 API 查找股票新闻

        这里需要调用原有的 search_service.py 中的实现
        为了最小化改动，暂时返回空列表
        TODO: 集成原有的 SearchService
        """
        # TODO: 集成 src.search_service.SearchService
        logger.info(f"Searching stock news for {stock_code} using {self.api_type}")
        return []

    def get_market_sentiment(self, limit: int = 10) -> List[NewsItem]:
        """获取市场情绪"""
        # TODO: 实现
        logger.info(f"Getting market sentiment using {self.api_type}")
        return []

    def get_financial_news(self, limit: int = 10) -> List[NewsItem]:
        """获取财经新闻"""
        # TODO: 实现
        logger.info(f"Getting financial news using {self.api_type}")
        return []

    def search_news(
        self,
        query: str,
        limit: int = 10,
        days: int = 7
    ) -> List[NewsItem]:
        """通用新闻搜索"""
        # TODO: 实现
        logger.info(f"Searching news for '{query}' using {self.api_type}")
        return []


class LazySearchAPIProvider(SearchAPIProvider):
    """
    延迟加载的搜索 API 提供者

    在需要时才动态导入原有的 search_service
    避免启动时的循环依赖问题
    """

    def __init__(self, api_type: str = 'tavily'):
        super().__init__(api_type)
        self._search_service = None

    @property
    def search_service(self):
        """延迟导入 SearchService"""
        if self._search_service is None:
            try:
                from src.search_service import SearchService
                self._search_service = SearchService()
                logger.info("SearchService loaded successfully")
            except ImportError as e:
                logger.error(f"Failed to import SearchService: {e}")
                self._search_service = False
        return self._search_service

    def search_stock_news(
        self,
        stock_code: str,
        stock_name: str = None,
        days: int = 3,
        limit: int = 10
    ) -> List[NewsItem]:
        """使用原有 SearchService 搜索股票新闻"""
        service = self.search_service
        if not service:
            return []

        try:
            # 构建搜索查询
            query_parts = [stock_code]
            if stock_name:
                query_parts.append(stock_name)
            query = ' '.join(query_parts)

            # 调用搜索服务
            results = service.search_news(query, max_results=limit)

            # 转换为 NewsItem 格式
            items = []
            for result in results:
                items.append(NewsItem(
                    title=result.get('title', ''),
                    url=result.get('url', ''),
                    source=result.get('source', self.get_name()),
                    content=result.get('content', ''),
                    published_at=result.get('published_at', ''),
                    heat=result.get('score', ''),
                ))
            return items

        except Exception as e:
            logger.error(f"Error searching stock news: {e}")
            return []
