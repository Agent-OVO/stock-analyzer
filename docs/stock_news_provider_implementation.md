# 个股新闻源功能实施文档

## 一、功能概述

本次实施为股票分析系统添加了**专用个股新闻提供者（StockNewsProvider）**，解决了历史分析报告中资讯不准确的问题。

### 新增功能

1. **东方财富个股新闻**：实时获取个股相关市场新闻和媒体报道
2. **巨潮资讯官方公告**：获取公司发布的官方公告（分红、股东大会、财报等）
3. **同花顺F10新闻**（实验性）：基于网页抓取的个股新闻
4. **公告类型智能识别**：自动分类公告类型（分红、业绩、重组、人事等）
5. **API响应校验**：结构化验证API返回数据的完整性和正确性
6. **自动重试机制**：网络请求失败时自动重试，提升稳定性
7. **优先级自动切换**：个股新闻优先，降级到通用新闻源

### 文件变更

| 文件路径 | 操作 | 说明 |
|---------|------|------|
| `src/news_service/stock_news_provider.py` | 新增 | 专用个股新闻提供者核心实现，含API校验和重试 |
| `src/news_service/factory.py` | 修改 | 注册新的提供者，设置优先级 |
| `src/services/history_service.py` | 修改 | 使用新的提供者作为首选兜底 |
| `tests/test_stock_news_provider.py` | 新增 | 单元测试 |
| `requirements.txt` | 修改 | 添加 beautifulsoup4 依赖 |
| `docs/stock_news_provider_implementation.md` | 新增 | 本实施文档 |

## 二、API 数据源

### 1. 东方财富个股新闻

- **API**: `akshare.stock_news_em(symbol)`
- **内容**: 市场新闻、媒体报道、分析文章
- **数量**: ~100条
- **更新频率**: 实时
- **字段**: 标题、内容、发布时间、来源、链接

### 2. 巨潮资讯官方公告

- **API**: `akshare.stock_zh_a_disclosure_report_cninfo(symbol)`
- **内容**: 公司正式公告（官方披露平台）
- **数量**: 35条
- **公告类型识别**:
  - 分红类（分红、派息、股息）
  - 业绩类（财报、盈利、利润）
  - 股东大会
  - 董事会/监事会
  - 重组、融资、人事、诉讼等

### 3. 同花顺F10新闻（实验性）

- **方式**: 基于网页抓取 (requests + BeautifulSoup)
- **URL**: `https://news.10jqka.com.cn/f10_news_{stock_code}/`
- **状态**: 非致命功能，失败不影响其他数据源
- **注意**: URL格式可能变化，如遇404错误会自动跳过

## 三、使用方式

### 自动启用（推荐）

系统会自动使用新的提供者，无需额外配置：

```python
# 历史服务查询时自动使用
from src.services.history_service import HistoryService

service = HistoryService()
news_items = service.get_news_intel(query_id="xxx", limit=20)
# 优先使用 StockNewsProvider 获取个股专属资讯
```

### 手动使用

```python
from src.news_service.factory import NewsProviderFactory

# 获取个股新闻提供者
provider = NewsProviderFactory.create('stock_news')

# 搜索个股资讯
items = provider.search_stock_news(
    stock_code='600519',
    stock_name='贵州茅台',
    days=7,    # 最近7天
    limit=20   # 最多20条
)

# 遍历资讯
for item in items:
    print(f"标题: {item.title}")
    print(f"来源: {item.source}")
    print(f"时间: {item.published_at}")
    print(f"链接: {item.url}")

    # 检查资讯类型
    if item.raw_data:
        data_type = item.raw_data.get('type')  # 'news' 或 'disclosure'
        provider = item.raw_data.get('provider')  # 'eastmoney' 或 'cninfo'

        if data_type == 'disclosure':
            announcement_type = item.raw_data.get('announcement_type')
            print(f"公告类型: {announcement_type}")
```

## 四、优先级策略

