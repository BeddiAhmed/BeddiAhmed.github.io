import { setRequestLocale } from 'next-intl/server';
import { locales, type Locale } from '../../../i18n';

interface Props { params: { locale: Locale } }

export function generateStaticParams() {
  return locales.map(locale => ({ locale }));
}

const SKILLS = [
  { group: 'Economics',    items: ['Macroeconomics', 'Econometrics', 'Trade Analysis', 'Monetary Policy', 'Development Economics'] },
  { group: 'Data & Code',  items: ['Python (Pandas, NumPy, Plotly)', 'R (ggplot2, tidyverse)', 'SQL', 'Statistical Modelling', 'Time Series Analysis'] },
  { group: 'Methods',      items: ['OLS / GLS Regression', 'Synthetic Control Method', 'Difference-in-Differences', 'Structural Break Tests', 'Panel Data Analysis'] },
  { group: 'Finance',      items: ['CIRO Licensing (Retail Securities)', 'Fixed Income', 'Derivatives', 'Portfolio Theory', 'Canadian Capital Markets'] },
];

const TIMELINE = [
  { year: '2024–',     event: 'Founder, CIROPrep — CIRO exam prep platform for career switchers & retakers' },
  { year: '2024',      event: 'Launched Calculation Labs — quantitative tutoring sub-brand' },
  { year: '2023',      event: 'Published first data-driven economic analysis on African energy markets' },
  { year: '2022–23',   event: 'M.Sc. Economics — advanced econometrics, trade theory, macroeconomic modelling' },
  { year: '2020–22',   event: 'Economic analysis & research — African markets focus' },
];

