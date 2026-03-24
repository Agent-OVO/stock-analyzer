import type React from 'react';
import type { NewsItem } from '../../api/news';

interface NewsCardProps {
  item: NewsItem;
}

export const NewsCard: React.FC<NewsCardProps> = ({ item }) => {
  const handleTitleClick = () => {
    if (item.url) {
      window.open(item.url, '_blank', 'noopener,noreferrer');
    }
  };

  return (
    <div className="group flex flex-col gap-2 rounded-lg border border-border bg-card p-3 transition-all hover:border-primary/50 hover:shadow-md">
      <div className="flex items-start justify-between gap-2">
        <h4
          onClick={handleTitleClick}
          className="flex-1 text-sm font-medium leading-snug text-foreground transition-colors group-hover:text-primary cursor-pointer line-clamp-2"
          title={item.title}
        >
          {item.title}
        </h4>
        {item.heat && (
          <span className="flex-shrink-0 rounded-full bg-orange-100 px-2 py-0.5 text-xs font-medium text-orange-600 dark:bg-orange-900/30 dark:text-orange-400">
            🔥 {item.heat}
          </span>
        )}
      </div>

      <div className="flex items-center gap-2 text-xs text-secondary-text">
        <span className="rounded bg-muted px-1.5 py-0.5 font-medium">{item.source}</span>
        {item.published_at && (
          <span>{item.published_at}</span>
        )}
      </div>

      {item.content && (
        <p className="text-xs text-secondary-text line-clamp-2">
          {item.content}
        </p>
      )}

      {item.tags && item.tags.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {item.tags.map((tag, index) => (
            <span
              key={index}
              className="rounded bg-primary/10 px-1.5 py-0.5 text-xs text-primary"
            >
              {tag}
            </span>
          ))}
        </div>
      )}
    </div>
  );
};
