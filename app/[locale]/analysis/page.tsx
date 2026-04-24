import { setRequestLocale } from 'next-intl/server';
import Link from 'next/link';
import { locales, type Locale } from '../../../i18n';

interface Props { params: { locale: Locale } }

export function generateStaticParams() {
  return locales.map(locale => ({ locale }));
}

/* ── Data sources ── */
const SOURCES = [
  {
    name: 'FRED',
    full: 'Federal Reserve Economic Data',
    desc: 'WTI crude, Brent crude, Henry Hub natural gas, and LNG spot prices. Monthly and weekly series from 2010 to present.',
    badge: 'badge-accent',
  },
  {
    name: 'World Bank',
    full: 'World Development Indicators',
    desc: 'GDP growth, inflation (CPI), current account balance, trade-to-GDP ratio, and fuel import share for Mauritania and 12 peer countries.',
    badge: 'badge',
  },
  {
    name: 'COMTRADE',
    full: 'UN Comtrade Public API v2',
    desc: 'Mauritania bilateral trade flows by HS commodity code and partner country — exports and imports, 2015–2023.',
    badge: 'badge-gold',
  },
  {
    name: 'IMF WEO',
    full: 'World Economic Outlook',
    desc: 'GDP level and growth forecasts, inflation outlook, and external balance projections used for counterfactual benchmarking.',
    badge: 'badge',
  },
];

/* ── Chart groups ── */
const CHART_GROUPS = [
  {
    label: 'Price Analysis',
    desc: 'Global commodity price dynamics, volatility regimes, and shock detection across the 2021–2024 energy cycle.',
    charts: [
      { file: 'A_price_timeline.png',       title: 'Energy Price Timeline',      desc: 'Annotated WTI, Brent, and LNG price series with key geopolitical event markers.' },
      { file: 'B_indexed_prices.png',        title: 'Indexed Price Movements',    desc: 'Normalized to 100 at Jan 2021 — relative volatility across commodities.' },
      { file: 'C_rolling_correlations.png',  title: 'Rolling Correlations',       desc: '12-month rolling correlations between oil price and Mauritanian macro variables.' },
      { file: 'D_stress_index.png',          title: 'Energy Stress Index',        desc: 'Composite z-score index aggregating price stress across all tracked commodities.' },
      { file: 'E_correlation_heatmap.png',   title: 'Correlation Heatmap',        desc: 'Cross-correlation matrix of weekly commodity returns over the full sample.' },
      { file: 'F_return_distributions.png',  title: 'Return Distributions',       desc: 'Weekly return distributions by regime — pre-shock vs. escalation vs. current.' },
    ],
  },
  {
    label: 'Mauritania Macro Analysis',
    desc: 'OLS regression results, structural break testing, trade exposure, and peer benchmarking.',
    charts: [
      { file: 'G_macro_dashboard.png',  title: 'Macro Dashboard',     desc: 'Four-panel overview: GDP growth, inflation, trade balance, and current account vs. peers.' },
      { file: 'H_oil_vs_outcomes.png',  title: 'Oil Price → Outcomes', desc: 'Scatter and time plots from OLS: oil price shocks mapped to GDP, inflation, and trade balance.' },
      { file: 'J_trade_flows.png',      title: 'Trade Flow Breakdown', desc: 'Export and import composition by commodity and top trading partners from COMTRADE.' },
      { file: 'K_peer_comparison.png',  title: 'Peer Comparison',      desc: 'Mauritania macro trajectory vs. the unweighted peer group mean across key indicators.' },
    ],
  },
  {
    label: 'Synthetic Control',
    desc: 'Causal identification via the Abadie–Gardeazabal (2003) Synthetic Control Method, with placebo validation.',
    charts: [
      { file: 'M_synthetic_control_main.png', title: 'SCM — Main Result',    desc: 'Real vs. synthetic Mauritania GDP growth gap, 2015–2024. The post-2023 divergence is the estimated treatment effect.' },
      { file: 'N_placebo_tests.png',          title: 'Placebo Tests',         desc: 'SCM applied to all 12 donor countries. Mauritania\'s gap sits in the tail of the placebo distribution.' },
      { file: 'O_donor_weights.png',          title: 'Donor Country Weights', desc: 'Optimal weights assigned to each peer country to construct the synthetic control unit.' },
      { file: 'P_predictor_balance.png',      title: 'Predictor Balance',     desc: 'Pre-treatment fit quality across all matching variables (GDP, inflation, trade, investment).' },
    ],
  },
];

