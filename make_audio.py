#!/usr/bin/env python3
"""Extract article body text from a Sinapeos post and generate Edge TTS audio."""
import re, subprocess, sys, os

slug = sys.argv[1]
src = f"/root/sinapeos/src/pages/posts/{slug}.astro"
out = f"/root/sinapeos/public/audio/{slug}.mp3"
tmp = f"/tmp/{slug}-text.txt"

c = open(src, encoding="utf-8").read()
start = c.find('<div class="article-body">')
if start == -1:
    print("ERROR: article-body not found"); sys.exit(1)
start += len('<div class="article-body">')
depth, pos = 1, start
while depth > 0 and pos < len(c):
    op = c.find('<div', pos)
    cl = c.find('</div>', pos)
    if cl == -1:
        break
    if op != -1 and op < cl:
        depth += 1; pos = op + 5
    else:
        depth -= 1; pos = cl + 6
body = c[start:pos - 6]

# strip the audio player block so the mp3 does not read its own player markup.
# The player nests two divs, so a lazy regex never matched it and the mp3 opened
# with "Listen to this story". Walk the divs to the player's matching close instead.
def _strip_audio_player(html):
    key = '<div class="audio-player"'
    i = html.find(key)
    if i == -1:
        return html
    depth, pos = 1, i + len(key)
    while depth > 0 and pos < len(html):
        op = html.find('<div', pos)
        cl = html.find('</div>', pos)
        if cl == -1:
            break
        if op != -1 and op < cl:
            depth += 1
            pos = op + 5
        else:
            depth -= 1
            pos = cl + 6
    return html[:i] + html[pos:]

body = _strip_audio_player(body)
body = re.sub(r'<svg.*?</svg>', ' ', body, flags=re.S)
text = re.sub(r'<[^>]+>', ' ', body)
for a, b in [('&amp;', '&'), ('&lt;', '<'), ('&gt;', '>'), ('&quot;', '"'), ('&#39;', "'"), ('&nbsp;', ' ')]:
    text = text.replace(a, b)
# headings: add a period so TTS pauses naturally
text = re.sub(r'\n{3,}', '\n\n', text)
text = re.sub(r'[ \t]{2,}', ' ', text).strip()
# NOTE: no character cap. A [:15000] slice here silently truncated long posts
# (leaded-gasoline body is ~35k chars) so the mp3 covered less than half the story.
# edge-tts splits long input into chunks on its own.

open(tmp, 'w', encoding='utf-8').write(text)
words = len(text.split())
print(f"extracted {words} words -> {tmp}")

r = subprocess.run(["/root/.ttsvenv/bin/edge-tts", "--voice", "en-US-AvaNeural",
                    "--rate=+0%", "--pitch=-5Hz", "-f", tmp, "--write-media", out],
                   capture_output=True, text=True)
if r.returncode != 0:
    print("TTS FAILED:", r.stderr[-800:]); sys.exit(1)

size = os.path.getsize(out)
print(f"audio written: {out} ({size/1024/1024:.2f} MB)")
os.remove(tmp)
