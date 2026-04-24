import Link from 'next/link';
import type { Locale } from '../i18n';

export default function Footer({ locale }: { locale: Locale }) {
  const year = new Date().getFullYear();
  return (
    <footer style={{
      borderTop: '1px solid var(--border)',
      background: 'var(--bg-subtle)',
    }}>
      <div style={{ maxWidth: '1100px', margin: '0 auto', padding: '48px 32px 32px' }}>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
          gap: '32px',
          marginBottom: '40px',
        }}>
          <div>
            <div style={{
              fontFamily: 'var(--font-display)',
              fontSize: '1.1rem', fontWeight: 700,
              color: 'var(--text)', marginBottom: '8px',
            }}>
              Ahmed<span style={{ color: 'var(--accent)', fontStyle: 'italic' }}>.</span>
            </div>
            <p style={{ fontFamily: 'var(--font-body)', fontSize: '0.82rem', color: 'var(--muted)', lineHeight: 1.6 }}>
              Economist &amp; Data Analyst
            </p>
          </div>

          {[
            { heading: 'Work', links: [
              { label: 'Projects',   href: `/${locale}/projects` },
              { label: 'Articles',   href: `/${locale}/articles` },
              { label: 'About',      href: `/${locale}/about` },
            ]},
            { heading: 'External', links: [
              { label: 'GitHub ↗',   href: 'https://github.com' },
              { label: 'LinkedIn ↗', href: 'https://linkedin.com' },
              { label: 'CIROPrep ↗', href: 'https://ciroprep.ca' },
            ]},
          ].map(col => (
            <div key={col.heading}>
              <p style={{ fontFamily: 'var(--font-mono)', fontSize: '0.69rem', textTransform: 'uppercase', letterSpacing: '0.1em', color: 'var(--muted)', marginBottom: '12px' }}>
                {col.heading}
              </p>
              {col.links.map(l => (
                <div key={l.label} style={{ marginBottom: '6px' }}>
                  <Link href={l.href} style={{ fontFamily: 'var(--font-body)', fontSize: '0.875rem', color: 'var(--text-2)', textDecoration: 'none' }}>
                    {l.label}
                  </Link>
                </div>
              ))}
            </div>
          ))}
        </div>

        <div style={{
          borderTop: '1px solid var(--border)', paddingTop: '20px',
          display: 'flex', justifyContent: 'space-between',
          alignItems: 'center', flexWrap: 'wrap', gap: '8px',
        }}>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.72rem', color: 'var(--muted)' }}>
            © {year} Ahmed. All rights reserved.
          </span>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.72rem', color: 'var(--muted)' }}>
            Built with Next.js · GitHub Pages
          </span>
        </div>
      </div>
    </footer>
  );
}
