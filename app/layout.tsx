import type { Metadata } from 'next';
import '../styles/globals.css';

export const metadata: Metadata = {
  title: { default: 'Ahmed — Economist & Data Analyst', template: '%s · Ahmed' },
  description: 'Data-driven economic analysis, African markets, and CIRO exam preparation.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return children;
}