/* ── Excel downloads ── */
const DOWNLOADS = [
  {
    file: 'price_analysis.xlsx',
    title: 'Price Analysis',
    desc: 'Returns, volatility, z-scores, regime statistics, and correlation matrices.',
    sheets: ['Prices', 'Returns', 'Volatility', 'Correlations', 'Regimes'],
  },
  {
    file: 'mauritania_analysis.xlsx',
    title: 'Mauritania Macro',
    desc: 'OLS regression output, Chow test, before/after comparison, and COMTRADE trade exposure.',
    sheets: ['OLS Results', 'Chow Test', 'Before/After', 'Trade Exposure'],
  },
  {
    file: 'synthetic_control_results.xlsx',
    title: 'Synthetic Control',
    desc: 'Donor weights, predictor balance, gap series, and placebo test p-values.',
    sheets: ['Weights', 'Predictor Balance', 'Gap Series', 'Placebo Tests'],
  },
  {
    file: 'summary.xlsx',
    title: 'Full Summary',
    desc: 'All datasets combined in a single workbook — prices, macro, trade, and SCM results.',
    sheets: ['Prices', 'WB Macro', 'COMTRADE', 'SCM'],
  },
];

/* ── Python scripts ── */
const SCRIPTS = [
  {
    file: 'collect_data.py',
    title: 'Data Collection Pipeline',
    desc: 'Fetches all four data sources via API — FRED commodity prices, World Bank WDI macro panel, UN COMTRADE trade flows, and IMF WEO forecasts. Outputs clean CSV files and a summary Excel workbook.',
    outputs: ['prices.csv', 'wb_macro.csv', 'comtrade_exports.csv', 'comtrade_imports.csv', 'summary.xlsx'],
  },
  {
    file: 'analyze_prices.py',
    title: 'Price & Volatility Analysis',
    desc: 'Computes log returns, rolling volatility, z-score shock detection, and cross-commodity correlations. Runs regime analysis across three periods: pre-war, escalation, and current. Annotates key geopolitical events on price charts.',
    outputs: ['price_analysis/A–F charts', 'price_analysis.xlsx'],
  },
  {
    file: 'analyze_mauritania.py',
    title: 'Empirical Macro Analysis',
    desc: 'Merges price, macro, and trade data. Runs OLS regressions (oil/gas → GDP, trade balance, inflation) with heteroskedasticity-robust standard errors. Performs a Chow structural break test at Oct 2023. Computes fuel import cost shock estimates from COMTRADE volumes.',
    outputs: ['mauritania_analysis/G–K charts', 'mauritania_analysis.xlsx'],
  },
  {
    file: 'synthetic_control.py',
    title: 'Synthetic Control Method',
    desc: 'Implements the Abadie–Gardeazabal SCM from scratch using scipy.optimize. Builds a synthetic Mauritania from 12 peer countries that minimises pre-treatment MSPE (2015–2022). Post-2023 gap = causal estimate. Runs placebo tests on all donor countries to assess statistical significance.',
    outputs: ['synthetic_control/M–P charts', 'synthetic_control_results.xlsx'],
  },
  {
    file: 'visualize.py',
    title: 'Interactive Dashboard Builder',
    desc: 'Reads all pipeline outputs and assembles a self-contained Plotly HTML dashboard — no server required, fully embed-ready. Falls back to synthetic data if pipeline outputs are missing, so the dashboard always renders.',
    outputs: ['dashboard.html'],
  },
];

