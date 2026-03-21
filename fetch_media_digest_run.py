import urllib.request, re, os, sys
from datetime import date
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def fetch_html(channel):
    url = f"https://t.me/s/{channel}"
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

media_dir = f"My_Knowledge_Base/Digest_Media/{date.today().isoformat()}"
os.makedirs(media_dir, exist_ok=True)

selected = [
    ('gpt_5_4',            'seeallochnaya',    ['GPT-5.4', 'gpt-5-4', '1M token', '1М токен', 'gpt-5.4']),
    ('claude_code_review', 'seeallochnaya',    ['code review', 'Code Review', 'claude.com/blog', '$15', '$25']),
    ('runway_characters',  'AcidCrunch',       ['Characters', 'runway', 'runwayml']),
    ('grok_references',    'neyr0graph',       ['References', 'Grok', '7 reference', '7 референс', 'компонент']),
    ('tencent_hy_3d',      'data_analysis_ml', ['HY 3D Studio', 'hunyuan', '3D', 'HY-WorldPlay', 'Tencent']),
    ('photoshop_rotate',   'cgevent',          ['Rotate Object', 'Photoshop', 'rotation', 'вращени']),
    ('perplexity_pc',      'data_secrets',     ['Personal Computer', 'Perplexity', 'Mac mini', 'perplexity.ai']),
    ('claude_auto_memory', 'tips_ai',          ['Auto Memory', 'MEMORY.md', '/memory', 'memory', 'Memory']),
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
            print(f"[{slug}] пост не найден в {channel}")
            continue
        media = [('photo', u) for u in matched['photos']] + [('video', u) for u in matched['videos']]
        if not media:
            print(f"[{slug}] нет медиа в посте (текст: {matched['text'][:80]})")
            continue
        for idx, (kind, url) in enumerate(media, 1):
            ext = url.split('?')[0].split('.')[-1][:4]
            if ext not in ('jpg', 'jpeg', 'png', 'gif', 'mp4', 'webp'):
                ext = 'jpg' if kind == 'photo' else 'mp4'
            filename = f"{media_dir}/{slug}_{idx}.{ext}"
            download_file(url, filename)
            saved_all.append(filename)
            print(f"Сохранено: {filename}")
    except Exception as e:
        print(f"[{slug}] ошибка: {e}")

print(f"\nИтого: {len(saved_all)} файлов в {media_dir}")
