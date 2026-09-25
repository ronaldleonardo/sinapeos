# SESSION HANDOFF - TabletopHarvest Empire (paste di sesi baru)

Kontek siap lanjut. Memory (MEMORY.md/USER.md) + skill otoritatif, terapin terus.

## Status terakhir (mau lanjut dari sini)

1. **Sinapeos HIV + Whale article** - udah di-rewrite pake Character Deep-Dive Pass (skill sinapeos section baru): setiap artikel wajib second-pass - riset backstory protagonist (asal-usul, kegagalan, personal stakes), ditulis gaya cerita bukan textbook, tiap detail relevan ke struggle/breakthrough, underdog cuma kalau fakta, ekspansi jadi 10-20 menit baca. HIV (David Ho: nunggu 8 tahun buat bapak + percaya angka) & Whale (Bob Hunter: mind bomb/media). Live + audio fixed + push. Skill udah di-update.
2. **Cloudflare audio cache gotcha (penting buat semua site):** edge-nyimpen .mp3 lama. Tiap regen audio wajib cache-bust URL pake ?v=N di `<source src>` artikel, verify ukuran publik vs lokal (public/audio/). Udah ditulis di skill sinapeos → Audio Pipeline.

## Pending thread (belum dikerjain, user minta stop dulu)

- TH G9 pillar auto-publish sama cron (job_id fed1b5ffc76a): "Grow 30% of Your Food Indoors" → /posts/grow-30-percent-of-your-food. Hero image DIHAPUS 09-24 (SVG→PNG keliatan jelek): artikel sekarang tanpa hero, og:image fallback default. Pasang gambar real kapan Atlas jalan — prompt pack udah dikasih ke user di chat.

### Verified 2026-09-24 (catatan Hermes, bukan dari user)

- cron fed1b5ffc76a masih ENABLED: daily 02:00 UTC, next run 2026-09-25T02:00. Belum di-pause (gak gw pause tanpa konfirmasi). Artikel G9 sudah live (ke-publish 09-24T02:08).
- Pipeline next = G10. Image-gen berbayar MATI: OpenRouter 403, Gemini quota habis (config image_gen = openrouter / google/gemini-3-pro-image). Kebijakan gambar (user 09-24): JANGAN generate gambar apa pun (no image_generate, no SVG placeholder) — tulis PROMPT PACK di laporan/chat aja, user yang generate lokal di Atlas. Cron prompt 10PGB udah di-update sesuai.
- Atlas (192.168.18.4): Open WebUI :3000 + Firecrawl :3002 UP; ComfyUI 8188, SD WebUI 7860, Ollama 11434, 3001/5000/8888 gak reachable. Arah user (09-24): gambar dibuat LOKAL di Atlas, prompt dikirim via Telegram; bridge/endpoint-nya belum ada, perlu setup.
- Audit OpenRouter 09-24 (user matiin quota buat investigasi siapa yang make): konsumen = (1) image_gen (semua cron pipeline artikel: TH Daily, TH Pillar, GTDB, BGDB, Sinapeos; model openai/gpt-5.4-image-2 lalu google/gemini-3-pro-image), (2) vision_analyze (Evening Article Review & cron QC gambar), (3) auxiliary.compression (google/gemini-3-flash, sesi panjang), (4) fallback_providers (deepseek via OR kalau opencode-go down). Model utama = opencode-go. Sejak quota mati semua balikin 403.
- File ini dibuat 2026-09-24, belum ada HANDOFF.md sebelumnya.

## Cara deploy (biar cepat)

- TH: `npx astro build && systemctl restart tabletopharvest` (serve :8080, publik cloudflared tunnel → tabletopharvest.com)
- Sinapeos: `npx astro build && systemctl restart sinapeos` (serve :8084 → sinapeos.com), audio/gambar wajib cache-bust ?v=N
- Git push tiap kelar, token di /root/.github-token.

## Rule wajib

No em dash di mana pun. Headline + content site-lo pake grep sebelum kelar: `grep -rn '—' src/pages/`