# -*- coding: utf-8 -*-
"""
===================================
测试专用个股新闻提供者
===================================
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.news_service.stock_news_provider import StockNewsProvider


def test_stock_news_provider():
    """测试个股新闻提供者"""
    print("=" * 60)
    print("测试专用个股新闻提供者")
    print("=" * 60)

    provider = StockNewsProvider()

    # 检查可用性
    print(f"\n1. 提供者名称: {provider.get_name()}")
    print(f"2. 是否可用: {provider.is_available()}")

    if not provider.is_available():
        print("\n[ERROR] 提供者不可用，请确保已安装 akshare: pip install akshare")
        return

    # 测试获取个股新闻（贵州茅台）
    stock_code = "600519"
    stock_name = "贵州茅台"

    print(f"\n3. 测试获取 {stock_name}({stock_code}) 的资讯...")
    news_items = provider.search_stock_news(
        stock_code=stock_code,
        stock_name=stock_name,
        days=30,  # 获取最近30天
        limit=15  # 最多15条
    )

    print(f"\n[OK] 获取到 {len(news_items)} 条资讯\n")

    # 分类统计
    news_count = sum(1 for item in news_items if item.raw_data and item.raw_data.get('type') == 'news')
    disclosure_count = sum(1 for item in news_items if item.raw_data and item.raw_data.get('type') == 'disclosure')

    print(f"   - 东方财富新闻: {news_count} 条")
    print(f"   - 巨潮资讯公告: {disclosure_count} 条")
    print()

    # 显示前5条
    for i, item in enumerate(news_items[:5], 1):
        print(f"{'=' * 60}")
        print(f"资讯 {i}:")
        print(f"  标题: {item.title}")
        print(f"  来源: {item.source}")
        print(f"  时间: {item.published_at}")

        if item.raw_data:
            data_type = item.raw_data.get('type', '')
            provider_name = item.raw_data.get('provider', '')
            print(f"  类型: {data_type} ({provider_name})")

            if data_type == 'disclosure':
                announcement_type = item.raw_data.get('announcement_type', '')
                print(f"  公告类型: {announcement_type}")

        if item.content and len(item.content) > 100:
            content_preview = item.content[:100] + "..."
        else:
            content_preview = item.content or ""
        print(f"  内容: {content_preview}")

        if item.url:
            print(f"  链接: {item.url}")

    print(f"\n{'=' * 60}")
    print(f"[SUCCESS] 测试完成")


def test_different_stocks():
    """测试不同股票"""
    print("\n" + "=" * 60)
    print("测试不同股票的新闻获取")
    print("=" * 60)

    provider = StockNewsProvider()

    test_stocks = [
        ("000001", "平安银行"),
        ("000002", "万科A"),
        ("600000", "浦发银行"),
    ]

    for code, name in test_stocks:
        print(f"\n测试 {name}({code})...")
        items = provider.search_stock_news(
            stock_code=code,
            stock_name=name,
            days=7,
            limit=5
        )
        print(f"  获取到 {len(items)} 条资讯")

        if items:
            for item in items[:2]:
                print(f"    - {item.title[:50]}...")


if __name__ == "__main__":
    test_stock_news_provider()
    test_different_stocks()
