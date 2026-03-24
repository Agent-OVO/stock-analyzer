# -*- coding: utf-8 -*-
"""
===================================
新闻服务模块 - News Service Module
===================================

提供统一的新闻获取接口，支持多种新闻源：
- News Aggregator Skill (免费爬取)
- Tavily/SerpAPI/Bocha/Brave (API搜索)

设计原则：
- 依赖倒置：高层依赖抽象，不依赖具体实现
- 开闭原则：对扩展开放，对修改关闭
- 接口隔离：定义清晰的新闻服务接口
- 配置驱动：通过配置切换实现方式
"""

from .service import NewsService
from .factory import NewsProviderFactory
from .base import NewsProvider, NewsItem

__all__ = ['NewsService', 'NewsProviderFactory', 'NewsProvider', 'NewsItem']
