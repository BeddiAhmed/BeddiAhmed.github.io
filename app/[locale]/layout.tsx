import { notFound } from 'next/navigation';
import { NextIntlClientProvider } from 'next-intl';
import { getMessages, setRequestLocale } from 'next-intl/server';
import { locales, localeDir, type Locale } from '../../i18n';
import Navbar from '../../components/Navbar';
import Footer from '../../components/Footer';

interface Props {
  children: React.ReactNode;
  params: { locale: string };
}

export function generateStaticParams() {
  return locales.map((locale) => ({ locale }));
}

export default async function LocaleLayout({ children, params: { locale } }: Props) {
  if (!locales.includes(locale as Locale)) notFound();

  setRequestLocale(locale);
  const messages = await getMessages({ locale });
  const dir = localeDir[locale as Locale];

  return (
    <html lang={locale} dir={dir}>
      <head>
        {/* Arabic font fallback */}
        {locale === 'ar' && (
          <link
            rel="stylesheet"
            href="https://fonts.googleapis.com/css2?family=Noto+Serif+Arabic:wght@300;400;500;600&display=swap"
          />
        )}
      </head>
      <body>
        <NextIntlClientProvider locale={locale} messages={messages}>
          <div className="flex flex-col min-h-screen">
            <Navbar locale={locale as Locale} />
            <main className="flex-1">{children}</main>
            <Footer locale={locale as Locale} />
          </div>
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