export default function AnalysisPage({ params: { locale } }: Props) {
  setRequestLocale(locale);

  return (
    <div style={{ maxWidth: '1120px', margin: '0 auto', padding: '64px 24px 96px' }}>

      {/* ── HEADER ── */}
      <div style={{ maxWidth: '680px', marginBottom: '72px' }}>
        <span className="section-label">Data Pipeline</span>
        <h1 style={{
          fontFamily: 'var(--font-display)',
          fontSize: 'clamp(2rem, 5vw, 3.2rem)',
          fontWeight: 600, lineHeight: 1.1,
          letterSpacing: '-0.03em', color: 'var(--text)',
          marginBottom: '16px',
        }}>
          Analysis — Middle East Energy Crisis
        </h1>
        <div style={{ width: '40px', height: '2px', background: 'var(--accent)', marginBottom: '20px' }} />
        <p style={{
          fontFamily: 'var(--font-body)',
          fontSize: '1.0625rem', color: 'var(--text-2)', lineHeight: 1.75,
        }}>
          Full methodology, charts, and data outputs for the empirical study of the 2023–2024
          Middle East energy shock and its transmission to the Mauritanian economy.
        </p>
        <div style={{ marginTop: '28px', display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
          <Link href={`/${locale}/articles/energy-crisis-mauritania`} className="btn-primary">
            Read Article →
          </Link>
          <a href="/dashboards/dashboard.html" target="_blank" rel="noopener noreferrer" className="btn-secondary">
            Full Dashboard ↗
          </a>
        </div>
      </div>

      <hr style={{ border: 'none', borderTop: '1px solid var(--border)', marginBottom: '72px' }} />

      {/* ── DATA SOURCES ── */}
      <section style={{ marginBottom: '80px' }}>
        <span className="section-label">Sources</span>
        <h2 style={{
          fontFamily: 'var(--font-display)',
          fontSize: 'clamp(1.4rem, 2.5vw, 1.9rem)',
          fontWeight: 600, marginBottom: '32px', letterSpacing: '-0.02em',
        }}>
          Four-Source Data Pipeline
        </h2>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
          gap: '1px',
          background: 'var(--border)',
          border: '1px solid var(--border)',
          borderRadius: '6px',
          overflow: 'hidden',
        }}>
          {SOURCES.map((src, i) => (
            <div key={i} style={{
              background: 'var(--bg)',
              padding: '24px',
              display: 'flex', flexDirection: 'column', gap: '10px',
            }}>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: '10px' }}>
                <span style={{
                  fontFamily: 'var(--font-display)',
                  fontSize: '1.25rem', fontWeight: 700,
                  color: 'var(--text)', letterSpacing: '-0.02em',
                }}>
                  {src.name}
                </span>
                <span className={`badge ${src.badge}`} style={{ flexShrink: 0 }}>API</span>
              </div>
              <p style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '0.68rem', color: 'var(--muted)',
                letterSpacing: '0.02em', lineHeight: 1.4,
              }}>
                {src.full}
              </p>
              <p style={{
                fontFamily: 'var(--font-body)',
                fontSize: '0.875rem', color: 'var(--text-2)', lineHeight: 1.65,
              }}>
                {src.desc}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* ── CHART GALLERY ── */}
      <section style={{ marginBottom: '80px' }}>
        <span className="section-label">Charts</span>
        <h2 style={{
          fontFamily: 'var(--font-display)',
          fontSize: 'clamp(1.4rem, 2.5vw, 1.9rem)',
          fontWeight: 600, marginBottom: '8px', letterSpacing: '-0.02em',
        }}>
          Output Charts
        </h2>
        <p style={{
          fontFamily: 'var(--font-body)',
          fontSize: '0.9375rem', color: 'var(--text-2)', marginBottom: '48px',
        }}>
          14 charts across three analysis stages. Copy PNGs to{' '}
          <code style={{
            fontFamily: 'var(--font-mono)', fontSize: '0.82rem',
            background: 'var(--bg-subtle)', border: '1px solid var(--border)',
            padding: '1px 6px', borderRadius: '3px', color: 'var(--accent)',
          }}>
            public/analysis-charts/
          </code>{' '}
          to populate the grid.
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '56px' }}>
          {CHART_GROUPS.map((group, gi) => (
            <div key={gi}>
              <div style={{
                display: 'flex', alignItems: 'baseline', gap: '16px',
                marginBottom: '8px', flexWrap: 'wrap',
              }}>
                <h3 style={{
                  fontFamily: 'var(--font-display)',
                  fontSize: '1.15rem', fontWeight: 600,
                  color: 'var(--text)', letterSpacing: '-0.01em',
                }}>
                  {group.label}
                </h3>
                <span className="badge">{group.charts.length} charts</span>
              </div>
              <p style={{
                fontFamily: 'var(--font-body)',
                fontSize: '0.875rem', color: 'var(--muted)',
                marginBottom: '20px',
              }}>
                {group.desc}
              </p>
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
                gap: '16px',
              }}>
                {group.charts.map((chart, ci) => (
                  <div key={ci} style={{
                    border: '1px solid var(--border)',
                    borderRadius: '6px',
                    overflow: 'hidden',
                    background: 'var(--bg)',
                  }}>
                    <div style={{
                      background: 'var(--bg-subtle)',
                      aspectRatio: '16/10',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      overflow: 'hidden',
                      position: 'relative',
                    }}>
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img
                        src={`/analysis-charts/${chart.file}`}
                        alt={chart.title}
                        style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }}
                        loading="lazy"
                        onError={undefined}
                      />
                    </div>
                    <div style={{ padding: '14px 16px' }}>
                      <p style={{
                        fontFamily: 'var(--font-mono)',
                        fontSize: '0.65rem', color: 'var(--muted)',
                        letterSpacing: '0.04em', marginBottom: '4px',
                      }}>
                        {chart.file.replace('.png', '')}
                      </p>
                      <p style={{
                        fontFamily: 'var(--font-body)',
                        fontSize: '0.875rem', fontWeight: 500,
                        color: 'var(--text)', marginBottom: '6px',
                      }}>
                        {chart.title}
                      </p>
                      <p style={{
                        fontFamily: 'var(--font-body)',
                        fontSize: '0.8rem', color: 'var(--text-2)', lineHeight: 1.5,
                      }}>
                        {chart.desc}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </section>

      <hr style={{ border: 'none', borderTop: '1px solid var(--border)', marginBottom: '72px' }} />

      {/* ── DOWNLOADS ── */}
      <section style={{ marginBottom: '80px' }}>
        <span className="section-label">Downloads</span>
        <h2 style={{
          fontFamily: 'var(--font-display)',
          fontSize: 'clamp(1.4rem, 2.5vw, 1.9rem)',
          fontWeight: 600, marginBottom: '32px', letterSpacing: '-0.02em',
        }}>
          Excel Output Files
        </h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {DOWNLOADS.map((dl, i) => (
            <div key={i} style={{
              display: 'flex', alignItems: 'flex-start',
              gap: '20px', padding: '20px 24px',
              border: '1px solid var(--border)', borderRadius: '6px',
              background: 'var(--bg)',
            }} className="download-row">
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: '10px', flexWrap: 'wrap', marginBottom: '6px' }}>
                  <span style={{
                    fontFamily: 'var(--font-body)',
                    fontSize: '0.9375rem', fontWeight: 600,
                    color: 'var(--text)',
                  }}>
                    {dl.title}
                  </span>
                  <span style={{
                    fontFamily: 'var(--font-mono)',
                    fontSize: '0.65rem', color: 'var(--muted)',
                    letterSpacing: '0.04em',
                  }}>
                    {dl.file}
                  </span>
                </div>
                <p style={{
                  fontFamily: 'var(--font-body)',
                  fontSize: '0.875rem', color: 'var(--text-2)',
                  lineHeight: 1.5, marginBottom: '10px',
                }}>
                  {dl.desc}
                </p>
                <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                  {dl.sheets.map(sheet => (
                    <span key={sheet} className="badge">{sheet}</span>
                  ))}
                </div>
              </div>
              <a
                href={`/analysis-charts/${dl.file}`}
                download
                className="btn-secondary"
                style={{ fontSize: '0.8rem', padding: '8px 16px', flexShrink: 0 }}
              >
                Download ↓
              </a>
            </div>
          ))}
        </div>
      </section>

      {/* ── EMBEDDED DASHBOARD ── */}
      <section style={{ marginBottom: '80px' }}>
        <span className="section-label">Interactive</span>
        <h2 style={{
          fontFamily: 'var(--font-display)',
          fontSize: 'clamp(1.4rem, 2.5vw, 1.9rem)',
          fontWeight: 600, marginBottom: '8px', letterSpacing: '-0.02em',
        }}>
          Live Dashboard
        </h2>
        <p style={{
          fontFamily: 'var(--font-body)',
          fontSize: '0.9375rem', color: 'var(--text-2)', marginBottom: '20px',
        }}>
          Interactive Plotly charts — hover to explore values, click legend items to toggle series.
        </p>
        <div style={{
          border: '1px solid var(--border)',
          borderRadius: '6px',
          overflow: 'hidden',
        }}>
          <div style={{
            padding: '10px 16px',
            background: 'var(--bg-subtle)',
            borderBottom: '1px solid var(--border)',
            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          }}>
            <span style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '0.7rem', color: 'var(--muted)',
              letterSpacing: '0.04em',
            }}>
              public/dashboards/dashboard.html
            </span>
            <a
              href="/dashboards/dashboard.html"
              target="_blank" rel="noopener noreferrer"
              className="link-arrow"
              style={{ fontSize: '0.78rem' }}
            >
              Open full screen ↗
            </a>
          </div>
          <iframe
            src="/dashboards/dashboard.html"
            width="100%"
            height="900"
            style={{ border: 'none', display: 'block' }}
            title="Middle East Energy Crisis — Interactive Dashboard"
          />
        </div>
      </section>

      <hr style={{ border: 'none', borderTop: '1px solid var(--border)', marginBottom: '72px' }} />

      {/* ── PYTHON SCRIPTS ── */}
      <section>
        <span className="section-label">Code</span>
        <h2 style={{
          fontFamily: 'var(--font-display)',
          fontSize: 'clamp(1.4rem, 2.5vw, 1.9rem)',
          fontWeight: 600, marginBottom: '8px', letterSpacing: '-0.02em',
        }}>
          Python Scripts
        </h2>
        <p style={{
          fontFamily: 'var(--font-body)',
          fontSize: '0.9375rem', color: 'var(--text-2)', marginBottom: '32px',
        }}>
          Five scripts, run in order. All outputs are reproducible from the raw API data.
        </p>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0', border: '1px solid var(--border)', borderRadius: '6px', overflow: 'hidden' }}>
          {SCRIPTS.map((script, i) => (
            <div key={i} style={{
              padding: '24px',
              borderBottom: i < SCRIPTS.length - 1 ? '1px solid var(--border)' : 'none',
              background: 'var(--bg)',
              display: 'grid',
              gridTemplateColumns: '1fr 220px',
              gap: '24px',
              alignItems: 'start',
            }} className="script-row">
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px', flexWrap: 'wrap' }}>
                  <span style={{
                    fontFamily: 'var(--font-mono)',
                    fontSize: '0.78rem', fontWeight: 500,
                    color: 'var(--accent)', letterSpacing: '0.02em',
                  }}>
                    {String(i + 1).padStart(2, '0')} — {script.file}
                  </span>
                </div>
                <p style={{
                  fontFamily: 'var(--font-body)',
                  fontSize: '0.9375rem', fontWeight: 600,
                  color: 'var(--text)', marginBottom: '8px',
                }}>
                  {script.title}
                </p>
                <p style={{
                  fontFamily: 'var(--font-body)',
                  fontSize: '0.875rem', color: 'var(--text-2)',
                  lineHeight: 1.65,
                }}>
                  {script.desc}
                </p>
              </div>
              <div>
                <p style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: '0.63rem', textTransform: 'uppercase',
                  letterSpacing: '0.08em', color: 'var(--muted)',
                  marginBottom: '8px',
                }}>
                  Outputs
                </p>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  {script.outputs.map(out => (
                    <span key={out} style={{
                      fontFamily: 'var(--font-mono)',
                      fontSize: '0.72rem', color: 'var(--text-2)',
                      padding: '3px 8px',
                      background: 'var(--bg-subtle)',
                      border: '1px solid var(--border)',
                      borderRadius: '3px',
                      display: 'block',
                    }}>
                      {out}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      <style>{`
        @media (max-width: 640px) {
          .download-row { flex-direction: column; }
          .download-row a { align-self: flex-start; }
          .script-row { grid-template-columns: 1fr !important; }
        }
      `}</style>
    </div>
  );
}
