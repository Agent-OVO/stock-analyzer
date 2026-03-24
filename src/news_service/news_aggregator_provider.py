# -*- coding: utf-8 -*-
"""
===================================
News Aggregator Skill 集成
===================================

将 news-aggregator-skill 集成为新闻提供者
支持 28+ 免费新闻源，无需 API Key
"""

import subprocess
import json
import os
import sys
import logging
from typing import List
from datetime import datetime

from .base import NewsProvider, NewsItem

logger = logging.getLogger(__name__)


class NewsAggregatorProvider(NewsProvider):
    """
    News Aggregator Skill 集成提供者

    特点：
    - 免费使用，无需 API Key
    - 支持 28+ 新闻源
    - 中文优化（36Kr、华尔街见闻、微博热搜等）
    - 支持深度获取正文内容

    新闻源：
    - 全球科技: Hacker News, Product Hunt
    - 开源进展: GitHub Trending, V2EX
    - 国内风控: 36Kr, 腾讯科技
    - 社会金融: 微博热搜, 华尔街见闻
    - AI 论文: Hugging Face Papers
    - AI 行业内参: Latent Space, Ben's Bites, ChinAI 等
    """

    # 支持的新闻源映射
    SOURCE_MAPPING = {
        'tech': 'hackernews,github,producthunt,v2ex',
        'chinese_tech': '36kr,tencent,v2ex',
        'financial': '36kr,wallstreetcn,tencent',
        'sentiment': 'weibo',  # 微博热搜反映市场情绪
        'ai': 'huggingface,latentspace_ainews',
        'all': '36kr,wallstreetcn,weibo,hackernews,github,v2ex,tencent',
    }

    def __init__(self, skill_path: str = None):
        """
        初始化 News Aggregator 提供者

        Args:
            skill_path: news-aggregator-skill 的路径
                      默认为 ./skills/news-aggregator-skill
        """
        if skill_path is None:
            # 默认路径
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            skill_path = os.path.join(project_root, 'skills', 'news-aggregator-skill')

        self.skill_path = skill_path
        self.fetch_script = os.path.join(skill_path, 'scripts', 'fetch_news.py')

        logger.info(f"NewsAggregatorProvider initialized with path: {self.skill_path}")

    def get_name(self) -> str:
        return "NewsAggregator"

    def is_available(self) -> bool:
        """检查 news-aggregator-skill 是否可用"""
        return os.path.exists(self.fetch_script)

    def _run_fetcher(
        self,
        sources: str,
        limit: int = 10,
        keyword: str = None,
        deep: bool = False
    ) -> List[dict]:
        """
        调用 news-aggregator-skill 的 fetch_news.py

        Args:
            sources: 新闻源（逗号分隔）
            limit: 返回数量限制
            keyword: 关键词过滤
            deep: 是否深度获取正文

        Returns:
            原始新闻数据列表
        """
        if not self.is_available():
            logger.warning(f"News aggregator script not found: {self.fetch_script}")
            return []

        try:
            cmd = [
                sys.executable,  # 使用当前 Python 解释器
                self.fetch_script,
                '--source', sources,
                '--limit', str(limit),
                '--no-save'  # 不保存文件，直接返回 JSON
            ]

            if keyword:
                cmd.extend(['--keyword', keyword])

            if deep:
                cmd.append('--deep')

            logger.debug(f"Running command: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=120,  # 2分钟超时
                cwd=self.skill_path,  # 在 skill 目录中运行
                text=True,  # 文本模式
                encoding='utf-8',
                errors='replace'  # 替换无法解码的字符
            )

            if result.returncode == 0:
                stdout = result.stdout

                # 记录 stderr 用于调试
                if result.stderr:
                    logger.debug(f"Fetch script stderr: {result.stderr}")

                try:
                    data = json.loads(stdout)
                    logger.info(f"Fetched {len(data)} items from sources: {sources}")
                    return data
                except json.JSONDecodeError as e:
                    # 如果 JSON 解析失败，尝试清理数据
                    cleaned = stdout.strip()
                    logger.warning(f"JSON parse error: {e}, trying to clean output")
                    if cleaned:
                        try:
                            data = json.loads(cleaned)
                            logger.info(f"Fetched {len(data)} items from sources: {sources}")
                            return data
                        except json.JSONDecodeError:
                            logger.error(f"Failed to parse JSON even after cleaning: {cleaned[:200]}")
                    return []
            else:
                logger.error(f"Fetch script failed with return code {result.returncode}")
                if result.stderr:
                    logger.error(f"Error output: {result.stderr}")
                return []

        except subprocess.TimeoutExpired:
            logger.error("Fetch script timeout after 120 seconds")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON output: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error running fetch script: {e}")
            return []

    def _to_news_item(self, raw: dict) -> NewsItem:
        """将原始数据转换为 NewsItem"""
        return NewsItem(
            title=raw.get('title', ''),
            url=raw.get('url', ''),
            source=raw.get('source', ''),
            content=raw.get('content', ''),
            published_at=raw.get('time', ''),
            heat=raw.get('heat', ''),
            raw_data=raw  # 保留原始数据用于调试
        )

    def search_stock_news(
        self,
        stock_code: str,
        stock_name: str = None,
        days: int = 3,
        limit: int = 10
    ) -> List[NewsItem]:
        """
        搜索股票相关新闻

        使用 36Kr + 华尔街见闻 搜索
        """
        # 构建搜索关键词
        keywords = [stock_code]
        if stock_name:
            keywords.append(stock_name)
        keyword = ','.join(keywords)

        # 使用财经新闻源
        sources = self.SOURCE_MAPPING['financial']
        raw_items = self._run_fetcher(sources, limit, keyword)

        return [self._to_news_item(item) for item in raw_items]

    def get_market_sentiment(self, limit: int = 10) -> List[NewsItem]:
        """
        获取市场情绪

        使用微博热搜反映市场情绪
        """
        sources = self.SOURCE_MAPPING['sentiment']
        raw_items = self._run_fetcher(sources, limit)

        items = [self._to_news_item(item) for item in raw_items]

        # 添加情绪标签
        for item in items:
            item.tags = ['sentiment', 'hot_search']

        return items

    def get_financial_news(self, limit: int = 10) -> List[NewsItem]:
        """
        获取财经新闻

        综合 36Kr + 华尔街见闻 + 腾讯科技
        """
        sources = self.SOURCE_MAPPING['financial']
        raw_items = self._run_fetcher(sources, limit)

        items = [self._to_news_item(item) for item in raw_items]

        # 添加财经标签
        for item in items:
            item.tags = ['financial', 'news']

        return items

    def search_news(
        self,
        query: str,
        limit: int = 10,
        days: int = 7
    ) -> List[NewsItem]:
        """
        通用新闻搜索

        搜索所有可用源
        """
        sources = self.SOURCE_MAPPING['all']
        raw_items = self._run_fetcher(sources, limit, query)

        return [self._to_news_item(item) for item in raw_items]

    def get_tech_news(self, limit: int = 10) -> List[NewsItem]:
        """
        获取科技新闻

        Hacker News + GitHub + Product Hunt + V2EX
        """
        sources = self.SOURCE_MAPPING['tech']
        raw_items = self._run_fetcher(sources, limit)

        items = [self._to_news_item(item) for item in raw_items]

        for item in items:
            item.tags = ['tech', 'news']

        return items

    def get_ai_news(self, limit: int = 10) -> List[NewsItem]:
        """
        获取 AI 相关新闻

        Hugging Face Papers + Latent Space AI News
        """
        sources = self.SOURCE_MAPPING['ai']
        raw_items = self._run_fetcher(sources, limit)

        items = [self._to_news_item(item) for item in raw_items]

        for item in items:
            item.tags = ['ai', 'research']

        return items
