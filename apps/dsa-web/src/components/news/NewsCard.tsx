import type React from 'react';
import { ExternalLink, Clock, Tag } from 'lucide-react';
import type { NewsItem } from '../../api/news';
import { cn } from '../../utils/cn';

interface NewsCardProps {
  item: NewsItem;
  index?: number;
}

export const NewsCard: React.FC<NewsCardProps> = ({ item, index = 0 }) => {
  const handleTitleClick = () => {
    if (item.url) {
      window.open(item.url, '_blank', 'noopener,noreferrer');
    }
  };

  // Stagger animation based on index
  const animationDelay = `${Math.min(index * 50, 300)}ms`;

  return (
    <article
      className={cn(
        'group relative flex flex-col gap-3 rounded-xl border border-border bg-card/80 p-4',
        'transition-all duration-250 ease-out',
        'hover:border-cyan/30 hover:shadow-lg hover:shadow-cyan/5 hover:-translate-y-0.5',
        'cursor-pointer',
        // Focus visible for keyboard navigation
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan/50 focus-visible:ring-offset-2',
        // Animation on mount
        'animate-fade-in opacity-0'
      )}
      style={{ animationDelay, animationFillMode: 'forwards' }}
      onClick={handleTitleClick}
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          handleTitleClick();
        }
      }}
      aria-label={`阅读新闻: ${item.title}`}
    >
      {/* Header with title and heat indicator */}
      <div className="flex items-start gap-3">
        <h3
          className="flex-1 text-sm font-medium leading-snug text-foreground transition-colors group-hover:text-cyan line-clamp-2"
          title={item.title}
        >
          {item.title}
        </h3>
        {item.heat && (
          <span
            className={cn(
              'flex-shrink-0 rounded-full px-2 py-0.5 text-xs font-medium transition-colors',
              'bg-orange-500/10 text-orange-500 border border-orange-500/20',
              'group-hover:bg-orange-500/20'
            )}
            aria-label={`热度: ${item.heat}`}
          >
            🔥 {item.heat}
          </span>
        )}
      </div>

      {/* Content snippet */}
      {item.content && (
        <p className="text-xs text-secondary-text line-clamp-2 leading-relaxed">
          {item.content}
        </p>
      )}

      {/* Tags */}
      {item.tags && item.tags.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {item.tags.slice(0, 3).map((tag, tagIndex) => (
            <span
              key={tagIndex}
              className={cn(
                'inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-xs',
                'bg-primary/10 text-primary border border-primary/20',
                'transition-colors group-hover:bg-primary/15'
              )}
            >
              <Tag className="h-3 w-3" />
              {tag}
            </span>
          ))}
        </div>
      )}

      {/* Footer with source and time */}
      <div className={cn(
        'flex items-center justify-between gap-2 pt-2 border-t border-border/50',
        'text-xs text-muted-text'
      )}>
        <div className="flex items-center gap-2">
          <span className="rounded-md bg-muted px-2 py-0.5 font-medium text-secondary-text">
            {item.source}
          </span>
          {item.published_at && (
            <span className="flex items-center gap-1" aria-label={`发布时间: ${item.published_at}`}>
              <Clock className="h-3 w-3" />
              {item.published_at}
            </span>
          )}
        </div>

        {/* External link indicator */}
        <span
          className={cn(
            'flex items-center gap-1 text-muted-text opacity-0 transition-opacity',
            'group-hover:opacity-100'
          )}
        >
          <ExternalLink className="h-3.5 w-3.5" />
        </span>
      </div>

      {/* Hover glow effect */}
      <span
        className={cn(
          'absolute inset-0 rounded-xl opacity-0 transition-opacity duration-300',
          'pointer-events-none',
          'bg-gradient-to-br from-cyan/5 via-transparent to-purple/5',
          'group-hover:opacity-100'
        )}
        aria-hidden="true"
      />
    </article>
  );
};
