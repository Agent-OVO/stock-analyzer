# -*- coding: utf-8 -*-
"""
===================================
新闻服务抽象层 - Base Module
===================================

定义新闻提供者的抽象接口和数据结构
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class NewsItem:
    """
    统一新闻数据结构

    Attributes:
        title: 新闻标题
        url: 新闻链接
        source: 新闻来源
        content: 新闻正文（可选）
        published_at: 发布时间（可选）
        heat: 热度指标（可选）
        tags: 标签列表（可选）
        raw_data: 原始数据（可选，用于调试）
    """
    title: str
    url: str
    source: str
    content: Optional[str] = None
    published_at: Optional[str] = None
    heat: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    raw_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'title': self.title,
            'url': self.url,
            'source': self.source,
            'content': self.content,
            'published_at': self.published_at,
            'heat': self.heat,
            'tags': self.tags,
        }


@dataclass
class SearchResult:
    """
    搜索结果封装

    Attributes:
        items: 新闻列表
        total: 总数（如果有）
        source: 数据来源
        query_time: 查询耗时（毫秒）
    """
    items: List[NewsItem]
    total: Optional[int] = None
    source: str = ""
    query_time: Optional[int] = None


class NewsProvider(ABC):
    """
    新闻提供者抽象基类

    所有新闻提供者必须实现此接口
    """

    @abstractmethod
    def get_name(self) -> str:
        """
        获取提供者名称

        Returns:
            提供者名称，如 'NewsAggregator', 'Tavily', 'Bocha'
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        检查提供者是否可用

        Returns:
            True 如果可用，False 否则
        """
        pass

    @abstractmethod
    def search_stock_news(
        self,
        stock_code: str,
        stock_name: str = None,
        days: int = 3,
        limit: int = 10
    ) -> List[NewsItem]:
        """
        搜索股票相关新闻

        Args:
            stock_code: 股票代码（如 600519）
            stock_name: 股票名称（如 贵州茅台）
            days: 搜索最近几天的新闻
            limit: 返回数量限制

        Returns:
            新闻列表
        """
        pass

    @abstractmethod
    def get_market_sentiment(self, limit: int = 10) -> List[NewsItem]:
        """
        获取市场情绪（热搜、热门话题等）

        Args:
            limit: 返回数量限制

        Returns:
            热门话题列表
        """
        pass

    @abstractmethod
    def get_financial_news(self, limit: int = 10) -> List[NewsItem]:
        """
        获取财经新闻

        Args:
            limit: 返回数量限制

        Returns:
            财经新闻列表
        """
        pass

    @abstractmethod
    def search_news(
        self,
        query: str,
        limit: int = 10,
        days: int = 7
    ) -> List[NewsItem]:
        """
        通用新闻搜索

        Args:
            query: 搜索关键词
            limit: 返回数量限制
            days: 搜索最近几天的新闻

        Returns:
            新闻列表
        """
        pass

    def get_provider_info(self) -> Dict[str, Any]:
        """
        获取提供者信息

        Returns:
            提供者信息字典
        """
        return {
            'name': self.get_name(),
            'available': self.is_available(),
            'type': self.__class__.__name__,
        }
