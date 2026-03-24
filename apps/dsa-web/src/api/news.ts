import apiClient from './index';

export interface NewsItem {
  title: string;
  url: string;
  source: string;
  content?: string;
  published_at?: string;
  heat?: string;
  tags?: string[];
}

export interface NewsSearchResult {
  items: NewsItem[];
  total: number;
  source: string;
  query_time: number;
}

export interface NewsProvidersResponse {
  current: {
    name: string;
    available: boolean;
    type: string;
  };
  available: Record<string, boolean>;
}

export const newsApi = {
  getProviders: async (): Promise<NewsProvidersResponse> => {
    const response = await apiClient.get<NewsProvidersResponse>('/api/v1/news/providers');
    return response.data;
  },

  getMarketSentiment: async (limit = 10): Promise<NewsSearchResult> => {
    const response = await apiClient.get<NewsSearchResult>('/api/v1/news/sentiment', {
      params: { limit }
    });
    return response.data;
  },

  getFinancialNews: async (limit = 10): Promise<NewsSearchResult> => {
    const response = await apiClient.get<NewsSearchResult>('/api/v1/news/financial', {
      params: { limit }
    });
    return response.data;
  },

  getStockNews: async (stockCode: string, limit = 10): Promise<NewsSearchResult> => {
    const response = await apiClient.get<NewsSearchResult>(`/api/v1/news/stock/${stockCode}`, {
      params: { limit }
    });
    return response.data;
  },

  searchNews: async (query: string, limit = 10): Promise<NewsSearchResult> => {
    const response = await apiClient.get<NewsSearchResult>('/api/v1/news/search', {
      params: { query, limit }
    });
    return response.data;
  },

  getTechNews: async (limit = 10): Promise<NewsSearchResult> => {
    const response = await apiClient.get<NewsSearchResult>('/api/v1/news/tech', {
      params: { limit }
    });
    return response.data;
  },

  getAINews: async (limit = 10): Promise<NewsSearchResult> => {
    const response = await apiClient.get<NewsSearchResult>('/api/v1/news/ai', {
      params: { limit }
    });
    return response.data;
  },
};
