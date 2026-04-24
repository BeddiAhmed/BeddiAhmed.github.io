import Link from 'next/link';
import { setRequestLocale } from 'next-intl/server';
import type { Locale } from '../../i18n';
import { getAllArticles } from '../../lib/articles';
import { getFeaturedProjects } from '../../lib/projects';
import ArticleCard from '../../components/ArticleCard';
import ProjectCard from '../../components/ProjectCard';

interface Props { params: { locale: Locale } }

/* ── Capability pillars — what you actually do ── */
const CAPABILITIES = [
  {
    icon: '◈',
    title: 'Data Systems & Pipelines',
    body: 'End-to-end analytical pipelines from raw data collection through structured models and interactive dashboards — built to be reproducible, documented, and reusable.',
  },
  {
    icon: '◉',
    title: 'Economic Analysis',
    body: 'Rigorous empirical analysis of macroeconomic questions — trade flows, energy shocks, growth dynamics — using OLS, synthetic control, and panel methods on real-world data.',
  },
  {
    icon: '◎',
    title: 'Structured Explanation',
    body: 'Complex problems broken into clear frameworks. From exam prep systems to published analyses, the output is always interpretable — not just correct.',
  },
];

/* ── Featured case study (flagship project) ── */
const FLAGSHIP = {
  label:    'Case Study',
  category: 'Data System',
  title:    'Middle East Energy Crisis — Mauritanian Economy',
  problem:  'How did the 2023–2024 Middle East escalation transmit through global energy prices to Mauritania\'s GDP, trade balance, and inflation?',
  approach: 'Built a four-source data pipeline (FRED, World Bank, COMTRADE, IMF), ran OLS regression with structural break testing, then applied Synthetic Control to isolate the causal effect.',
  outcome:  'Estimated ~2.5 pp GDP growth cost attributable to the shock. Full trilingual article with embedded interactive Plotly dashboard.',
  stack:    ['Python', 'Plotly', 'OLS', 'Synthetic Control'],
  links:    { article: 'articles/energy-crisis-mauritania', dashboard: '/dashboards/dashboard.html' },
};

