# -*- coding: utf-8 -*-
"""
===================================
新闻服务 - News Service
===================================

统一的新闻服务接口
提供给上层（API/Web）调用
"""

import logging
from typing import List, Optional

from .base import NewsProvider, NewsItem, SearchResult
from .factory import NewsProviderFactory, get_news_provider

logger = logging.getLogger(__name__)


class NewsService:
    """
    统一新闻服务

    职责：
    1. 封装底层新闻提供者的调用
    2. 提供统一的业务接口
    3. 处理异常和降级
    4. 记录日志和指标

    使用示例：
        service = NewsService()
        news = service.get_stock_news('600519')
        sentiment = service.get_market_sentiment()
    """

    def __init__(self, provider: NewsProvider = None):
        """
        初始化新闻服务

        Args:
            provider: 新闻提供者实例，None 则自动创建
        """
        self.provider = provider or get_news_provider()
        self.provider_name = self.provider.get_name()
        logger.info(f"NewsService initialized with provider: {self.provider_name}")

    def get_stock_news(
        self,
        stock_code: str,
        stock_name: str = None,
        days: int = 3,
        limit: int = 10
    ) -> SearchResult:
        """
        获取股票相关新闻

        Args:
            stock_code: 股票代码
            stock_name: 股票名称（可选）
            days: 搜索最近几天
            limit: 返回数量限制

        Returns:
            SearchResult 包含新闻列表和元数据
        """
        import time
        start_time = time.time()

        try:
            logger.info(f"Fetching news for stock: {stock_code}")
            items = self.provider.search_stock_news(stock_code, stock_name, days, limit)

            query_time = int((time.time() - start_time) * 1000)

            logger.info(f"Fetched {len(items)} news for {stock_code} in {query_time}ms")

            return SearchResult(
                items=items,
                total=len(items),
                source=self.provider_name,
                query_time=query_time
            )

        except Exception as e:
            logger.error(f"Error fetching stock news for {stock_code}: {e}")
            return SearchResult(
                items=[],
                total=0,
                source=self.provider_name,
                query_time=int((time.time() - start_time) * 1000)
            )

    def get_market_sentiment(self, limit: int = 10) -> SearchResult:
        """
        获取市场情绪（热搜、热门话题）

        Args:
            limit: 返回数量限制

        Returns:
            SearchResult 包含热门话题列表
        """
        import time
        start_time = time.time()

        try:
            logger.info("Fetching market sentiment")
            items = self.provider.get_market_sentiment(limit)

            query_time = int((time.time() - start_time) * 1000)

            logger.info(f"Fetched {len(items)} sentiment items in {query_time}ms")

            return SearchResult(
                items=items,
                total=len(items),
                source=self.provider_name,
                query_time=query_time
            )

        except Exception as e:
            logger.error(f"Error fetching market sentiment: {e}")
            return SearchResult(
                items=[],
                total=0,
                source=self.provider_name,
                query_time=int((time.time() - start_time) * 1000)
            )

    def get_financial_news(self, limit: int = 10) -> SearchResult:
        """
        获取财经新闻

        Args:
            limit: 返回数量限制

        Returns:
            SearchResult 包含财经新闻列表
        """
        import time
        start_time = time.time()

        try:
            logger.info("Fetching financial news")
            items = self.provider.get_financial_news(limit)

            query_time = int((time.time() - start_time) * 1000)

            logger.info(f"Fetched {len(items)} financial news in {query_time}ms")

            return SearchResult(
                items=items,
                total=len(items),
                source=self.provider_name,
                query_time=query_time
            )

        except Exception as e:
            logger.error(f"Error fetching financial news: {e}")
            return SearchResult(
                items=[],
                total=0,
                source=self.provider_name,
                query_time=int((time.time() - start_time) * 1000)
            )

    def search_news(
        self,
        query: str,
        limit: int = 10,
        days: int = 7
    ) -> SearchResult:
        """
        通用新闻搜索

        Args:
            query: 搜索关键词
            limit: 返回数量限制
            days: 搜索最近几天

        Returns:
            SearchResult 包含新闻列表
        """
        import time
        start_time = time.time()

        try:
            logger.info(f"Searching news for query: {query}")
            items = self.provider.search_news(query, limit, days)

            query_time = int((time.time() - start_time) * 1000)

            logger.info(f"Found {len(items)} results for '{query}' in {query_time}ms")

            return SearchResult(
                items=items,
                total=len(items),
                source=self.provider_name,
                query_time=query_time
            )

        except Exception as e:
            logger.error(f"Error searching news for '{query}': {e}")
            return SearchResult(
                items=[],
                total=0,
                source=self.provider_name,
                query_time=int((time.time() - start_time) * 1000)
            )

    def get_provider_info(self) -> dict:
        """
        获取当前提供者信息

        Returns:
            提供者信息字典
        """
        return self.provider.get_provider_info()

    def get_available_providers(self) -> dict:
        """
        获取所有可用提供者的状态

        Returns:
            {provider_type: is_available}
        """
        return NewsProviderFactory.get_available_providers()
