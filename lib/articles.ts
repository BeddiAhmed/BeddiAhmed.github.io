import fs from 'fs';
import path from 'path';
import matter from 'gray-matter';
import { remark } from 'remark';
import remarkHtml from 'remark-html';
import type { Locale } from '../i18n';

const ARTICLES_DIR = path.join(process.cwd(), 'content', 'articles');

export interface ArticleMeta {
  slug:       string;
  title:      string;
  date:       string;
  excerpt?:   string;
  category?:  string;
  tags?:      string[];
  readTime?:  number;
  locale:     Locale;
  dashboard?: boolean;
}

export interface Article extends ArticleMeta {
  content: string;  // HTML string
}

export function getArticleSlugs(locale: Locale): string[] {
  const dir = path.join(ARTICLES_DIR, locale);
  if (!fs.existsSync(dir)) return [];
  return fs.readdirSync(dir)
    .filter(f => f.endsWith('.md'))
    .map(f => f.replace(/\.md$/, ''));
}

export function getArticleMeta(slug: string, locale: Locale): ArticleMeta | null {
  const filePath = path.join(ARTICLES_DIR, locale, `${slug}.md`);
  if (!fs.existsSync(filePath)) {
    // Fall back to English if translation doesn't exist yet
    const enPath = path.join(ARTICLES_DIR, 'en', `${slug}.md`);
    if (!fs.existsSync(enPath)) return null;
    const { data } = matter(fs.readFileSync(enPath, 'utf8'));
    return { slug, locale, ...data } as ArticleMeta;
  }
  const { data } = matter(fs.readFileSync(filePath, 'utf8'));
  return { slug, locale, ...data } as ArticleMeta;
}

export async function getArticle(slug: string, locale: Locale): Promise<Article | null> {
  let filePath = path.join(ARTICLES_DIR, locale, `${slug}.md`);
  if (!fs.existsSync(filePath)) {
    filePath = path.join(ARTICLES_DIR, 'en', `${slug}.md`);
    if (!fs.existsSync(filePath)) return null;
  }
  const raw = fs.readFileSync(filePath, 'utf8');
  const { data, content: mdContent } = matter(raw);
  const processed = await remark().use(remarkHtml).process(mdContent);
  return {
    slug, locale,
    content: processed.toString(),
    ...data,
  } as Article;
}

export function getAllArticles(locale: Locale): ArticleMeta[] {
  // Collect slugs from both the locale dir and en (union, locale takes priority)
  const localeSlugs = getArticleSlugs(locale);
  const enSlugs     = getArticleSlugs('en');
  const allSlugs    = [...new Set([...localeSlugs, ...enSlugs])];

  return allSlugs
    .map(slug => getArticleMeta(slug, locale))
    .filter((a): a is ArticleMeta => a !== null)
    .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
}
