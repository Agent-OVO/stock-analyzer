import type React from 'react';
import { useCallback, useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  Newspaper,
  Search,
  TrendingUp,
  Filter,
  RefreshCw,
  FileText,
  Sparkles,
  AlertCircle,
} from 'lucide-react';
import { newsApi, type NewsItem } from '../api/news';
import { NewsCard } from '../components/news/NewsCard';
import { cn } from '../utils/cn';

type NewsCategory = 'sentiment' | 'financial' | 'tech' | 'ai' | 'stock';

const NEWS_CATEGORIES: Record<
  NewsCategory,
  { label: string; icon: React.ReactNode; description: string; color: string }
> = {
  sentiment: {
    label: '市场情绪',
    icon: <TrendingUp className="h-4 w-4" />,
    description: '微博热搜 · 舆情监测',
    color: 'text-orange-500',
  },
  financial: {
    label: '财经新闻',
    icon: <Newspaper className="h-4 w-4" />,
    description: '36Kr · 华尔街见闻 · 腾讯财经',
    color: 'text-blue-500',
  },
  tech: {
    label: '科技动态',
    icon: <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
    </svg>,
    description: 'HackerNews · GitHub · ProductHunt',
    color: 'text-purple-500',
  },
  ai: {
    label: 'AI前沿',
    icon: <Sparkles className="h-4 w-4" />,
    description: 'HuggingFace · Latent Space · AI论文',
    color: 'text-cyan-500',
  },
  stock: {
    label: '个股资讯',
    icon: <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
    </svg>,
    description: '特定股票相关新闻',
    color: 'text-green-500',
  },
};

const NewsPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [activeCategory, setActiveCategory] = useState<NewsCategory>(() => {
    // Initialize from URL or default to 'sentiment'
    const category = searchParams.get('category') as NewsCategory;
    return category && category in NEWS_CATEGORIES ? category : 'sentiment';
  });
  const [newsItems, setNewsItems] = useState<NewsItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [stockCodeInput, setStockCodeInput] = useState(() => searchParams.get('stock') || '');
  const [showStockSearch, setShowStockSearch] = useState(false);
  const [sortBy, setSortBy] = useState<'latest' | 'hot'>(() => {
    const sort = searchParams.get('sort');
    return sort === 'hot' ? 'hot' : 'latest';
  });

  // Set page title
  useEffect(() => {
    document.title = '资讯动态 - DSA';
  }, []);

  // Update URL when category/sort/stock changes
  useEffect(() => {
    const params = new URLSearchParams();
    if (activeCategory !== 'sentiment') params.set('category', activeCategory);
    if (sortBy !== 'latest') params.set('sort', sortBy);
    if (stockCodeInput) params.set('stock', stockCodeInput);
    setSearchParams(params, { replace: true });
  }, [activeCategory, sortBy, stockCodeInput, setSearchParams]);

  const fetchNews = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      let data;
      switch (activeCategory) {
        case 'sentiment':
          data = await newsApi.getMarketSentiment(50);
          break;
        case 'financial':
          data = await newsApi.getFinancialNews(50);
          break;
        case 'tech':
          data = await newsApi.getTechNews(50);
          break;
        case 'ai':
          data = await newsApi.getAINews(50);
          break;
        case 'stock':
          if (stockCodeInput.trim()) {
            data = await newsApi.getStockNews(stockCodeInput.trim(), 50);
          } else {
            data = { items: [], total: 0, source: '', query_time: 0 };
          }
          break;
        default:
          data = { items: [], total: 0, source: '', query_time: 0 };
      }
      setNewsItems(data.items);
    } catch (err) {
      console.error('Failed to fetch news:', err);
      setError('获取新闻失败，请稍后重试');
      setNewsItems([]);
    } finally {
      setIsLoading(false);
    }
  }, [activeCategory, stockCodeInput]);

  useEffect(() => {
    void fetchNews();
  }, [fetchNews]);

  // Handle stock search
  const handleStockSearch = () => {
    if (stockCodeInput.trim()) {
      setActiveCategory('stock');
    }
  };

  // Filter news by search query
  const filteredNews = newsItems.filter((item) => {
    if (!searchQuery.trim()) return true;
    const query = searchQuery.toLowerCase();
    return (
      item.title.toLowerCase().includes(query) ||
      item.content?.toLowerCase().includes(query) ||
      item.tags?.some((tag) => tag.toLowerCase().includes(query))
    );
  });

  // Sort news
  const sortedNews = [...filteredNews].sort((a, b) => {
    if (sortBy === 'hot' && a.heat && b.heat) {
      const heatA = parseInt(a.heat) || 0;
      const heatB = parseInt(b.heat) || 0;
      return heatB - heatA;
    }
    // Default: latest (by published_at if available)
    if (a.published_at && b.published_at) {
      return new Date(b.published_at).getTime() - new Date(a.published_at).getTime();
    }
    return 0;
  });

  return (
    <div className="flex h-[calc(100vh-5rem)] w-full flex-col overflow-hidden sm:h-[calc(100vh-5.5rem)] lg:h-[calc(100vh-2rem)]">
      {/* Header */}
      <header className="flex flex-shrink-0 flex-col gap-4 border-b border-border/70 bg-card/60 px-4 py-4 md:px-6 md:py-5 backdrop-blur-sm">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-purple-500/20 to-cyan-500/20 text-cyan">
              <Newspaper className="h-5 w-5" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-foreground md:text-2xl">资讯动态</h1>
              <p className="text-xs text-secondary-text md:text-sm">
                市场舆情 · 财经新闻 · 科技前沿 · AI动态
              </p>
            </div>
          </div>
        </div>

        {/* Category Tabs */}
        <div className="flex flex-col gap-3">
          <div className="flex gap-1.5 overflow-x-auto pb-1 scrollbar-thin">
            {(Object.keys(NEWS_CATEGORIES) as NewsCategory[]).map((category) => (
              <button
                key={category}
                onClick={() => {
                  setActiveCategory(category);
                  setShowStockSearch(category === 'stock');
                }}
                className={cn(
                  'group relative flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-medium transition-all whitespace-nowrap cursor-pointer',
                  'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan/50 focus-visible:ring-offset-2',
                  activeCategory === category
                    ? 'bg-primary text-primary-foreground shadow-lg shadow-cyan/20'
                    : 'bg-muted text-secondary-text hover:bg-hover hover:text-foreground'
                )}
                aria-label={`切换到${NEWS_CATEGORIES[category].label}`}
                aria-current={activeCategory === category ? 'page' : undefined}
              >
                <span className={activeCategory === category ? '' : NEWS_CATEGORIES[category].color}>
                  {NEWS_CATEGORIES[category].icon}
                </span>
                <span>{NEWS_CATEGORIES[category].label}</span>
                {activeCategory === category && (
                  <span className="absolute inset-0 rounded-xl bg-gradient-to-r from-cyan/20 to-purple/20 opacity-0 group-hover:opacity-100 transition-opacity" />
                )}
              </button>
            ))}
          </div>

          {/* Description + Search Bar */}
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <p className="text-xs text-secondary-text">
              {NEWS_CATEGORIES[activeCategory].description}
            </p>
            <div className="flex items-center gap-2 flex-wrap">
              {/* Stock Search (only visible for stock category) */}
              {showStockSearch && (
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    value={stockCodeInput}
                    onChange={(e) => setStockCodeInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleStockSearch()}
                    placeholder="输入股票代码 (如 600519)"
                    className="input-terminal w-32 px-3 py-2 text-sm focus-visible:ring-2 focus-visible:ring-cyan/50"
                  />
                  <button
                    onClick={handleStockSearch}
                    disabled={!stockCodeInput.trim()}
                    className="btn-primary px-3 py-2 text-sm disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
                  >
                    搜索
                  </button>
                </div>
              )}

              {/* Global Search */}
              <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-secondary-text pointer-events-none" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="搜索新闻..."
                  className="input-terminal pl-9 pr-4 py-2 w-40 sm:w-56 text-sm focus-visible:ring-2 focus-visible:ring-cyan/50"
                />
              </div>

              {/* Sort Toggle */}
              <button
                onClick={() => setSortBy(sortBy === 'latest' ? 'hot' : 'latest')}
                className={cn(
                  'flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium transition-colors cursor-pointer',
                  'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan/50 focus-visible:ring-offset-2',
                  sortBy === 'hot'
                    ? 'bg-orange-500/10 text-orange-500 border border-orange-500/30'
                    : 'bg-muted text-secondary-text hover:bg-hover hover:text-foreground border border-transparent'
                )}
                title={sortBy === 'latest' ? '按热门排序' : '按最新排序'}
                aria-label={`当前排序: ${sortBy === 'latest' ? '最新' : '热门'}`}
              >
                <Filter className="h-4 w-4" />
                <span className="hidden sm:inline">{sortBy === 'latest' ? '最新' : '热门'}</span>
              </button>

              {/* Refresh Button */}
              <button
                onClick={() => void fetchNews()}
                disabled={isLoading}
                className="rounded-lg p-2 text-secondary-text transition-colors hover:bg-hover hover:text-foreground disabled:opacity-50 cursor-pointer focus-visible:ring-2 focus-visible:ring-cyan/50"
                title="刷新"
                aria-label="刷新新闻"
              >
                <RefreshCw className={cn('h-4 w-4', isLoading && 'animate-spin')} />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        <div className="px-4 py-4 md:px-6 md:py-5">
          {isLoading ? (
            <LoadingState />
          ) : error ? (
            <ErrorState error={error} onRetry={() => void fetchNews()} />
          ) : sortedNews.length === 0 ? (
            <EmptyState searchQuery={searchQuery} activeCategory={activeCategory} />
          ) : (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {sortedNews.map((item, index) => (
                <NewsCard key={`${item.url}-${index}`} item={item} index={index} />
              ))}
            </div>
          )}

          {/* Results count */}
          {!isLoading && !error && sortedNews.length > 0 && (
            <div className="mt-6 text-center">
              <p className="text-xs text-secondary-text">
                显示 {sortedNews.length} 条新闻
                {searchQuery && ' (已过滤)'}
              </p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

// Loading State Component
const LoadingState: React.FC = () => (
  <div className="flex h-64 items-center justify-center">
    <div className="flex flex-col items-center gap-4">
      <div className="relative h-16 w-16">
        <div className="absolute inset-0 rounded-full border-4 border-cyan/10" />
        <div className="absolute inset-0 rounded-full border-4 border-cyan border-t-transparent animate-spin" />
        <div className="absolute inset-2 rounded-full bg-gradient-to-br from-cyan/20 to-purple/20 animate-pulse" />
      </div>
      <div className="text-center">
        <p className="text-sm font-medium text-foreground">加载中...</p>
        <p className="text-xs text-secondary-text mt-1">正在获取最新资讯</p>
      </div>
    </div>
  </div>
);

// Error State Component
interface ErrorStateProps {
  error: string;
  onRetry: () => void;
}

const ErrorState: React.FC<ErrorStateProps> = ({ error, onRetry }) => (
  <div className="flex h-64 items-center justify-center">
    <div className="text-center max-w-md">
      <div className="flex justify-center mb-4">
        <div className="flex h-16 w-16 items-center justify-center rounded-xl bg-danger/10">
          <AlertCircle className="h-8 w-8 text-danger" />
        </div>
      </div>
      <h3 className="text-base font-semibold text-foreground mb-2">加载失败</h3>
      <p className="text-sm text-secondary-text mb-4">{error}</p>
      <button
        onClick={onRetry}
        className="btn-primary px-6 py-2.5 text-sm cursor-pointer focus-visible:ring-2 focus-visible:ring-cyan/50"
      >
        重试
      </button>
    </div>
  </div>
);

// Empty State Component
interface EmptyStateProps {
  searchQuery: string;
  activeCategory: NewsCategory;
}

const EmptyState: React.FC<EmptyStateProps> = ({ searchQuery, activeCategory }) => {
  if (searchQuery) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="text-center">
          <Search className="mx-auto mb-3 h-12 w-12 text-muted-text" />
          <h3 className="text-base font-medium text-foreground mb-1">未找到匹配结果</h3>
          <p className="text-sm text-secondary-text">
            搜索 &quot;<span className="text-foreground">{searchQuery}</span>&quot; 没有找到相关新闻
          </p>
        </div>
      </div>
    );
  }

  if (activeCategory === 'stock') {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="text-center">
          <FileText className="mx-auto mb-3 h-12 w-12 text-muted-text" />
          <h3 className="text-base font-medium text-foreground mb-1">请输入股票代码</h3>
          <p className="text-sm text-secondary-text">
            在上方输入股票代码（如 600519）查看相关资讯
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-64 items-center justify-center">
      <div className="text-center">
        <Newspaper className="mx-auto mb-3 h-12 w-12 text-muted-text" />
        <h3 className="text-base font-medium text-foreground mb-1">暂无新闻</h3>
        <p className="text-sm text-secondary-text">
          {NEWS_CATEGORIES[activeCategory].label}分类下暂时没有新闻
        </p>
      </div>
    </div>
  );
};

export default NewsPage;
