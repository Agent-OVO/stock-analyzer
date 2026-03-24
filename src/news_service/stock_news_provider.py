# -*- coding: utf-8 -*-
"""
===================================
专用个股新闻提供者 - StockNewsProvider
===================================

数据来源：
1. 东方财富个股新闻 (akshare.stock_news_em)
2. 巨潮资讯官方公告 (akshare.stock_zh_a_disclosure_report_cninfo)
3. 同花顺F10新闻 (基于网页抓取)

特点：
- 专注个股特定新闻和公告
- 权威性强（巨潮资讯为官方披露平台）
- 免费使用，无需 API Key
- 支持A股市场
- 增强的 API 响应校验
"""

import logging
import re
import time
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

try:
    import requests
    from bs4 import BeautifulSoup
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

from .base import NewsProvider, NewsItem

logger = logging.getLogger(__name__)


class StockNewsProvider(NewsProvider):
    """
    专用个股新闻提供者

    整合东方财富新闻、巨潮资讯公告和同花顺F10新闻
    为个股分析提供精准的资讯数据

    增强特性：
    - API 响应结构校验
    - 数据完整性验证
    - 多源聚合和去重
    """

    # API 响应校验配置
    EASTMONEY_REQUIRED_FIELDS = ['新闻标题', '发布时间', '新闻链接']
    CNINFO_REQUIRED_FIELDS = ['公告标题', '公告时间', '公告链接']

    def __init__(self):
        """初始化个股新闻提供者"""
        self.akshare_available = False
        self._check_akshare()
        self.web_fetch_enabled = HAS_REQUESTS

    def _check_akshare(self) -> bool:
        """检查 akshare 是否可用"""
        try:
            import akshare as ak
            self.akshare_available = True
            self._ak = ak
            logger.info("StockNewsProvider: akshare 可用")
            return True
        except ImportError:
            logger.warning("StockNewsProvider: akshare 未安装，请运行: pip install akshare")
            return False
        except Exception as e:
            logger.warning(f"StockNewsProvider: akshare 检查失败: {e}")
            return False

    def _validate_dataframe_response(self, df, source_name: str, required_fields: List[str]) -> bool:
        """
        校验 API 返回的 DataFrame 响应

        Args:
            df: API 返回的 DataFrame
            source_name: 数据源名称（用于日志）
            required_fields: 必需字段列表

        Returns:
            是否校验通过
        """
        if df is None:
            logger.warning(f"[{source_name}] API 返回 None")
            return False

        if not isinstance(df, pd.DataFrame):
            logger.warning(f"[{source_name}] API 返回非 DataFrame 类型: {type(df)}")
            return False

        if df.empty:
            logger.info(f"[{source_name}] API 返回空数据")
            return False

        # 检查必需字段
        missing_fields = []
        for field in required_fields:
            if field not in df.columns:
                missing_fields.append(field)

        if missing_fields:
            logger.error(f"[{source_name}] API 缺少必需字段: {missing_fields}, 实际字段: {df.columns.tolist()}")
            return False

        return True

    def _safe_fetch_with_retry(self, fetch_func, source_name: str, max_retries: int = 2) -> Optional[Any]:
        """
        带重试的安全数据获取

        Args:
            fetch_func: 获取函数
            source_name: 数据源名称
            max_retries: 最大重试次数

        Returns:
            获取结果或 None
        """
        for attempt in range(max_retries):
            try:
                result = fetch_func()
                return result
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"[{source_name}] 第 {attempt + 1} 次尝试失败: {e}, 重试中...")
                    time.sleep(1)  # 等待1秒后重试
                else:
                    logger.error(f"[{source_name}] 所有重试均失败: {e}")
                    return None

    def get_name(self) -> str:
        return "StockNews"

    def is_available(self) -> bool:
        """
        检查提供者是否可用

        增强检查：验证 akshare 可用且 API 可正常调用
        """
        if not self.akshare_available:
            return False

        # 验证 API 是否可正常调用（快速健康检查）
        try:
            # 尝试调用一次API来验证连通性
            import pandas as pd
            # 使用已知存在的股票代码进行快速测试
            test_df = self._ak.stock_news_em(symbol='600000')
            return test_df is not None and not test_df.empty
        except Exception as e:
            logger.warning(f"StockNewsProvider API 不可用: {e}")
            return False

    def search_stock_news(
        self,
        stock_code: str,
        stock_name: str = None,
        days: int = 3,
        limit: int = 10
    ) -> List[NewsItem]:
        """
        获取个股相关新闻（整合东方财富新闻 + 巨潮资讯公告）

        Args:
            stock_code: 股票代码（如 '600519'）
            stock_name: 股票名称（可选，用于日志）
            days: 搜索最近几天（用于过滤）
            limit: 返回数量限制

        Returns:
            NewsItem 列表，新闻在前，公告在后
        """
        if not self.is_available():
            logger.warning("StockNewsProvider 不可用")
            return []

        all_items = []
        # 扩展日期范围以获取更多资讯
        cutoff_date = datetime.now() - timedelta(days=days * 2)

        # 1. 获取东方财富个股新闻
        try:
            news_items = self._fetch_eastmoney_news(stock_code, stock_name)
            for item in news_items:
                if self._is_within_date_range(item.published_at, cutoff_date):
                    all_items.append(item)
        except Exception as e:
            logger.warning(f"获取东方财富新闻失败: {e}")

        # 2. 获取巨潮资讯官方公告（使用宽松的日期策略）
        try:
            disclosure_items = self._fetch_cninfo_disclosures(stock_code, stock_name)
            # 公告数量较少，保留最近的几条不过滤
            for item in disclosure_items[:10]:  # 最多10条公告
                all_items.append(item)
        except Exception as e:
            logger.warning(f"获取巨潮资讯公告失败: {e}")

        # 3. 获取同花顺F10新闻（网页抓取）
        try:
            ths_items = self._fetch_tonghuashun_f10_news(stock_code, stock_name)
            for item in ths_items:
                if self._is_within_date_range(item.published_at, cutoff_date):
                    all_items.append(item)
        except Exception as e:
            logger.debug(f"获取同花顺F10新闻失败（非致命）: {e}")

        # 4. 按时间排序（最新的在前），过滤掉日期解析失败的项
        valid_items = []
        for item in all_items:
            pub_date = self._parse_datetime(item.published_at)
            if pub_date is not None:
                valid_items.append(item)
            else:
                logger.debug(f"过滤掉日期解析失败的资讯: {item.title[:50]}...")

        valid_items.sort(key=lambda x: self._parse_datetime(x.published_at) or datetime.min, reverse=True)

        # 5. 去重（基于URL）
        seen_urls = set()
        unique_items = []
        for item in valid_items:
            if item.url and item.url not in seen_urls:
                unique_items.append(item)
                seen_urls.add(item.url)
            elif not item.url:  # 没有URL的保留
                unique_items.append(item)

        logger.info(f"[{stock_code}] 获取到 {len(unique_items)} 条有效资讯（过滤 {len(all_items) - len(unique_items)} 条重复/无效数据）")
        return unique_items[:limit]

    def _fetch_eastmoney_news(
        self,
        stock_code: str,
        stock_name: str = None
    ) -> List[NewsItem]:
        """
        获取东方财富个股新闻（增强版，带校验和重试）

        API: akshare.stock_news_em
        """
        def fetch_func():
            df = self._ak.stock_news_em(symbol=stock_code)
            # 校验响应
            if not self._validate_dataframe_response(df, "东方财富", self.EASTMONEY_REQUIRED_FIELDS):
                raise ValueError("东方财富API响应校验失败")
            return df

        df = self._safe_fetch_with_retry(fetch_func, "东方财富")

        if df is None:
            return []

        items = []
        for _, row in df.iterrows():
            try:
                # 解析字段（增加字段缺失时的默认值处理）
                title = row.get('新闻标题', '').strip()
                content = row.get('新闻内容', '').strip()
                published_at = row.get('发布时间', '').strip()
                source = row.get('文章来源', '东方财富').strip()
                url = row.get('新闻链接', '').strip()

                # 必需字段校验
                if not title:
                    logger.debug(f"东方财富新闻缺少标题，跳过")
                    continue

                if not url:
                    logger.debug(f"东方财富新闻缺少URL，跳过: {title[:30]}")
                    continue

                items.append(NewsItem(
                    title=title,
                    url=url,
                    source=source,
                    content=content,
                    published_at=published_at,
                    raw_data={
                        'type': 'news',
                        'provider': 'eastmoney',
                        'stock_code': stock_code
                    }
                ))

            except Exception as e:
                logger.debug(f"解析东方财富新闻行数据失败: {e}")
                continue

        logger.debug(f"[{stock_code}] 东方财富新闻: {len(items)} 条")
        return items

    def _fetch_cninfo_disclosures(
        self,
        stock_code: str,
        stock_name: str = None
    ) -> List[NewsItem]:
        """
        获取巨潮资讯官方公告（增强版，带校验和重试）

        API: akshare.stock_zh_a_disclosure_report_cninfo
        """
        def fetch_func():
            df = self._ak.stock_zh_a_disclosure_report_cninfo(symbol=stock_code)
            # 校验响应
            if not self._validate_dataframe_response(df, "巨潮资讯", self.CNINFO_REQUIRED_FIELDS):
                raise ValueError("巨潮资讯API响应校验失败")
            return df

        df = self._safe_fetch_with_retry(fetch_func, "巨潮资讯")

        if df is None:
            return []

        items = []
        for _, row in df.iterrows():
            try:
                # 解析字段（增加字段缺失时的默认值处理）
                title = row.get('公告标题', '').strip()
                published_at = row.get('公告时间', '').strip()
                url = row.get('公告链接', '').strip()
                code = row.get('代码', stock_code).strip()
                name = row.get('简称', '').strip()

                # 必需字段校验
                if not title:
                    logger.debug(f"巨潮资讯公告缺少标题，跳过")
                    continue

                if not url:
                    logger.debug(f"巨潮资讯公告缺少URL，跳过: {title[:30]}")
                    continue

                # 公告类型推断
                announcement_type = self._infer_announcement_type(title)

                items.append(NewsItem(
                    title=f"[{announcement_type}] {title}",
                    url=url,
                    source='巨潮资讯',
                    content=f"{name}({code}) 发布{announcement_type}公告",
                    published_at=published_at,
                    raw_data={
                        'type': 'disclosure',
                        'provider': 'cninfo',
                        'stock_code': stock_code,
                        'announcement_type': announcement_type
                    }
                ))

            except Exception as e:
                logger.debug(f"解析巨潮资讯公告行数据失败: {e}")
                continue

        logger.debug(f"[{stock_code}] 巨潮资讯公告: {len(items)} 条")
        return items

    def _fetch_tonghuashun_f10_news(
        self,
        stock_code: str,
        stock_name: str = None
    ) -> List[NewsItem]:
        """
        获取同花顺F10新闻（基于网页抓取）

        Args:
            stock_code: 股票代码（如 '600519'）
            stock_name: 股票名称（可选）

        Returns:
            NewsItem 列表
        """
        if not self.web_fetch_enabled:
            logger.debug("网页抓取未启用（缺少 requests 或 beautifulsoup4）")
            return []

        try:
            # 同花顺 F10 新闻页面 URL
            # 格式: https://news.10jqka.com.cn/f10_news_600519/
            f10_url = f"https://news.10jqka.com.cn/f10_news_{stock_code}/"

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            }

            response = requests.get(f10_url, headers=headers, timeout=10)
            response.raise_for_status()

            # 解析 HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            items = []

            # 同花顺新闻列表的解析逻辑
            # 需要根据实际页面结构调整
            news_items = soup.select('.list-item') or soup.select('.news-item') or soup.select('li')

            for item in news_items[:20]:  # 最多获取20条
                try:
                    # 提取标题
                    title_elem = item.select_one('.title a') or item.select_one('a')
                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)
                    url = title_elem.get('href', '')

                    # 处理相对 URL
                    if url and not url.startswith('http'):
                        url = urljoin('https://news.10jqka.com.cn/', url)

                    # 提取时间
                    time_elem = item.select_one('.time') or item.select_one('.date')
                    published_at = time_elem.get_text(strip=True) if time_elem else ''

                    # 提取来源
                    source_elem = item.select_one('.source') or item.select_one('.src')
                    source = source_elem.get_text(strip=True) if source_elem else '同花顺'

                    # 提取摘要
                    content_elem = item.select_one('.desc') or item.select_one('.summary')
                    content = content_elem.get_text(strip=True) if content_elem else ''

                    if title:
                        items.append(NewsItem(
                            title=title,
                            url=url,
                            source=source,
                            content=content,
                            published_at=published_at,
                            raw_data={
                                'type': 'news',
                                'provider': 'tonghuashun',
                                'stock_code': stock_code
                            }
                        ))

                except Exception as e:
                    logger.debug(f"解析同花顺新闻项失败: {e}")
                    continue

            logger.debug(f"[{stock_code}] 同花顺F10新闻: {len(items)} 条")
            return items

        except requests.RequestException as e:
            logger.warning(f"[{stock_code}] 同花顺网络请求失败: {e}")
            return []
        except Exception as e:
            logger.error(f"[{stock_code}] 获取同花顺F10新闻失败: {e}")
            return []

    def _infer_announcement_type(self, title: str) -> str:
        """
        根据公告标题推断公告类型

        Args:
            title: 公告标题

        Returns:
            公告类型标签
        """
        title_lower = title.lower()

        # 优先级从高到低
        type_keywords = [
            ('分红', ['分红', '派息', '股息', '红利']),
            ('业绩', ['业绩', '盈利', '利润', '财报', '报告']),
            ('股东大会', ['股东大会', '临时股东大会', '年会']),
            ('董事会', ['董事会', '监事会']),
            ('重组', ['重组', '并购', '收购']),
            ('融资', ['融资', '增发', '配股', '可转债']),
            ('人事', ['聘任', '辞职', '人事', '高管']),
            ('诉讼', ['诉讼', '仲裁', '案件']),
            ('处罚', ['处罚', '监管', '警示']),
            ('股份', ['股份', '持股', '减持', '增持']),
        ]

        for type_name, keywords in type_keywords:
            if any(kw in title for kw in keywords):
                return type_name

        return '公告'

    def _is_within_date_range(self, published_at: str, cutoff_date: datetime, strict: bool = True) -> bool:
        """
        判断新闻发布时间是否在指定范围内

        Args:
            published_at: 发布时间字符串
            cutoff_date: 截止日期
            strict: 是否严格检查（False则保留所有）

        Returns:
            是否在范围内
        """
        if not strict:
            return True

        try:
            pub_date = self._parse_datetime(published_at)
            return pub_date >= cutoff_date
        except Exception:
            # 如果解析失败，保守返回True（保留该条新闻）
            return True

    def _parse_datetime(self, date_str: str) -> Optional[datetime]:
        """
        解析各种格式的日期字符串

        支持格式：
        - 2023-12-14 15:30:00
        - 2023-12-14
        - 20231214

        Returns:
            解析成功的 datetime 对象，解析失败返回 None
        """
        if not date_str:
            logger.debug("日期字符串为空")
            return None

        # 清理字符串
        date_str = str(date_str).strip()

        # 尝试各种格式
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d',
            '%Y%m%d',
            '%Y/%m/%d %H:%M:%S',
            '%Y/%m/%d',
        ]

        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                # 验证日期合理性：不能是未来日期，不能太旧（超过2年）
                now = datetime.now()
                two_years_ago = now.replace(year=now.year - 2)
                if parsed > now:
                    logger.warning(f"日期是未来时间: {date_str}, 使用当前时间")
                    return now
                if parsed < two_years_ago:
                    logger.debug(f"日期过旧: {date_str}")
                    return parsed  # 保留但标记
                return parsed
            except ValueError:
                continue

        # 如果都失败，记录警告并返回 None（数据无效）
        logger.warning(f"无法解析日期格式: {date_str}, 将此条数据标记为无效")
        return None

    def get_market_sentiment(self, limit: int = 10) -> List[NewsItem]:
        """
        获取市场情绪（热搜、热门话题）

        注意：个股新闻提供者不支持此功能，返回空列表
        """
        logger.warning("StockNewsProvider 不支持市场情绪查询")
        return []

    def get_financial_news(self, limit: int = 10) -> List[NewsItem]:
        """
        获取财经新闻

        注意：个股新闻提供者不支持此功能，返回空列表
        """
        logger.warning("StockNewsProvider 不支持通用财经新闻查询")
        return []

    def search_news(
        self,
        query: str,
        limit: int = 10,
        days: int = 7
    ) -> List[NewsItem]:
        """
        通用新闻搜索

        注意：个股新闻提供者不支持此功能，返回空列表
        """
        logger.warning("StockNewsProvider 不支持通用新闻搜索")
        return []
