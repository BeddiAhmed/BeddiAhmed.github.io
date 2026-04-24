import { useTranslations } from 'next-intl';
import { setRequestLocale } from 'next-intl/server';
import { locales, type Locale } from '../../../i18n';
import { getAllProjects } from '../../../lib/projects';
import ProjectCard from '../../../components/ProjectCard';

interface Props { params: { locale: Locale } }

export function generateStaticParams() {
  return locales.map(locale => ({ locale }));
}

export default function ProjectsPage({ params: { locale } }: Props) {
  setRequestLocale(locale);
  const t = useTranslations('projects');
  const projects = getAllProjects();

  const live       = projects.filter(p => p.status === 'live');
  const inProgress = projects.filter(p => p.status !== 'live' && p.status !== 'archived');
  const archived   = projects.filter(p => p.status === 'archived');

  return (
    <div style={{ maxWidth: '1120px', margin: '0 auto', padding: '64px 24px 80px' }}>

      {/* Header */}
      <div style={{ marginBottom: '56px', maxWidth: '640px' }}>
        <span style={{
          fontFamily: 'JetBrains Mono, monospace',
          fontSize: '0.7rem', textTransform: 'uppercase',
          letterSpacing: '0.1em', color: '#C9973A', display: 'block',
          marginBottom: '14px',
        }}>
          Work
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

      {/* Live projects */}
      {live.length > 0 && (
        <section style={{ marginBottom: '56px' }}>
          <div style={{
            display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px',
          }}>
            <span style={{
              width: '8px', height: '8px', borderRadius: '50%',
              background: '#4A8A6A', display: 'inline-block',
              boxShadow: '0 0 8px #4A8A6A',
            }} />
            <h2 style={{
              fontFamily: 'JetBrains Mono, monospace',
              fontSize: '0.78rem', textTransform: 'uppercase',
              letterSpacing: '0.1em', color: '#4A8A6A', margin: 0,
            }}>
              Live
            </h2>
          </div>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))',
            gap: '16px',
          }}>
            {live.map((project, i) => (
              <ProjectCard key={project.id} project={project} locale={locale} index={i} />
            ))}
          </div>
        </section>
      )}

      {/* In progress */}
      {inProgress.length > 0 && (
        <section style={{ marginBottom: '56px' }}>
          <div style={{
            display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px',
          }}>
            <span style={{
              width: '8px', height: '8px', borderRadius: '50%',
              background: '#C9973A', display: 'inline-block',
            }} />
            <h2 style={{
              fontFamily: 'JetBrains Mono, monospace',
              fontSize: '0.78rem', textTransform: 'uppercase',
              letterSpacing: '0.1em', color: '#C9973A', margin: 0,
            }}>
              In Progress
            </h2>
          </div>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))',
            gap: '16px',
          }}>
            {inProgress.map((project, i) => (
              <ProjectCard key={project.id} project={project} locale={locale} index={i} />
            ))}
          </div>
        </section>
      )}

      {/* Archived */}
      {archived.length > 0 && (
        <section>
          <div style={{
            display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px',
          }}>
            <h2 style={{
              fontFamily: 'JetBrains Mono, monospace',
              fontSize: '0.78rem', textTransform: 'uppercase',
              letterSpacing: '0.1em', color: '#6B6560', margin: 0,
            }}>
              Archived
            </h2>
          </div>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))',
            gap: '16px',
            opacity: 0.6,
          }}>
            {archived.map((project, i) => (
              <ProjectCard key={project.id} project={project} locale={locale} index={i} />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
