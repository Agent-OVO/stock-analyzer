import type React from 'react';
import { useCallback, useEffect, useState } from 'react';
import { newsApi } from '../../api/news';
import type { NewsItem } from '../../api/news';
import { NewsCard } from './NewsCard';

type NewsTab = 'sentiment' | 'financial' | 'tech' | 'ai';

const NEWS_TABS: Record<NewsTab, { label: string; description: string }> = {
  sentiment: { label: '市场情绪', description: '微博热搜' },
  financial: { label: '财经新闻', description: '36Kr · 华尔街见闻 · 腾讯' },
  tech: { label: '科技动态', description: 'HackerNews · GitHub · ProductHunt' },
  ai: { label: 'AI前沿', description: 'HuggingFace · Latent Space' },
};

interface NewsListProps {
  stockCode?: string;
  limit?: number;
  className?: string;
}

export const NewsList: React.FC<NewsListProps> = ({ stockCode: _stockCode, limit = 10, className = '' }) => {
  const [activeTab, setActiveTab] = useState<NewsTab>('sentiment');
  const [newsItems, setNewsItems] = useState<NewsItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchNews = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      let data;
      switch (activeTab) {
        case 'sentiment':
          data = await newsApi.getMarketSentiment(limit);
          break;
        case 'financial':
          data = await newsApi.getFinancialNews(limit);
          break;
        case 'tech':
          data = await newsApi.getTechNews(limit);
          break;
        case 'ai':
          data = await newsApi.getAINews(limit);
          break;
        default:
          data = { items: [], total: 0, source: '', query_time: 0 };
      }
      setNewsItems(data.items);
    } catch (err) {
      console.error('Failed to fetch news:', err);
      setError('获取新闻失败');
      setNewsItems([]);
    } finally {
      setIsLoading(false);
    }
  }, [activeTab, limit]);

  useEffect(() => {
    void fetchNews();
  }, [fetchNews]);

  return (
    <div className={`flex flex-col ${className}`}>
      {/* Header with tabs */}
      <div className="mb-3 flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-foreground">资讯动态</h3>
          <button
            onClick={() => void fetchNews()}
            disabled={isLoading}
            className="rounded-lg p-1.5 text-secondary-text transition-colors hover:bg-hover hover:text-foreground disabled:opacity-50"
            title="刷新"
          >
            <svg
              className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
              />
            </svg>
          </button>
        </div>

        {/* Tabs */}
        <div className="flex gap-1 overflow-x-auto pb-1">
          {(Object.keys(NEWS_TABS) as NewsTab[]).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`
                rounded-lg px-3 py-1.5 text-sm font-medium transition-colors whitespace-nowrap
                ${
                  activeTab === tab
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted text-secondary-text hover:bg-hover hover:text-foreground'
                }
              `}
            >
              {NEWS_TABS[tab].label}
            </button>
          ))}
        </div>

        {/* Description */}
        <p className="text-xs text-secondary-text">{NEWS_TABS[activeTab].description}</p>
      </div>

      {/* News content */}
      <div className="flex-1 overflow-y-auto">
        {isLoading ? (
          <div className="flex h-40 items-center justify-center">
            <div className="flex flex-col items-center gap-2 text-secondary-text">
              <svg className="h-6 w-6 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              <span className="text-sm">加载中...</span>
            </div>
          </div>
        ) : error ? (
          <div className="flex h-40 items-center justify-center">
            <p className="text-sm text-danger">{error}</p>
          </div>
        ) : newsItems.length === 0 ? (
          <div className="flex h-40 items-center justify-center">
            <p className="text-sm text-secondary-text">暂无新闻</p>
          </div>
        ) : (
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-1">
            {newsItems.map((item, index) => (
              <NewsCard key={`${item.url}-${index}`} item={item} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
