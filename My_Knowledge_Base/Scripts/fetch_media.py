import urllib.request, re, os, sys
from datetime import date

# Fix Windows encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

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
        text_parts = re.findall(
            r'<div[^>]*class="[^"]*tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>',
            block, re.DOTALL
        )
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

import json

CHANNELS = [
    'neyr0graph', 'cgevent', 'data_secrets', 'TochkiNadAI',
    'tips_ai', 'seeallochnaya', 'AcidCrunch', 'data_analysis_ml'
]

media_dir = f"My_Knowledge_Base/Digest_Media/{date.today().isoformat()}"
os.makedirs(media_dir, exist_ok=True)

# Читаем список из JSON если CC его записал, иначе используем дефолтный
JSON_PATH = f"My_Knowledge_Base/Digest_Media/media_selected.json"

DEFAULT_SELECTED = [
    ('gpt_5_4',            ['GPT-5.4'],                         ['1M', 'million', 'Computer Use', '/fast']),
    ('claude_code_review', ['claude.com/blog/code-review'],     []),
    ('claude_code_review', ['Code Review', 'Claude Code'],      ['pull request', 'PR', '$15', '$25']),
    ('runway_characters',  ['Runway', 'Characters'],            ['аватар', 'avatar', 'API', 'runwayml']),
    ('grok_references',    ['Grok', 'References'],              ['7', 'reference', 'референс']),
    ('tencent_hy_3d',      ['HY 3D Studio'],                   []),
    ('tencent_hy_3d',      ['HY-WorldPlay'],                    []),
    ('photoshop_rotate',   ['Rotate Object'],                   []),
    ('photoshop_rotate',   ['Photoshop'],                       ['поворот', 'rotation', '3D']),
    ('perplexity_pc',      ['Perplexity', 'Computer'],          ['Mac mini', 'автономн', 'локальн', 'Personal']),
    ('claude_auto_memory', ['Auto Memory'],                     []),
    ('claude_auto_memory', ['MEMORY.md'],                       []),
]

if os.path.exists(JSON_PATH):
    try:
        with open(JSON_PATH, encoding='utf-8') as f:
            raw = json.load(f)
        # Формат JSON: [{"slug": "...", "channel": "...", "must_all": [...], "any_of": [...]}]
        # channel — конкретный канал где CC нашёл пост (ищем только там)
        json_rules = raw  # сохраняем как список dict для доступа к полю channel
        selected = None   # будет использован json_rules вместо selected
        print(f"Используем список из {JSON_PATH} ({len(json_rules)} правил)")
        os.remove(JSON_PATH)  # удаляем после прочтения
    except Exception as e:
        print(f"Не удалось прочитать {JSON_PATH}: {e} — используем дефолтный список")
        json_rules = None
        selected = DEFAULT_SELECTED
else:
    json_rules = None
    selected = DEFAULT_SELECTED

# Кэш HTML по каналу
html_cache = {}

def get_html(channel):
    if channel not in html_cache:
        html_cache[channel] = fetch_html(channel)
    return html_cache[channel]

# Предзагрузка всех каналов
print("Загружаю каналы...")
for ch in CHANNELS:
    try:
        get_html(ch)
        print(f"  OK: {ch}")
    except Exception as e:
        print(f"  FAIL: {ch} — {e}")

def matches(post_text, must_all, any_of):
    t = post_text.lower()
    if not all(kw.lower() in t for kw in must_all):
        return False
    if any_of and not any(kw.lower() in t for kw in any_of):
        return False
    return True

# Группируем правила по slug
from collections import defaultdict

saved_all = []

if json_rules is not None:
    # Режим JSON: CC указал конкретный канал для каждой новости
    for item in json_rules:
        slug = item['slug']
        channel = item.get('channel', '')
        must_all = item.get('must_all', [])
        any_of = item.get('any_of', [])
        search_channels = [channel] if channel in CHANNELS else CHANNELS
        print(f"\n--- {slug} (канал: {channel or 'все'}) ---")
        all_media_urls = []
        for ch in search_channels:
            try:
                html = get_html(ch)
                posts = parse_posts(html)
                for post in posts:
                    if matches(post['text'], must_all, any_of):
                        new_media = post['photos'] + post['videos']
                        if new_media:
                            preview = post['text'][:60].replace('\n', ' ')
                            print(f"  [{ch}] {preview}... → {len(new_media)} медиа")
                            for u in new_media:
                                if u not in all_media_urls:
                                    all_media_urls.append(u)
                        break
            except Exception as e:
                print(f"  [{ch}] ошибка: {e}")
        if not all_media_urls:
            print(f"  [!] нет медиа")
            continue
        for idx, url in enumerate(all_media_urls, 1):
            try:
                ext = url.split('?')[0].split('.')[-1][:4]
                if ext not in ('jpg', 'jpeg', 'png', 'gif', 'mp4', 'webp'):
                    ext = 'jpg'
                filename = f"{media_dir}/{slug}_{idx}.{ext}"
                download_file(url, filename)
                saved_all.append(filename)
                print(f"  Сохранено: {filename}")
            except Exception as e:
                print(f"  [!] не удалось скачать: {e}")

else:
    # Режим DEFAULT: ищем по всем каналам с pre-tuned правилами
    rules_by_slug = defaultdict(list)
    slugs_order = []
    for row in selected:
        slug = row[0]
        rules_by_slug[slug].append((row[1], row[2]))
        if slug not in slugs_order:
            slugs_order.append(slug)

    for slug in slugs_order:
        rules = rules_by_slug[slug]
        print(f"\n--- {slug} ---")
        all_media_urls = []

        for channel in CHANNELS:
            try:
                html = get_html(channel)
                posts = parse_posts(html)
                for post in posts:
                    for must_all, any_of in rules:
                        if matches(post['text'], must_all, any_of):
                            new_media = post['photos'] + post['videos']
                            if new_media:
                                preview = post['text'][:60].replace('\n', ' ')
                                print(f"  [{channel}] {preview}... → {len(new_media)} медиа")
                                for u in new_media:
                                    if u not in all_media_urls:
                                        all_media_urls.append(u)
                            break
            except Exception as e:
                print(f"  [{channel}] ошибка: {e}")

        if not all_media_urls:
            print(f"  [!] нет медиа ни в одном канале")
            continue

        for idx, url in enumerate(all_media_urls, 1):
            try:
                ext = url.split('?')[0].split('.')[-1][:4]
                if ext not in ('jpg', 'jpeg', 'png', 'gif', 'mp4', 'webp'):
                    ext = 'jpg'
                filename = f"{media_dir}/{slug}_{idx}.{ext}"
                download_file(url, filename)
                saved_all.append(filename)
                print(f"  Сохранено: {filename}")
            except Exception as e:
                print(f"  [!] не удалось скачать: {e}")

print(f"\n=== Итого: {len(saved_all)} файлов в {media_dir} ===")
for f in saved_all:
    print(f"  {f}")
