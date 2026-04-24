export interface Project {
  id:           string;
  title:        string;
  description:  string;
  stack?:       string[];
  github?:      string;
  live?:        string;
  dashboard?:   string;
  status?:      'live' | 'in progress' | 'archived';
  year?:        number;
  featured?:    boolean;
}

// Add your real projects here
export const PROJECTS: Project[] = [
  {
    id:          'energy-crisis-dashboard',
    title:       'Middle East Energy Crisis — Interactive Dashboard',
    description: 'Interactive Plotly dashboard analyzing the 2023–2024 Middle East energy shock on Mauritania and global markets. Uses OLS regression, Chow tests, and Synthetic Control Method.',
    stack:       ['Python', 'Plotly', 'Pandas'],
    dashboard:   '/dashboards/dashboard.html',
    status:      'live',
    year:        2024,
    featured:    true,
  },
  {
    id:          'ciro-question-bank',
    title:       'CIROPrep Question Bank Generator',
    description: 'Python pipeline using Claude claude-sonnet-4-20250514 to expand a CIRO Retail Securities exam question bank from 30 seed questions to 1,000+ variations across all 23 learning outcomes.',
    stack:       ['Python', 'Pandas'],
    github:      'https://github.com',
    status:      'live',
    year:        2024,
    featured:    true,
  },
  {
    id:          'mauritania-trade-analysis',
    title:       'Mauritania Trade Flow Analysis',
    description: 'Empirical analysis of Mauritania\'s trade partner concentration and fuel import vulnerability using UN COMTRADE and World Bank data.',
    stack:       ['Python', 'Pandas', 'Plotly'],
    github:      'https://github.com',
    status:      'in progress',
    year:        2024,
    featured:    false,
  },
  {
    id:          'synthetic-control-africa',
    title:       'Synthetic Control Toolkit for African Economies',
    description: 'Reusable Python implementation of the Synthetic Control Method (Abadie et al. 2010) for causal inference on African macro data. No specialized packages required.',
    stack:       ['Python', 'Pandas'],
    github:      'https://github.com',
    status:      'in progress',
    year:        2024,
    featured:    false,
  },
];

export function getFeaturedProjects(): Project[] {
  return PROJECTS.filter(p => p.featured);
}

export function getAllProjects(): Project[] {
  return PROJECTS;
}