系统按以下优先级选择新闻源：

1. **StockNewsProvider** （新增，最高优先级）
   - 专用个股新闻 + 官方公告
   - 免费使用

2. **NewsAggregatorProvider**
   - 36氪、华尔街见闻、腾讯科技
   - 免费使用

3. **SearchAPIProvider** (Bocha/Tavily/SerpAPI等)
   - 需要API Key
   - 搜索引擎结果

## 五、配置要求

### 环境依赖

```bash
pip install akshare
pip install beautifulsoup4  # 用于同花顺F10新闻抓取（可选）
```

### 增强特性

1. **API响应校验**
   - 校验返回类型是否为 DataFrame
   - 校验必需字段是否存在
   - 校验数据是否为空
   - 校验失败会记录详细日志并返回空结果

2. **自动重试机制**
   - 每个API调用最多重试2次
   - 重试间隔1秒
   - 所有重试失败后记录错误日志

3. **日期解析增强**
   - 支持多种日期格式（2023-12-14、20231214等）
   - 验证日期合理性（非未来日期）
   - 解析失败返回None并过滤，避免数据污染

### 无需额外配置

- 不需要API Key
- 不需要注册账号
- 不需要配置环境变量

## 六、性能说明

| 操作 | 预计耗时 | 说明 |
|------|----------|------|
| 获取东方财富新闻 | 2-5秒 | 网络请求+解析 |
| 获取巨潮资讯公告 | 1-3秒 | 网络请求+解析 |
| 总计 | 3-8秒 | 并发请求 |

### 缓存策略

- 历史服务会缓存查询结果到数据库
- 重复查询直接返回缓存，无需重新请求

## 七、测试验证

### 运行测试

```bash
cd D:\Project\股票智能分析系统
python tests/test_stock_news_provider.py
```

### 预期输出

```
============================================================
测试专用个股新闻提供者
============================================================

1. 提供者名称: StockNews
2. 是否可用: True

3. 测试获取 贵州茅台(600519) 的资讯...

[OK] 获取到 15 条资讯

   - 东方财富新闻: 10 条
   - 巨潮资讯公告: 5 条

============================================================
资讯 1:
  标题: 贵州茅台缺席春糖酒店展，仅在主会场设展
  来源: 红星资本局
  时间: 2026-03-22 15:41:00
  类型: news (eastmoney)
...
```

## 八、问题排查

### 问题1：akshare未安装

**现象**：`StockNewsProvider 不可用`

**解决**：
```bash
pip install akshare
```

### 问题2：获取不到资讯

**可能原因**：
- 网络连接问题
- API限流
- 股票代码格式错误

**排查步骤**：
1. 检查股票代码格式（纯数字，如 '600519'）
2. 查看日志中的错误信息
3. 手动测试API：
   ```python
   import akshare as ak
   df = ak.stock_news_em(symbol='600519')
   print(df.head())
   ```

### 问题3：公告都是旧的

**原因**：巨潮资讯API返回的数据有限，可能包含较旧的公告

**当前策略**：保留最近的公告不过滤，确保用户能看到公司重要公告

## 九、后续优化建议

1. **修复同花顺F10新闻**
   - 当前URL格式返回404，需要调研新的URL格式
   - 可能需要使用同花顺API或调整抓取策略

2. **增加更多数据源**
   - 新浪个股公告
   - 网易财经新闻
   - 新浪个股公告

2. **智能去重**
   - 根据URL去重
   - 根据标题相似度去重

3. **时间范围优化**
   - 允许用户自定义时间范围
   - 支持按日期筛选

4. **缓存优化**
   - 增加Redis缓存
   - 设置缓存过期时间

## 十、版本记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.1.0 | 2026-03-24 | 增强版：添加API响应校验、自动重试机制、同花顺F10新闻（实验性） |
| v1.0.0 | 2026-03-24 | 初始版本，支持东方财富新闻和巨潮资讯公告 |