export default function HomePage({ params: { locale } }: Props) {
  setRequestLocale(locale);
  const articles = getAllArticles(locale).slice(0, 3);
  const projects = getFeaturedProjects().slice(0, 3);

  return (
    <div style={{ maxWidth: '1100px', margin: '0 auto', padding: '0 32px' }}>

      {/* ════════════════════════════════════════
          HERO — positioning statement, not a bio
          ════════════════════════════════════════ */}
      <section style={{ padding: '88px 0 80px' }}>
        <div style={{ maxWidth: '720px' }}>

          <span className="animate-fade-up badge badge-accent" style={{ marginBottom: '24px', display: 'inline-block' }}>
            Economist · Data Analyst · Systems Builder
          </span>

          <h1 className="animate-fade-up delay-1" style={{
            fontFamily: 'var(--font-display)',
            fontSize: 'clamp(2.4rem, 5vw, 3.8rem)',
            fontWeight: 600,
            lineHeight: 1.1,
            letterSpacing: '-0.03em',
            color: 'var(--text)',
            marginBottom: '24px',
          }}>
            I turn complex economic problems into{' '}
            <span style={{ color: 'var(--accent)', fontStyle: 'italic' }}>
              structured, measurable systems.
            </span>
          </h1>

          <p className="animate-fade-up delay-2" style={{
            fontFamily: 'var(--font-body)',
            fontSize: '1.0625rem',
            color: 'var(--text-2)',
            lineHeight: 1.75,
            maxWidth: '580px',
            marginBottom: '36px',
          }}>
            M.Sc. Economics. I build data pipelines, empirical analyses, and decision tools
            that make real-world economic questions answerable — and the answers readable.
            Published in English, French, and Arabic.
          </p>

          <div className="animate-fade-up delay-3" style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
            <Link href={`/${locale}/projects`} className="btn-primary">
              View Projects →
            </Link>
            <Link href={`/${locale}/articles`} className="btn-secondary">
              Read Analysis
            </Link>
          </div>
        </div>
      </section>

      {/* Divider */}
      <hr style={{ border: 'none', borderTop: '1px solid var(--border)', margin: 0 }} />

      {/* ════════════════════════════════════════
          PROOF BAR — quiet credential signals
          ════════════════════════════════════════ */}
      <section style={{
        padding: '20px 0',
        display: 'flex',
        gap: '32px',
        alignItems: 'center',
        flexWrap: 'wrap',
      }}>
        {[
          { value: 'M.Sc. Economics', sub: 'Econometrics + Trade Theory' },
          { value: 'CIROPrep',        sub: 'Retail Securities Exam Prep' },
          { value: 'Open Data',       sub: 'All code public on GitHub' },
          { value: 'EN / FR / AR',    sub: 'Trilingual publication' },
        ].map((item, i) => (
          <div key={i} style={{
            display: 'flex', gap: '10px', alignItems: 'center',
            paddingRight: '32px',
            borderRight: i < 3 ? '1px solid var(--border)' : 'none',
          }}>
            <div>
              <div style={{
                fontFamily: 'var(--font-body)',
                fontWeight: 600, fontSize: '0.875rem',
                color: 'var(--text)',
              }}>
                {item.value}
              </div>
              <div style={{
                fontFamily: 'var(--font-body)',
                fontSize: '0.78rem', color: 'var(--muted)',
              }}>
                {item.sub}
              </div>
            </div>
          </div>
        ))}
      </section>

      {/* Divider */}
      <hr style={{ border: 'none', borderTop: '1px solid var(--border)', margin: 0 }} />

      {/* ════════════════════════════════════════
          CAPABILITIES — what I do and how
          ════════════════════════════════════════ */}
      <section style={{ padding: '72px 0' }}>
        <span className="section-label">What I Do</span>
        <h2 style={{
          fontFamily: 'var(--font-display)',
          fontSize: 'clamp(1.6rem, 3vw, 2.2rem)',
          fontWeight: 600,
          marginBottom: '40px',
          letterSpacing: '-0.02em',
        }}>
          Analysis → Systems → Clarity
        </h2>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: '1px',
          background: 'var(--border)',
          border: '1px solid var(--border)',
          borderRadius: '6px',
          overflow: 'hidden',
        }}>
          {CAPABILITIES.map((cap, i) => (
            <div key={i} style={{
              background: 'var(--bg)',
              padding: '28px 24px',
              display: 'flex', flexDirection: 'column', gap: '10px',
            }}>
              <span style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '1.1rem', color: 'var(--accent)', opacity: 0.5,
              }}>
                {cap.icon}
              </span>
              <h3 style={{
                fontFamily: 'var(--font-display)',
                fontSize: '1.05rem', fontWeight: 600,
                color: 'var(--text)', lineHeight: 1.3,
                letterSpacing: '-0.01em',
              }}>
                {cap.title}
              </h3>
              <p style={{
                fontFamily: 'var(--font-body)',
                fontSize: '0.875rem', color: 'var(--text-2)',
                lineHeight: 1.7,
              }}>
                {cap.body}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* ════════════════════════════════════════
          FLAGSHIP CASE STUDY
          ════════════════════════════════════════ */}
      <section style={{ padding: '0 0 72px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: '24px', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <span className="section-label">Featured Work</span>
            <h2 style={{
              fontFamily: 'var(--font-display)',
              fontSize: 'clamp(1.6rem, 3vw, 2.2rem)',
              fontWeight: 600, letterSpacing: '-0.02em',
            }}>
              Case Study
            </h2>
          </div>
          <Link href={`/${locale}/projects`} className="link-arrow">All Projects →</Link>
        </div>

        <div style={{
          border: '1px solid var(--border)',
          borderRadius: '8px',
          overflow: 'hidden',
        }}>
          {/* Top accent bar */}
          <div style={{ height: '3px', background: 'var(--accent)' }} />

          <div style={{
            padding: '36px',
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '40px',
            alignItems: 'start',
          }} className="case-grid">

            {/* Left — narrative */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                <span className="badge badge-accent">{FLAGSHIP.label}</span>
                <span className="badge">{FLAGSHIP.category}</span>
              </div>

              <h3 style={{
                fontFamily: 'var(--font-display)',
                fontSize: '1.5rem', fontWeight: 600,
                color: 'var(--text)', lineHeight: 1.25,
                letterSpacing: '-0.02em',
              }}>
                {FLAGSHIP.title}
              </h3>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                {[
                  { label: 'Problem',  text: FLAGSHIP.problem },
                  { label: 'Approach', text: FLAGSHIP.approach },
                  { label: 'Outcome',  text: FLAGSHIP.outcome },
                ].map(row => (
                  <div key={row.label} style={{ display: 'grid', gridTemplateColumns: '80px 1fr', gap: '8px' }}>
                    <span style={{
                      fontFamily: 'var(--font-mono)',
                      fontSize: '0.69rem', fontWeight: 600,
                      letterSpacing: '0.07em', textTransform: 'uppercase',
                      color: 'var(--muted)', paddingTop: '2px',
                    }}>
                      {row.label}
                    </span>
                    <span style={{
                      fontFamily: 'var(--font-body)',
                      fontSize: '0.875rem', color: 'var(--text-2)',
                      lineHeight: 1.65,
                    }}>
                      {row.text}
                    </span>
                  </div>
                ))}
              </div>

              {/* Stack */}
              <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                {FLAGSHIP.stack.map(t => (
                  <span key={t} className="badge">{t}</span>
                ))}
              </div>

              {/* Links */}
              <div style={{ display: 'flex', gap: '14px', flexWrap: 'wrap', paddingTop: '4px' }}>
                <Link href={`/${locale}/${FLAGSHIP.links.article}`} className="btn-primary" style={{ fontSize: '0.82rem', padding: '9px 18px' }}>
                  Read Article →
                </Link>
                <a href={FLAGSHIP.links.dashboard} target="_blank" rel="noopener noreferrer"
                  className="btn-secondary" style={{ fontSize: '0.82rem', padding: '9px 18px' }}>
                  Open Dashboard
                </a>
              </div>
            </div>

            {/* Right — metric highlights */}
            <div style={{
              background: 'var(--bg-subtle)',
              borderRadius: '6px', padding: '28px',
              display: 'flex', flexDirection: 'column', gap: '20px',
            }}>
              <p style={{ fontFamily: 'var(--font-mono)', fontSize: '0.69rem', textTransform: 'uppercase', letterSpacing: '0.1em', color: 'var(--muted)' }}>
                Key Findings
              </p>
              {[
                { metric: '−2.5 pp', label: 'GDP growth cost (SCM estimate)', accent: true },
                { metric: '−0.4 pp', label: 'Trade balance per $10 oil increase' },
                { metric: '0.08×',   label: 'Oil-to-CPI pass-through elasticity' },
                { metric: 'p = 0.07', label: 'Chow structural break at 2023' },
                { metric: '4 sources', label: 'FRED · World Bank · COMTRADE · IMF' },
              ].map((item, i) => (
                <div key={i} style={{
                  paddingBottom: '16px',
                  borderBottom: i < 4 ? '1px solid var(--border)' : 'none',
                }}>
                  <div style={{
                    fontFamily: 'var(--font-display)',
                    fontSize: '1.5rem', fontWeight: 700,
                    color: item.accent ? 'var(--accent)' : 'var(--text)',
                    lineHeight: 1, marginBottom: '4px',
                  }}>
                    {item.metric}
                  </div>
                  <div style={{
                    fontFamily: 'var(--font-body)',
                    fontSize: '0.8rem', color: 'var(--muted)',
                  }}>
                    {item.label}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <style>{`
          @media (max-width: 760px) { .case-grid { grid-template-columns: 1fr !important; } }
        `}</style>
      </section>

      {/* ════════════════════════════════════════
          LATEST WRITING
          ════════════════════════════════════════ */}
      <section style={{ padding: '0 0 72px', borderTop: '1px solid var(--border)', paddingTop: '72px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: '32px', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <span className="section-label">Insights</span>
            <h2 style={{
              fontFamily: 'var(--font-display)',
              fontSize: 'clamp(1.6rem, 3vw, 2.2rem)',
              fontWeight: 600, letterSpacing: '-0.02em',
            }}>
              Latest Analysis
            </h2>
          </div>
          <Link href={`/${locale}/articles`} className="link-arrow">All Articles →</Link>
        </div>

        {articles.length === 0 ? (
          <div style={{
            border: '1px dashed var(--border-2)', borderRadius: '6px',
            padding: '48px', textAlign: 'center',
            fontFamily: 'var(--font-body)', fontSize: '0.875rem', color: 'var(--muted)',
          }}>
            Articles coming soon — check back shortly.
          </div>
        ) : (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
            gap: '16px',
          }}>
            {articles.map((article, i) => (
              <ArticleCard key={article.slug} article={article} locale={locale} index={i} />
            ))}
          </div>
        )}
      </section>

      {/* ════════════════════════════════════════
          ALL PROJECTS GRID
          ════════════════════════════════════════ */}
      <section style={{ borderTop: '1px solid var(--border)', padding: '72px 0' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: '32px', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <span className="section-label">Build</span>
            <h2 style={{
              fontFamily: 'var(--font-display)',
              fontSize: 'clamp(1.6rem, 3vw, 2.2rem)',
              fontWeight: 600, letterSpacing: '-0.02em',
            }}>
              Projects
            </h2>
          </div>
          <Link href={`/${locale}/projects`} className="link-arrow">All Projects →</Link>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
          gap: '16px',
        }}>
          {projects.map((project, i) => (
            <ProjectCard key={project.id} project={project} locale={locale} index={i} />
          ))}
        </div>
      </section>

      {/* ════════════════════════════════════════
          FOOTER CTA
          ════════════════════════════════════════ */}
      <section style={{
        borderTop: '1px solid var(--border)',
        padding: '64px 0',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '24px',
      }}>
        <div>
          <h2 style={{
            fontFamily: 'var(--font-display)',
            fontSize: '1.6rem', fontWeight: 600,
            letterSpacing: '-0.02em', marginBottom: '8px',
          }}>
            Let's build something rigorous.
          </h2>
          <p style={{ fontFamily: 'var(--font-body)', fontSize: '0.9375rem', color: 'var(--text-2)' }}>
            Open to research collaborations, consulting, and CIRO tutoring.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
          <a href="https://linkedin.com" target="_blank" rel="noopener noreferrer" className="btn-primary">
            Connect →
          </a>
          <Link href={`/${locale}/about`} className="btn-secondary">
            About Me
          </Link>
        </div>
      </section>

    </div>
  );
}