export default function AboutPage({ params: { locale } }: Props) {
  setRequestLocale(locale);
  const isRtl = locale === 'ar';

  return (
    <div style={{ maxWidth: '1120px', margin: '0 auto', padding: '64px 24px 80px' }}>
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'minmax(0, 2fr) minmax(0, 1fr)',
        gap: '64px',
        alignItems: 'start',
      }}
        className="about-grid"
      >

        {/* ── LEFT — Bio ── */}
        <div>
          <span style={{
            fontFamily: 'JetBrains Mono, monospace',
            fontSize: '0.7rem', textTransform: 'uppercase',
            letterSpacing: '0.1em', color: '#C9973A', display: 'block',
            marginBottom: '14px',
          }}>
            About
          </span>
          <h1 style={{
            fontFamily: 'Playfair Display, Georgia, serif',
            fontSize: 'clamp(2rem, 5vw, 3.2rem)',
            fontWeight: 600, lineHeight: 1.1,
            letterSpacing: '-0.03em', color: '#F2EDE4',
            marginBottom: '16px',
          }}>
            Ahmed
          </h1>
          <div style={{ width: '40px', height: '2px', background: '#C9973A', marginBottom: '32px' }} />

          <div style={{
            fontFamily: 'Source Serif 4, Georgia, serif',
            fontSize: '1.05rem', color: '#B8B0A4',
            lineHeight: 1.8, maxWidth: '62ch',
          }} dir={isRtl ? 'rtl' : 'ltr'}>
            <p style={{ marginBottom: '1.4rem' }}>
              I'm an economist and data analyst with an M.Sc. in Economics, specialising in
              African macroeconomics, energy markets, and global trade. My work sits at the
              intersection of rigorous empirical analysis and clear communication — turning
              complex datasets into interpretable insights.
            </p>
            <p style={{ marginBottom: '1.4rem' }}>
              Through <strong style={{ color: '#F2EDE4' }}>CIROPrep</strong>, I help career
              switchers, recent graduates, and exam retakers pass CIRO licensing exams
              (Retail Securities, WME) with structured question banks and personalised tutoring.
              The <strong style={{ color: '#F2EDE4' }}>Calculation Labs</strong> sub-brand
              focuses on quantitative and mathematics tutoring.
            </p>
            <p style={{ marginBottom: '1.4rem' }}>
              My research interests include energy price transmission mechanisms in sub-Saharan
              Africa, Mauritanian trade vulnerability, and synthetic control applications in
              development economics.
            </p>
            <p>
              I publish in English, French, and Arabic — reflecting the linguistic reality
              of the African economies I study.
            </p>
          </div>

          {/* Contact */}
          <div style={{ marginTop: '40px', display: 'flex', gap: '14px', flexWrap: 'wrap' }}>
            {[
              { label: 'GitHub', href: 'https://github.com' },
              { label: 'LinkedIn', href: 'https://linkedin.com' },
              { label: 'CIROPrep', href: 'https://ciroprep.ca' },
            ].map(link => (
              <a key={link.label} href={link.href}
                target="_blank" rel="noopener noreferrer"
                className="contact-link"
              >
                {link.label} ↗
              </a>
            ))}
          </div>
        </div>

        {/* ── RIGHT — Skills + Timeline ── */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '40px' }}>

          {/* Skills */}
          <div>
            <p style={{
              fontFamily: 'JetBrains Mono, monospace',
              fontSize: '0.68rem', textTransform: 'uppercase',
              letterSpacing: '0.1em', color: '#6B6560', marginBottom: '16px',
            }}>
              Skills & Expertise
            </p>
            {SKILLS.map(group => (
              <div key={group.group} style={{ marginBottom: '20px' }}>
                <p style={{
                  fontFamily: 'JetBrains Mono, monospace',
                  fontSize: '0.7rem', color: '#C9973A',
                  textTransform: 'uppercase', letterSpacing: '0.08em',
                  marginBottom: '8px',
                }}>
                  {group.group}
                </p>
                <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                  {group.items.map(item => (
                    <span key={item} style={{
                      fontFamily: 'JetBrains Mono, monospace',
                      fontSize: '0.68rem', color: '#B8B0A4',
                      background: '#1C1A17', border: '1px solid #2A2720',
                      padding: '3px 9px', borderRadius: '2px',
                      letterSpacing: '0.02em',
                    }}>
                      {item}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* Timeline */}
          <div>
            <p style={{
              fontFamily: 'JetBrains Mono, monospace',
              fontSize: '0.68rem', textTransform: 'uppercase',
              letterSpacing: '0.1em', color: '#6B6560', marginBottom: '16px',
            }}>
              Timeline
            </p>
            <div style={{ position: 'relative' }}>
              {/* Vertical line */}
              <div style={{
                position: 'absolute', left: '48px', top: 0, bottom: 0,
                width: '1px', background: '#2A2720',
              }} />
              {TIMELINE.map((item, i) => (
                <div key={i} style={{
                  display: 'grid', gridTemplateColumns: '48px 1fr',
                  gap: '16px', marginBottom: '20px', position: 'relative',
                }}>
                  <span style={{
                    fontFamily: 'JetBrains Mono, monospace',
                    fontSize: '0.65rem', color: '#C9973A',
                    textAlign: 'right', paddingTop: '2px',
                    whiteSpace: 'nowrap',
                  }}>
                    {item.year}
                  </span>
                  <div style={{
                    paddingLeft: '16px', borderLeft: '2px solid #C9973A',
                    marginLeft: '0',
                  }}>
                    <p style={{
                      fontFamily: 'Source Serif 4, Georgia, serif',
                      fontSize: '0.85rem', color: '#B8B0A4', lineHeight: 1.5,
                      margin: 0,
                    }}>
                      {item.event}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <style>{`
        @media (max-width: 768px) {
          .about-grid { grid-template-columns: 1fr !important; }
        }
        .contact-link {
          font-family: 'JetBrains Mono', monospace;
          font-size: 0.78rem;
          letter-spacing: 0.04em;
          color: #6B6560;
          text-decoration: none;
          border: 1px solid #3A3730;
          padding: 8px 18px;
          border-radius: 2px;
          transition: border-color 0.15s, color 0.15s;
        }
        .contact-link:hover {
          border-color: #C9973A;
          color: #C9973A;
        }
      `}</style>
    </div>
  );
}
