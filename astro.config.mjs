import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://sinapeos.com',
  compressHTML: true,
  devToolbar: { enabled: false },
  integrations: [sitemap()],
  build: {
    format: 'file',
  },
  server: {
    host: '0.0.0.0',
    port: 8084,
    allowedHosts: ['sinapeos.com', 'www.sinapeos.com', 'mia.ronaldleonardo.com'],
  },
});