import { useTranslations } from 'next-intl';
import { setRequestLocale } from 'next-intl/server';
import { locales, type Locale } from '../../../i18n';
import { getAllArticles } from '../../../lib/articles';
import ArticleCard from '../../../components/ArticleCard';

interface Props { params: { locale: Locale } }

export function generateStaticParams() {
  return locales.map(locale => ({ locale }));
}

export default function ArticlesPage({ params: { locale } }: Props) {
  setRequestLocale(locale);
  const t = useTranslations('articles');
  const articles = getAllArticles(locale);

  const categories = ['All', ...Array.from(new Set(
    articles.map(a => a.category).filter(Boolean) as string[]
  ))];

  return (
    <div style={{ maxWidth: '1120px', margin: '0 auto', padding: '64px 24px' }}>

      {/* Header */}
      <div style={{ marginBottom: '56px', maxWidth: '640px' }}>
        <span style={{
          fontFamily: 'JetBrains Mono, monospace',
          fontSize: '0.7rem', textTransform: 'uppercase',
          letterSpacing: '0.1em', color: '#C9973A', display: 'block',
          marginBottom: '14px',
        }}>
          Writing
        </span>
        <h1 style={{
          fontFamily: 'Playfair Display, Georgia, serif',
          fontSize: 'clamp(2rem, 5vw, 3.4rem)',
          fontWeight: 600, lineHeight: 1.1,
          letterSpacing: '-0.03em', color: '#F2EDE4',
          marginBottom: '16px',
        }}>
          {t('title')}
        </h1>
        <div style={{ width: '40px', height: '2px', background: '#C9973A', marginBottom: '20px' }} />
        <p style={{
          fontFamily: 'Source Serif 4, Georgia, serif',
          fontSize: '1rem', color: '#B8B0A4', lineHeight: 1.7,
        }}>
          {t('subtitle')}
        </p>
      </div>

      {/* Category filter pills */}
      {categories.length > 1 && (
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '36px' }}>
          {categories.map(cat => (
            <span key={cat} style={{
              fontFamily: 'JetBrains Mono, monospace',
              fontSize: '0.7rem', letterSpacing: '0.06em',
              textTransform: 'uppercase', padding: '5px 14px',
              border: '1px solid #3A3730', borderRadius: '2px',
              color: cat === 'All' ? '#C9973A' : '#6B6560',
              background: cat === 'All' ? 'rgba(201,151,58,0.08)' : 'transparent',
              cursor: 'pointer',
            }}>
              {cat}
            </span>
          ))}
        </div>
      )}

      {/* Articles grid */}
      {articles.length === 0 ? (
        <div style={{
          textAlign: 'center', padding: '80px 0',
          fontFamily: 'JetBrains Mono, monospace',
          fontSize: '0.85rem', color: '#6B6560',
        }}>
          Articles coming soon.
        </div>
      ) : (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))',
          gap: '16px',
        }}>
          {articles.map((article, i) => (
            <ArticleCard key={article.slug} article={article} locale={locale} index={i} />
          ))}
        </div>
      )}
    </div>
  );
}
