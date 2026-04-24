const createNextIntlPlugin = require('next-intl/plugin');
const withNextIntl = createNextIntlPlugin('./i18n.ts');

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  images: { unoptimized: true },
  // Uncomment + replace if repo name is NOT yourusername.github.io:
  // basePath: '/ahmed-portfolio',
  // assetPrefix: '/ahmed-portfolio/',
};

module.exports = withNextIntl(nextConfig);
