import type { Project } from '../lib/projects';
import type { Locale } from '../i18n';

interface Props { project: Project; locale: Locale; index?: number; featured?: boolean; }

const STACK_COLORS: Record<string, string> = {
  Python: '#1A3A5C', R: '#1A6644', 'Next.js': '#B8821E',
  Plotly: '#6644AA', SQL: '#B83232', Pandas: '#1A5C4A',
};

export default function ProjectCard({ project, index = 0, featured = false }: Props) {
  const statusColor = project.status === 'live'
    ? { dot: '#1A6644', label: '#1A6644', bg: '#EEF8F3' }
    : { dot: '#B8821E', label: '#B8821E', bg: '#FBF5E9' };

  return (
    <article style={{
      background: featured ? 'var(--bg-subtle)' : 'var(--bg)',
      border: '1px solid var(--border)',
      borderRadius: '6px',
      padding: featured ? '28px' : '24px',
      display: 'flex', flexDirection: 'column', gap: '12px',
      height: '100%',
      transition: 'border-color .18s, box-shadow .18s, transform .18s',
      animationDelay: `${index * 0.07}s`,
    }}
      className="animate-fade-up project-card"
    >
      {/* Status + year */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{
          fontFamily: 'var(--font-mono)',
          fontSize: '0.67rem', letterSpacing: '0.07em',
          textTransform: 'uppercase', fontWeight: 500,
          padding: '2px 8px', borderRadius: '3px',
          background: statusColor.bg, color: statusColor.label,
          display: 'flex', alignItems: 'center', gap: '5px',
        }}>
          <span style={{
            width: '5px', height: '5px', borderRadius: '50%',
            background: statusColor.dot, display: 'inline-block',
            boxShadow: project.status === 'live' ? '0 0 5px ' + statusColor.dot : 'none',
          }} />
          {project.status ?? 'in progress'}
        </span>
        {project.year && (
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.69rem', color: 'var(--muted)' }}>
            {project.year}
          </span>
        )}
      </div>

      {/* Title */}
      <h3 style={{
        fontFamily: 'var(--font-display)',
        fontSize: featured ? '1.2rem' : '1.05rem',
        fontWeight: 600, color: 'var(--text)',
        lineHeight: 1.3, letterSpacing: '-0.015em',
      }}>
        {project.title}
      </h3>

      {/* Description */}
      <p style={{
        fontFamily: 'var(--font-body)',
        fontSize: '0.875rem', color: 'var(--text-2)',
        lineHeight: 1.65, flex: 1,
      }}>
        {project.description}
      </p>

      {/* Stack */}
      {project.stack && (
        <div style={{ display: 'flex', gap: '5px', flexWrap: 'wrap' }}>
          {project.stack.map(tech => (
            <span key={tech} style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '0.65rem', letterSpacing: '0.04em',
              padding: '2px 7px', borderRadius: '3px',
              background: 'var(--bg-raised)', border: '1px solid var(--border)',
              color: STACK_COLORS[tech] ?? 'var(--text-2)',
              fontWeight: 500,
            }}>
              {tech}
            </span>
          ))}
        </div>
      )}

      {/* Links */}
      <div style={{ display: 'flex', gap: '14px', flexWrap: 'wrap', paddingTop: '4px', borderTop: '1px solid var(--border)' }}>
        {project.github && (
          <a href={project.github} target="_blank" rel="noopener noreferrer"
            style={{ fontFamily: 'var(--font-body)', fontSize: '0.82rem', fontWeight: 500, color: 'var(--accent)', textDecoration: 'none' }}>
            GitHub →
          </a>
        )}
        {project.dashboard && (
          <a href={project.dashboard} target="_blank" rel="noopener noreferrer"
            style={{ fontFamily: 'var(--font-body)', fontSize: '0.82rem', fontWeight: 500, color: '#6644AA', textDecoration: 'none' }}>
            Dashboard →
          </a>
        )}
        {project.live && (
          <a href={project.live} target="_blank" rel="noopener noreferrer"
            style={{ fontFamily: 'var(--font-body)', fontSize: '0.82rem', fontWeight: 500, color: 'var(--green)', textDecoration: 'none' }}>
            Live →
          </a>
        )}
      </div>
    </article>
  );
}
