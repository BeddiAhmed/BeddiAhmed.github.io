'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { locales, localeNames, type Locale } from '../i18n';

interface NavbarProps { locale: Locale; }

export default function Navbar({ locale }: NavbarProps) {
  const t = useTranslations('nav');
  const pathname = usePathname();

  function localePath(targetLocale: Locale) {
    const segments = pathname.split('/');
    segments[1] = targetLocale;
    return segments.join('/') || `/${targetLocale}`;
  }

  const navLinks = [
    { href: `/${locale}/projects`, label: t('projects') },
    { href: `/${locale}/articles`, label: t('articles') },
    { href: `/${locale}/analysis`, label: t('analysis') },
    { href: `/${locale}/about`,    label: t('about') },
  ];

  const isActive = (href: string) => pathname === href || pathname === href + '/';

  return (
    <header style={{
      position: 'sticky', top: 0, zIndex: 50,
      background: 'rgba(255,255,255,0.92)',
      backdropFilter: 'blur(12px)',
      borderBottom: '1px solid var(--border)',
    }}>
      <nav style={{
        maxWidth: '1100px', margin: '0 auto',
        padding: '0 32px',
        display: 'flex', alignItems: 'center',
        height: '58px', gap: '8px',
      }}>

        {/* Logo */}
        <Link href={`/${locale}`} style={{
          fontFamily: 'var(--font-display)',
          fontSize: '1.05rem', fontWeight: 700,
          color: 'var(--text)', textDecoration: 'none',
          letterSpacing: '-0.02em', marginInlineEnd: 'auto',
          display: 'flex', alignItems: 'center', gap: '2px',
        }}>
          Ahmed
          <span style={{ color: 'var(--accent)', fontStyle: 'italic' }}>.</span>
        </Link>

        {/* Nav links */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '2px' }} className="nav-links">
          {navLinks.map(link => (
            <Link key={link.href} href={link.href} style={{
              fontFamily: 'var(--font-body)',
              fontSize: '0.875rem',
              fontWeight: isActive(link.href) ? 600 : 400,
              color: isActive(link.href) ? 'var(--accent)' : 'var(--text-2)',
              textDecoration: 'none',
              padding: '6px 14px',
              borderRadius: '4px',
              background: isActive(link.href) ? 'var(--accent-subtle)' : 'transparent',
              transition: 'background .15s, color .15s',
            }}>
              {link.label}
            </Link>
          ))}
        </div>

        {/* Divider */}
        <div style={{ width: '1px', height: '20px', background: 'var(--border)', margin: '0 10px' }} className="nav-links" />

        {/* Language switcher */}
        <div style={{ display: 'flex', gap: '2px' }}>
          {(locales as readonly Locale[]).map(loc => (
            <Link key={loc} href={localePath(loc)} style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '0.69rem', letterSpacing: '0.07em',
              textTransform: 'uppercase',
              color: loc === locale ? 'var(--accent)' : 'var(--muted)',
              textDecoration: 'none',
              padding: '4px 8px',
              borderRadius: '3px',
              background: loc === locale ? 'var(--accent-subtle)' : 'transparent',
              fontWeight: loc === locale ? 600 : 400,
              transition: 'background .15s, color .15s',
            }}>
              {loc.toUpperCase()}
            </Link>
          ))}
        </div>

        {/* CTA */}
        <Link href={`/${locale}/articles`} className="btn-primary" style={{
          marginInlineStart: '10px', fontSize: '0.82rem',
          padding: '8px 18px',
        }} aria-label="Read articles">
          Read →
        </Link>
      </nav>

      <style>{`
        @media (max-width: 680px) {
          .nav-links { display: none !important; }
        }
      `}</style>
    </header>
  );
}
