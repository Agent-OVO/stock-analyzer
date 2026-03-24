# -*- coding: utf-8 -*-
"""
===================================
新闻接口 - News Endpoints
===================================

职责：
1. GET /api/v1/news/stock/{stock_code} 获取股票新闻
2. GET /api/v1/news/sentiment 获取市场情绪（热搜）
3. GET /api/v1/news/financial 获取财经新闻
4. GET /api/v1/news/search 搜索新闻
5. GET /api/v1/news/providers 获取可用提供者状态
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from src.news_service.service import NewsService
from src.news_service.base import NewsItem

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/news", tags=["news"])

# 创建新闻服务实例
news_service = NewsService()


@router.get("/stock/{stock_code}")
async def get_stock_news(
    stock_code: str,
    stock_name: Optional[str] = None,
    days: int = Query(3, ge=1, le=30, description="搜索最近几天的新闻"),
    limit: int = Query(10, ge=1, le=50, description="返回数量限制")
):
    """
    获取股票相关新闻

    Args:
        stock_code: 股票代码（如 600519, AAPL）
        stock_name: 股票名称（可选，如 贵州茅台）
        days: 搜索最近几天的新闻，默认3天
        limit: 返回数量限制，默认10条

    Returns:
        {
            "items": [...],
            "total": 10,
            "source": "NewsAggregator",
            "query_time": 1234
        }
    """
    try:
        result = news_service.get_stock_news(stock_code, stock_name, days, limit)
        return {
            "items": [item.to_dict() for item in result.items],
            "total": result.total,
            "source": result.source,
            "query_time": result.query_time
        }
    except Exception as e:
        logger.error(f"Error getting stock news for {stock_code}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sentiment")
async def get_market_sentiment(
    limit: int = Query(10, ge=1, le=50, description="返回数量限制")
):
    """
    获取市场情绪（热搜、热门话题）

    使用微博热搜等反映市场情绪

    Returns:
        {
            "items": [...],
            "total": 10,
            "source": "NewsAggregator",
            "query_time": 567
        }
    """
    try:
        result = news_service.get_market_sentiment(limit)
        return {
            "items": [item.to_dict() for item in result.items],
            "total": result.total,
            "source": result.source,
            "query_time": result.query_time
        }
    except Exception as e:
        logger.error(f"Error getting market sentiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/financial")
async def get_financial_news(
    limit: int = Query(10, ge=1, le=50, description="返回数量限制")
):
    """
    获取财经新闻

    综合 36Kr、华尔街见闻、腾讯科技等财经新闻源

    Returns:
        {
            "items": [...],
            "total": 10,
            "source": "NewsAggregator",
            "query_time": 890
        }
    """
    try:
        result = news_service.get_financial_news(limit)
        return {
            "items": [item.to_dict() for item in result.items],
            "total": result.total,
            "source": result.source,
            "query_time": result.query_time
        }
    except Exception as e:
        logger.error(f"Error getting financial news: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def search_news(
    query: str = Query(..., description="搜索关键词"),
    limit: int = Query(10, ge=1, le=50, description="返回数量限制"),
    days: int = Query(7, ge=1, le=30, description="搜索最近几天")
):
    """
    通用新闻搜索

    Args:
        query: 搜索关键词
        limit: 返回数量限制
        days: 搜索最近几天的新闻

    Returns:
        {
            "items": [...],
            "total": 10,
            "source": "NewsAggregator",
            "query_time": 1234
        }
    """
    try:
        result = news_service.search_news(query, limit, days)
        return {
            "items": [item.to_dict() for item in result.items],
            "total": result.total,
            "source": result.source,
            "query_time": result.query_time
        }
    except Exception as e:
        logger.error(f"Error searching news for '{query}': {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/providers")
async def get_providers_status():
    """
    获取所有新闻提供者的状态

    Returns:
        {
            "current": "NewsAggregator",
            "available": {
                "news_aggregator": true,
                "tavily": false,
                "bocha": false,
                ...
            }
        }
    """
    try:
        current = news_service.get_provider_info()
        available = news_service.get_available_providers()
        return {
            "current": current,
            "available": available
        }
    except Exception as e:
        logger.error(f"Error getting providers status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tech")
async def get_tech_news(
    limit: int = Query(10, ge=1, le=50, description="返回数量限制")
):
    """
    获取科技新闻

    Hacker News + GitHub Trending + Product Hunt + V2EX

    Returns:
        {
            "items": [...],
            "total": 10,
            "source": "NewsAggregator"
        }
    """
    try:
        # 如果提供者支持，获取科技新闻
        provider = news_service.provider
        if hasattr(provider, 'get_tech_news'):
            items = provider.get_tech_news(limit)
        else:
            items = []

        return {
            "items": [item.to_dict() for item in items],
            "total": len(items),
            "source": news_service.provider_name
        }
    except Exception as e:
        logger.error(f"Error getting tech news: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ai")
async def get_ai_news(
    limit: int = Query(10, ge=1, le=50, description="返回数量限制")
):
    """
    获取 AI 相关新闻和论文

    Hugging Face Papers + Latent Space AI News

    Returns:
        {
            "items": [...],
            "total": 10,
            "source": "NewsAggregator"
        }
    """
    try:
        # 如果提供者支持，获取AI新闻
        provider = news_service.provider
        if hasattr(provider, 'get_ai_news'):
            items = provider.get_ai_news(limit)
        else:
            items = []

        return {
            "items": [item.to_dict() for item in items],
            "total": len(items),
            "source": news_service.provider_name
        }
    except Exception as e:
        logger.error(f"Error getting AI news: {e}")
        raise HTTPException(status_code=500, detail=str(e))
