import { notFound } from 'next/navigation';
import Link from 'next/link';
import { setRequestLocale } from 'next-intl/server';
import { locales, type Locale } from '../../../../i18n';
import { getArticle, getArticleSlugs, getAllArticles } from '../../../../lib/articles';

interface Props {
  params: { locale: Locale; slug: string };
}

export async function generateStaticParams() {
  const params: { locale: Locale; slug: string }[] = [];
  for (const locale of locales) {
    const slugs = getArticleSlugs(locale);
    slugs.forEach(slug => params.push({ locale, slug }));
  }
  return params;
}

export default async function ArticlePage({ params: { locale, slug } }: Props) {
  setRequestLocale(locale);
  const article = await getArticle(slug, locale);
  if (!article) notFound();

  // Related articles (same category, different slug)
  const related = getAllArticles(locale)
    .filter(a => a.slug !== slug && a.category === article.category)
    .slice(0, 2);

  const isRtl = locale === 'ar';

  return (
    <div style={{ maxWidth: '1120px', margin: '0 auto', padding: '56px 24px 80px' }}>
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr min(72ch, 100%) 1fr',
        gap: '0 32px',
      }}>

        {/* ── LEFT SIDEBAR — Back + TOC placeholder ── */}
        <aside style={{
          gridColumn: '1',
          paddingTop: '8px',
          display: 'flex', flexDirection: 'column', gap: '24px',
        }}
          className="sidebar-left"
        >
          <Link href={`/${locale}/articles`} style={{
            fontFamily: 'JetBrains Mono, monospace',
            fontSize: '0.75rem', color: '#6B6560',
            textDecoration: 'none', letterSpacing: '0.04em',
            display: 'flex', alignItems: 'center', gap: '6px',
            whiteSpace: 'nowrap',
          }}>
            ← Articles
          </Link>

          {/* Language switcher */}
          <div>
            <p style={{
              fontFamily: 'JetBrains Mono, monospace',
              fontSize: '0.65rem', textTransform: 'uppercase',
              letterSpacing: '0.1em', color: '#6B6560', marginBottom: '8px',
            }}>
              Language
            </p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              {(locales as readonly Locale[]).map(loc => (
                <Link key={loc} href={`/${loc}/articles/${slug}`} style={{
                  fontFamily: 'JetBrains Mono, monospace',
                  fontSize: '0.75rem', letterSpacing: '0.05em',
                  textTransform: 'uppercase',
                  color: loc === locale ? '#C9973A' : '#6B6560',
                  textDecoration: 'none',
                  padding: '4px 10px',
                  border: loc === locale ? '1px solid #7A5A22' : '1px solid transparent',
                  borderRadius: '2px',
                  background: loc === locale ? 'rgba(201,151,58,0.08)' : 'transparent',
                }}>
                  {loc === 'en' ? 'English' : loc === 'fr' ? 'Français' : 'العربية'}
                </Link>
              ))}
            </div>
          </div>
        </aside>

        {/* ── MAIN CONTENT ── */}
        <article style={{ gridColumn: '2' }}>

          {/* Category + date */}
          <div style={{
            display: 'flex', gap: '10px', alignItems: 'center',
            flexWrap: 'wrap', marginBottom: '24px',
          }}>
            {article.category && (
              <span style={{
                fontFamily: 'JetBrains Mono, monospace',
                fontSize: '0.68rem', textTransform: 'uppercase',
                letterSpacing: '0.08em', color: '#C9973A',
                background: 'rgba(201,151,58,0.08)',
                border: '1px solid rgba(201,151,58,0.3)',
                padding: '3px 10px', borderRadius: '2px',
              }}>
                {article.category}
              </span>
            )}
            <span style={{
              fontFamily: 'JetBrains Mono, monospace',
              fontSize: '0.7rem', color: '#6B6560',
            }}>
              {article.date}
              {article.readTime && <> · {article.readTime} min read</>}
            </span>
          </div>

          {/* Title */}
          <h1 style={{
            fontFamily: 'Playfair Display, Georgia, serif',
            fontSize: 'clamp(1.9rem, 4vw, 2.8rem)',
            fontWeight: 600, lineHeight: 1.12,
            letterSpacing: '-0.025em', color: '#F2EDE4',
            marginBottom: '20px',
          }}>
            {article.title}
          </h1>

          {/* Gold rule */}
          <div style={{ width: '40px', height: '2px', background: '#C9973A', marginBottom: '32px' }} />

          {/* Tags */}
          {article.tags && article.tags.length > 0 && (
            <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', marginBottom: '40px' }}>
              {article.tags.map(tag => (
                <span key={tag} style={{
                  fontFamily: 'JetBrains Mono, monospace',
                  fontSize: '0.65rem', color: '#6B6560',
                  background: '#1C1A17', border: '1px solid #2A2720',
                  padding: '2px 8px', borderRadius: '2px',
                  letterSpacing: '0.04em',
                }}>
                  {tag}
                </span>
              ))}
            </div>
          )}

          {/* Prose content */}
          <div
            className="prose-article"
            dir={isRtl ? 'rtl' : 'ltr'}
            dangerouslySetInnerHTML={{ __html: article.content }}
          />

          {/* Dashboard embed (if article has one configured) */}
          {article.dashboard && (
            <div style={{ margin: '48px 0' }}>
              <p style={{
                fontFamily: 'JetBrains Mono, monospace',
                fontSize: '0.72rem', textTransform: 'uppercase',
                letterSpacing: '0.1em', color: '#C9973A', marginBottom: '12px',
              }}>
                Interactive Dashboard
              </p>
              <div style={{
                border: '1px solid #2A2720', borderRadius: '4px', overflow: 'hidden',
              }}>
                <iframe
                  src="/dashboards/dashboard.html"
                  width="100%"
                  height="900"
                  style={{ border: 'none', display: 'block' }}
                  title="Energy Crisis Dashboard"
                />
              </div>
              <p style={{
                fontFamily: 'JetBrains Mono, monospace',
                fontSize: '0.7rem', color: '#6B6560', marginTop: '8px',
              }}>
                Fig. — Interactive charts. Hover to explore. Sources: FRED, World Bank, UN COMTRADE, IMF WEO.
              </p>
            </div>
          )}

          {/* Article footer */}
          <div style={{
            marginTop: '56px', paddingTop: '32px',
            borderTop: '1px solid #2A2720',
            display: 'flex', justifyContent: 'space-between',
            alignItems: 'flex-start', flexWrap: 'wrap', gap: '20px',
          }}>
            <div>
              <p style={{
                fontFamily: 'JetBrains Mono, monospace',
                fontSize: '0.68rem', textTransform: 'uppercase',
                letterSpacing: '0.1em', color: '#6B6560', marginBottom: '4px',
              }}>
                Author
              </p>
              <p style={{
                fontFamily: 'Playfair Display, Georgia, serif',
                fontSize: '1rem', color: '#F2EDE4',
              }}>
                Ahmed
              </p>
              <p style={{
                fontFamily: 'JetBrains Mono, monospace',
                fontSize: '0.75rem', color: '#6B6560',
              }}>
                M.Sc. Economics
              </p>
            </div>
            <Link href={`/${locale}/articles`} style={{
              fontFamily: 'JetBrains Mono, monospace',
              fontSize: '0.78rem', color: '#C9973A',
              textDecoration: 'none',
            }}>
              ← All Articles
            </Link>
          </div>
        </article>

        {/* ── RIGHT SIDEBAR — Related articles ── */}
        <aside style={{
          gridColumn: '3',
          paddingTop: '8px',
        }}
          className="sidebar-right"
        >
          {related.length > 0 && (
            <div>
              <p style={{
                fontFamily: 'JetBrains Mono, monospace',
                fontSize: '0.65rem', textTransform: 'uppercase',
                letterSpacing: '0.1em', color: '#6B6560', marginBottom: '14px',
              }}>
                Related
              </p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                {related.map(rel => (
                  <Link key={rel.slug} href={`/${locale}/articles/${rel.slug}`}
                    className="related-link"
                  >
                    <p style={{
                      fontFamily: 'JetBrains Mono, monospace',
                      fontSize: '0.65rem', color: '#6B6560', marginBottom: '6px',
                    }}>
                      {rel.date}
                    </p>
                    <p style={{
                      fontFamily: 'Playfair Display, Georgia, serif',
                      fontSize: '0.9rem', color: '#F2EDE4', lineHeight: 1.3,
                    }}>
                      {rel.title}
                    </p>
                  </Link>
                ))}
              </div>
            </div>
          )}
        </aside>
      </div>

      {/* Responsive sidebar hiding */}
      <style>{`
        @media (max-width: 900px) {
          .sidebar-left, .sidebar-right { display: none; }
          article { grid-column: 1 / -1 !important; }
        }
        .related-link {
          text-decoration: none;
          display: block;
          padding: 14px;
          border: 1px solid #2A2720;
          border-radius: 3px;
          transition: border-color 0.15s;
        }
        .related-link:hover {
          border-color: #C9973A;
        }
      `}</style>
    </div>
  );
}
