import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import { statSync, existsSync } from 'node:fs';
import { stories } from './src/data/stories.js';

// Every URL gets a real <lastmod>. Sinapeos publishes one story a week and has 7 pages
// Google still has not indexed, so a truthful "when did this file actually change" date
// is the one recrawl hint we can give it honestly.
const storyDates = new Map(stories.map((s) => [`/posts/${s.slug}`, s.date]));
const newest = stories.reduce((a, s) => (s.date > a ? s.date : a), '2026-01-01');

function changedOn(path) {
  const base = path.replace(/^\//, '');
  const candidates = [
    `src/pages/${base || 'index'}.astro`,
    `src/pages/${base}/index.astro`,
  ];
  for (const f of candidates) {
    if (existsSync(f)) return statSync(f).mtime;
  }
  return null;
}

export default defineConfig({
  site: 'https://sinapeos.com',
  compressHTML: true,
  devToolbar: { enabled: false },
  integrations: [
    sitemap({
      serialize(item) {
        const path = new URL(item.url).pathname.replace(/\/$/, '') || '/';
        const published = new Date(`${storyDates.get(path) || newest}T06:00:00Z`);
        const edited = changedOn(path);
        const stamp = edited && edited > published ? edited : published;
        item.lastmod = stamp.toISOString();
        return item;
      },
    }),
  ],
  build: {
    format: 'file',
  },
  server: {
    host: '0.0.0.0',
    port: 8084,
    allowedHosts: ['sinapeos.com', 'www.sinapeos.com', 'mia.ronaldleonardo.com'],
  },
});