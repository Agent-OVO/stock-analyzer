# -*- coding: utf-8 -*-
"""
===================================
新闻提供者工厂 - Factory Module
===================================

根据配置创建新闻提供者实例
支持自动选择、手动指定、优先级排序
"""

import os
import logging
from typing import Optional, Dict, Callable

from .base import NewsProvider
from .news_aggregator_provider import NewsAggregatorProvider
from .search_api_provider import LazySearchAPIProvider
from .stock_news_provider import StockNewsProvider

logger = logging.getLogger(__name__)


class NewsProviderFactory:
    """
    新闻提供者工厂

    职责：
    1. 注册所有可用的新闻提供者
    2. 根据配置创建对应的提供者实例
    3. 支持自动选择可用的提供者
    4. 提供提供者优先级管理
    """

    # 提供者类型与创建函数的映射
    _providers: Dict[str, Callable[[], NewsProvider]] = {
        'stock_news': StockNewsProvider,           # 专用个股新闻（优先级最高）
        'news_aggregator': NewsAggregatorProvider,
        'tavily': lambda: LazySearchAPIProvider('tavily'),
        'serpapi': lambda: LazySearchAPIProvider('serpapi'),
        'bocha': lambda: LazySearchAPIProvider('bocha'),
        'brave': lambda: LazySearchAPIProvider('brave'),
    }

    # 提供者优先级（从高到低）
    # 个股新闻优先，然后是通用搜索
    _priority = ['stock_news', 'news_aggregator', 'bocha', 'tavily', 'serpapi', 'brave']

    @classmethod
    def create(cls, provider_type: str = None) -> NewsProvider:
        """
        创建新闻提供者实例

        Args:
            provider_type: 提供者类型
                           None/empty: 自动选择
                           'auto': 自动选择
                           具体名称: 创建指定类型

        Returns:
            NewsProvider 实例

        Raises:
            ValueError: 未知提供者类型
            RuntimeError: 没有可用的提供者
        """
        if not provider_type:
            provider_type = 'auto'

        if provider_type == 'auto':
            return cls._create_auto()

        if provider_type in cls._providers:
            try:
                provider = cls._providers[provider_type]()
                logger.info(f"Created news provider: {provider.get_name()}")
                return provider
            except Exception as e:
                logger.error(f"Failed to create provider {provider_type}: {e}")
                raise RuntimeError(f"Failed to create provider {provider_type}: {e}")

        raise ValueError(f"Unknown news provider type: {provider_type}")

    @classmethod
    def _create_auto(cls) -> NewsProvider:
        """
        自动选择可用的提供者

        按优先级尝试，返回第一个可用的
        """
        logger.info("Auto-selecting news provider...")

        for provider_type in cls._priority:
            try:
                provider = cls._providers[provider_type]()
                if provider.is_available():
                    logger.info(f"Auto-selected news provider: {provider.get_name()}")
                    return provider
            except Exception as e:
                logger.debug(f"Provider {provider_type} not available: {e}")
                continue

        raise RuntimeError(
            "No available news provider. "
            "Please configure NEWS_PROVIDER or add API keys."
        )

    @classmethod
    def get_available_providers(cls) -> Dict[str, bool]:
        """
        获取所有提供者的可用性状态

        Returns:
            {provider_type: is_available}
        """
        status = {}
        for provider_type in cls._providers:
            try:
                provider = cls._providers[provider_type]()
                status[provider_type] = provider.is_available()
            except Exception:
                status[provider_type] = False
        return status

    @classmethod
    def register_provider(cls, provider_type: str, factory: Callable[[], NewsProvider]):
        """
        注册新的提供者

        用于扩展第三方提供者

        Args:
            provider_type: 提供者类型名称
            factory: 创建提供者的工厂函数
        """
        cls._providers[provider_type] = factory
        logger.info(f"Registered news provider: {provider_type}")

    @classmethod
    def set_priority(cls, priority: list):
        """
        设置提供者优先级

        Args:
            priority: 提供者类型列表，按优先级排序
        """
        for provider_type in priority:
            if provider_type not in cls._providers:
                raise ValueError(f"Unknown provider in priority: {provider_type}")

        cls._priority = priority
        logger.info(f"Updated provider priority: {priority}")


def get_news_provider() -> NewsProvider:
    """
    便捷函数：获取新闻提供者

    从环境变量读取 NEWS_PROVIDER，未设置则自动选择

    Returns:
        NewsProvider 实例
    """
    provider_type = os.getenv('NEWS_PROVIDER', 'auto')
    return NewsProviderFactory.create(provider_type)
