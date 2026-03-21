# -*- coding: utf-8 -*-
import sys, io, urllib.request, re, os
from datetime import date

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def fetch_html(channel):
    url = "https://t.me/s/" + channel
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read().decode('utf-8', errors='replace')

def parse_posts(html):
    posts = []
    blocks = re.split(r'(?=<div class="tgme_widget_message_wrap)', html)
    for block in blocks:
        text_parts = re.findall(r'<div[^>]*class="[^"]*tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>', block, re.DOTALL)
        text = ' '.join(re.sub(r'<[^>]+>', ' ', t) for t in text_parts).strip()
        photos = re.findall(
            r'tgme_widget_message_photo_wrap[^"]*"[^>]*style="[^"]*background-image:url\(\'([^\']+)\'\)',
            block
        )
        videos = re.findall(r'<video[^>]+src="([^"]+)"', block)
        if text or photos or videos:
            posts.append({'text': text, 'photos': photos, 'videos': videos})
    return posts

def download_file(url, path):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    with urllib.request.urlopen(req, timeout=20) as r:
        data = r.read()
    with open(path, 'wb') as f:
        f.write(data)

media_dir = "My_Knowledge_Base/Digest_Media/" + date.today().isoformat()
os.makedirs(media_dir, exist_ok=True)

selected = [
    ('gpt_5_4',            'seeallochnaya',    ['GPT-5.4', 'gpt-5-4', '1M token', 'computer use']),
    ('claude_code_review', 'tips_ai',          ['code review', 'Code Review', 'claude.com/blog']),
    ('runway_characters',  'AcidCrunch',       ['Characters', 'runway', 'runwayml', 'avatar']),
    ('grok_references',    'neyr0graph',       ['References', 'Grok', '7 reference']),
    ('tencent_hy_3d',      'data_analysis_ml', ['HY 3D Studio', 'hunyuan', '3D Studio']),
    ('photoshop_rotate',   'neyr0graph',       ['Rotate Object', 'Photoshop', 'rotation']),
    ('perplexity_pc',      'data_secrets',     ['Personal Computer', 'Perplexity', 'Mac mini']),
    ('claude_auto_memory', 'tips_ai',          ['Auto Memory', 'MEMORY.md', 'Memory']),
    ('notebooklm_video',   'TochkiNadAI',      ['NotebookLM', 'cinematic', 'Veo']),
    ('gemini_embedding',   'data_analysis_ml', ['Gemini Embedding', 'embedding']),
]

saved_all = []

for slug, channel, keywords in selected:
    try:
        html = fetch_html(channel)
        posts = parse_posts(html)
        matched = None
        for post in posts:
            combined = (post['text'] + ' '.join(post['photos'] + post['videos'])).lower()
            if any(kw.lower() in combined for kw in keywords):
                matched = post
                break
        if not matched:
            print("[" + slug + "] post not found in " + channel)
            continue
        media = [('photo', u) for u in matched['photos']] + [('video', u) for u in matched['videos']]
        if not media:
            print("[" + slug + "] no media in post")
            continue
        for idx, (kind, url) in enumerate(media, 1):
            ext = url.split('?')[0].split('.')[-1][:4]
            if ext not in ('jpg', 'jpeg', 'png', 'gif', 'mp4', 'webp'):
                ext = 'jpg' if kind == 'photo' else 'mp4'
            filename = media_dir + "/" + slug + "_" + str(idx) + "." + ext
            download_file(url, filename)
            saved_all.append(filename)
            print("Saved: " + filename)
    except Exception as e:
        print("[" + slug + "] error: " + str(e))

print("\nTotal: " + str(len(saved_all)) + " files in " + media_dir)
