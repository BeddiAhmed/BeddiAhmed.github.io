import Link from 'next/link';
import type { ArticleMeta } from '../lib/articles';
import type { Locale } from '../i18n';

interface Props { article: ArticleMeta; locale: Locale; index?: number; }

const CAT_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  economics: { bg:'#EFF4FA', text:'#1A3A5C', border:'transparent' },
  energy:    { bg:'#EEF8F3', text:'#1A6644', border:'transparent' },
  trade:     { bg:'#FBF5E9', text:'#B8821E', border:'transparent' },
  finance:   { bg:'#FEF2F2', text:'#B83232', border:'transparent' },
  default:   { bg:'#F7F6F3', text:'#48484F', border:'transparent' },
};

export default function ArticleCard({ article, locale, index = 0 }: Props) {
  const cat = CAT_COLORS[article.category?.toLowerCase() ?? 'default'] ?? CAT_COLORS.default;

  return (
    <Link href={`/${locale}/articles/${article.slug}`} style={{ textDecoration: 'none', display: 'block' }}>
      <article style={{
        background: 'var(--bg)',
        border: '1px solid var(--border)',
        borderRadius: '6px',
        padding: '24px',
        display: 'flex', flexDirection: 'column', gap: '10px',
        height: '100%',
        transition: 'border-color .18s, box-shadow .18s, transform .18s',
        animationDelay: `${index * 0.07}s`,
        cursor: 'pointer',
      }}
        className="animate-fade-up article-card"
      >
        {/* Category + date row */}
        <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', gap:'8px' }}>
          {article.category && (
            <span style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '0.67rem', letterSpacing: '0.07em',
              textTransform: 'uppercase', fontWeight: 500,
              padding: '2px 8px', borderRadius: '3px',
              background: cat.bg, color: cat.text,
            }}>
              {article.category}
            </span>
          )}
          <span style={{
            fontFamily: 'var(--font-mono)',
            fontSize: '0.69rem', color: 'var(--muted)',
            marginInlineStart: 'auto', whiteSpace: 'nowrap',
          }}>
            {article.date}{article.readTime ? ` · ${article.readTime}m` : ''}
          </span>
        </div>

        {/* Title */}
        <h3 style={{
          fontFamily: 'var(--font-display)',
          fontSize: '1.1rem', fontWeight: 600,
          color: 'var(--text)', lineHeight: 1.3,
          letterSpacing: '-0.015em',
        }}>
          {article.title}
        </h3>

        {/* Excerpt */}
        {article.excerpt && (
          <p style={{
            fontFamily: 'var(--font-body)',
            fontSize: '0.875rem', color: 'var(--text-2)',
            lineHeight: 1.65, flex: 1,
          }}>
            {article.excerpt}
          </p>
        )}

        {/* Read link */}
        <div style={{
          fontFamily: 'var(--font-body)',
          fontSize: '0.82rem', fontWeight: 500,
          color: 'var(--accent)',
          display: 'flex', alignItems: 'center', gap: '4px',
          marginTop: '4px',
        }}>
          Read article <span style={{ transition: 'transform .15s' }} className="card-arrow">→</span>
        </div>
      </article>

      <style>{`
        .article-card:hover {
          border-color: var(--accent) !important;
          box-shadow: 0 4px 20px rgba(26,58,92,.07);
          transform: translateY(-2px);
        }
        .article-card:hover .card-arrow { transform: translateX(3px); }
      `}</style>
    </Link>
  );
}
