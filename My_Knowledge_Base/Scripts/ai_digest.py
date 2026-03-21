#!/usr/bin/env python3
"""
Еженедельный AI-дайджест для @VAI_ART.
Пайплайн: TG-каналы → отбор новостей (Groq) → веб-поиск деталей → стилизация @VAI_ART (Groq) → Telegram.
Использование: python ai_digest.py
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone, timedelta
from html.parser import HTMLParser

from groq import Groq
from duckduckgo_search import DDGS

# Cover generator (same Scripts folder)
sys.path.insert(0, os.path.dirname(__file__))
from cover_gen import generate_cover

# === НАСТРОЙКИ ===
CHANNELS = [
    "neyr0graph",
    "cgevent",
    "data_secrets",
    "TochkiNadAI",
    "tips_ai",
    "seeallochnaya",
    "AcidCrunch",
    "data_analysis_ml",
]

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
TG_TOKEN = os.environ.get("TG_TOKEN", "")
TG_CHAT_ID = os.environ.get("TG_CHAT_ID", "")
TG_THREAD_DIGEST = os.environ.get("TG_THREAD_DIGEST", "")


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip = True
        if tag == "a":
            href = dict(attrs).get("href", "")
            if href and href.startswith("http") and "t.me" not in href:
                self.parts.append(f"[{href}]")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip = False
        if tag in ("div", "p", "br", "li"):
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.skip:
            text = data.strip()
            if text:
                self.parts.append(text)

    def get_text(self):
        text = " ".join(self.parts)
        text = re.sub(r" {2,}", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()


def fetch_channel(channel):
    url = f"https://t.me/s/{channel}"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; bot)"}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            html = r.read().decode("utf-8", errors="replace")
        parser = TextExtractor()
        parser.feed(html)
        return parser.get_text()
    except Exception as e:
        print(f"Warning: не удалось загрузить {channel}: {e}", file=sys.stderr)
        return ""


def send_telegram(text):
    import html as _html

    if len(text) > 4096:
        text = text[:4090] + "..."

    def _post(payload_dict):
        data = json.dumps(payload_dict).encode("utf-8")
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
            data=data,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read()).get("ok", False)

    base = {"chat_id": TG_CHAT_ID, "text": text}
    if TG_THREAD_DIGEST:
        base["message_thread_id"] = int(TG_THREAD_DIGEST)

    print(f"DEBUG send_telegram: chat_id={TG_CHAT_ID} thread={TG_THREAD_DIGEST} keys={list(base.keys())}")

    # Попытка 1: HTML
    try:
        return _post({**base, "parse_mode": "HTML"})
    except urllib.error.HTTPError as e:
        if e.code == 400:
            err_body = e.read().decode("utf-8", errors="replace")
            print(f"Telegram HTML rejected: {err_body}", file=sys.stderr)
        else:
            raise

    # Попытка 2: plain text — убираем теги и html-entities
    plain = re.sub(r"<[^>]+>", "", text)
    plain = _html.unescape(plain)
    return _post({**base, "text": plain})


def send_telegram_photo(photo_path):
    import base64
    with open(photo_path, "rb") as f:
        photo_b64 = base64.b64encode(f.read()).decode()

    # Use sendPhoto with file_id via input_media — actually use multipart but with explicit logging
    boundary = "----FormBoundary7MA4YWxkTrZu0gW"
    parts = []
    parts.append(
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"chat_id\"\r\n\r\n{TG_CHAT_ID}\r\n"
    )
    if TG_THREAD_DIGEST:
        parts.append(
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"message_thread_id\"\r\n\r\n{TG_THREAD_DIGEST}\r\n"
        )
        print(f"Sending photo to thread_id={TG_THREAD_DIGEST}")

    photo_data = base64.b64decode(photo_b64)
    body = "".join(parts).encode() + (
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"photo\"; filename=\"cover.png\"\r\n"
        f"Content-Type: image/png\r\n\r\n"
    ).encode() + photo_data + f"\r\n--{boundary}--\r\n".encode()

    req = urllib.request.Request(
        f"https://api.telegram.org/bot{TG_TOKEN}/sendPhoto",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
    )
    with urllib.request.urlopen(req) as r:
        resp = json.loads(r.read())
        print(f"Photo response: {resp.get('ok')} thread={resp.get('result', {}).get('message_thread_id')}")
        return resp.get("ok", False)


def ask_groq(client, prompt):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000,
    )
    return response.choices[0].message.content.strip()


def extract_news(client, channels_content):
    """Шаг 1: Отбираем новости и возвращаем JSON."""
    now = datetime.now(timezone.utc)

    prompt = f"""Сегодня {now.strftime('%d.%m.%Y')}.

Вот тексты постов из Telegram-каналов за последние 7 дней:

{channels_content}

---

Из этих постов отбери до 10 продуктовых AI-новостей.

ЧТО БЕРЁМ:
1. Запуск новой модели — GPT, Claude, Gemini, Midjourney, Sora, Flux, Kling и любые другие AI-модели
2. Обновление существующей модели — новые возможности, улучшение качества, новые модальности
3. Запуск нового AI-продукта или инструмента — только реальный релиз, не анонс
4. Изменение доступности или цен

ЧТО НЕ БЕРЁМ: корпоративные события, сделки, скандалы, исследования без релиза, политика, анонсы без выхода, реклама, курсы.

Верни ТОЛЬКО валидный JSON-массив, без лишнего текста:
[
  {{
    "name": "Название модели или продукта",
    "what": "Что именно вышло — одно предложение, только факт без оценок",
    "available": "Где доступно (платформа, API, сайт) — или пусто",
    "price": "Цена — или пусто",
    "features": "Конкретные фичи и возможности через запятую — что УМЕЕТ продукт. Не абстрактные слова а конкретика. Или пусто если в посте не указано",
    "url": "прямая ссылка на продукт/сайт/блог из поста — или пусто если нет",
    "keywords": ["ключевое", "слово", "из поста"],
    "needs_search": true,
    "search_query": "Поисковый запрос на английском"
  }}
]

Правило для keywords: 2-4 слова которые точно есть в оригинальном посте (на языке поста) — для поиска медиа. Обычно это название продукта/модели.

Правило для needs_search:
- false — если в посте уже есть конкретные фичи: что умеет, чем отличается, цифры
- true — если пост короткий или расплывчатый, фич нет или их мало"""

    raw = ask_groq(client, prompt)

    match = re.search(r'\[.*\]', raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    print("Warning: не удалось распарсить JSON, возвращаем пустой список", file=sys.stderr)
    return []


def search_product_details(query):
    """Шаг 2: Ищем детали о продукте через DuckDuckGo."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))

        key_terms = [w.lower() for w in query.split() if len(w) >= 4]
        snippets = []
        for r in results:
            title = r.get('title', '')
            body = r.get('body', '').strip()
            # Отсеиваем CJK (китайский, японский, корейский)
            cjk = sum(1 for c in body if '\u4e00' <= c <= '\u9fff' or '\u3040' <= c <= '\u30ff')
            if cjk / max(len(body), 1) > 0.03:
                continue
            combined = (title + " " + body).lower()
            if key_terms and not any(t in combined for t in key_terms):
                continue
            if body:
                snippets.append(body[:250])
            if len(snippets) >= 3:
                break

        return " | ".join(snippets)
    except Exception as e:
        print(f"  Search warning для '{query}': {e}", file=sys.stderr)
        return ""


def generate_slug(name):
    """Название продукта → lower_snake_case для имён файлов."""
    slug = name.lower()
    slug = re.sub(r'[^\w\s.-]', '', slug)
    slug = re.sub(r'[\s.-]+', '_', slug.strip())
    return slug.strip('_')


def fetch_raw_html(channel):
    """Возвращает сырой HTML страницы канала."""
    url = f"https://t.me/s/{channel}"
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read().decode('utf-8', errors='replace')


def parse_posts_media(html):
    """Из сырого HTML канала возвращает [{text, photos, videos}]."""
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


def download_media_file(url, path):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    with urllib.request.urlopen(req, timeout=20) as r:
        data = r.read()
    with open(path, 'wb') as f:
        f.write(data)


def download_news_media(news_items, media_dir):
    """
    Скачивает медиа для каждой новости из всех каналов.
    Ключевые слова берутся из имени продукта (words >= 3 chars).
    Возвращает список сохранённых файлов.
    """
    os.makedirs(media_dir, exist_ok=True)

    # Кэшируем сырой HTML всех каналов
    html_cache = {}
    print("  Загружаю сырой HTML каналов для медиа...")
    for ch in CHANNELS:
        try:
            html_cache[ch] = fetch_raw_html(ch)
        except Exception as e:
            print(f"  [{ch}] не удалось загрузить: {e}", file=sys.stderr)

    saved_files = []

    for item in news_items:
        slug = generate_slug(item['name'])
        # keywords от Groq — слова из оригинального поста
        raw_kw = item.get('keywords') or []
        if isinstance(raw_kw, str):
            raw_kw = [raw_kw]
        # Fallback: берём из name если keywords пусто
        if not raw_kw:
            stop = {'the', 'and', 'for', 'with', 'new', 'from'}
            raw_kw = [
                w for w in re.findall(r'[\w.]+', item['name'])
                if len(w) >= 3 and w.lower() not in stop
            ]
        # Максимум 2 ключевых слова (меньше ложных пропусков)
        kw_strict = raw_kw[:2]
        if not kw_strict:
            continue
        print(f"  [{slug}] ищу по: {kw_strict}")

        all_media_urls = []

        for channel, html in html_cache.items():
            try:
                posts = parse_posts_media(html)
                matched = 0
                for post in posts:
                    t = post['text'].lower()
                    if all(kw.lower() in t for kw in kw_strict):
                        media = post['photos'] + post['videos']
                        matched += len(media)
                        for u in media:
                            if u not in all_media_urls:
                                all_media_urls.append(u)
                if matched:
                    print(f"    [{channel}] найдено {matched} медиа")
            except Exception as e:
                print(f"  [{channel}] ошибка парсинга: {e}", file=sys.stderr)

        if not all_media_urls:
            print(f"  [{slug}] медиа не найдено (keywords={kw_strict})")
            continue

        for idx, url in enumerate(all_media_urls, 1):
            try:
                ext = url.split('?')[0].split('.')[-1][:4]
                if ext not in ('jpg', 'jpeg', 'png', 'gif', 'mp4', 'webp'):
                    ext = 'jpg'
                filename = os.path.join(media_dir, f"{slug}_{idx}.{ext}")
                download_media_file(url, filename)
                saved_files.append(filename)
                print(f"  Сохранено: {filename}")
            except Exception as e:
                print(f"  [!] не удалось скачать: {e}", file=sys.stderr)

    return saved_files


def _convert_to_telegram_html(text):
    """Конвертирует [Q]...[/Q] в <blockquote> и [L=URL]...[/L] в <a href>, экранирует остальной HTML."""
    import html as _html

    # Шаг 1: Заменяем [L=URL]Name[/L] на плейсхолдер до экранирования
    links = []
    def _replace_link(m):
        url = m.group(1)
        name = m.group(2)
        placeholder = f"\x00LINK{len(links)}\x00"
        links.append(f'<a href="{url}">{_html.escape(name)}</a>')
        return placeholder
    text = re.sub(r'\[L=([^\]]+)\](.*?)\[/L\]', _replace_link, text)

    # Убираем маркеры и собираем текст + blockquote
    parts = re.split(r'\[Q\](.*?)\[/Q\]', text, flags=re.DOTALL)
    result = []
    for i, part in enumerate(parts):
        if i % 2 == 0:
            result.append(_html.escape(part))
        else:
            content = _html.escape(part.strip())
            if content:
                # blockquote на отдельной строке
                result.append(f"\n<blockquote>{content}</blockquote>\n")
    final = "".join(result)
    # Шаг 2: Восстанавливаем ссылки из плейсхолдеров
    for i, link_html in enumerate(links):
        final = final.replace(f"\x00LINK{i}\x00", link_html)
    # Убираем лишние пустые строки, оставляем одинарные переносы
    final = re.sub(r'\n{3,}', '\n\n', final)
    return final.strip()


def apply_vai_style(client, enriched_news):
    """Шаг 3: Форматируем новости в стиль @VAI_ART."""

    news_block = ""
    for i, item in enumerate(enriched_news, 1):
        news_block += f"\n{i}. {item['name']}\n"
        if item.get('url'):
            news_block += f"   URL: {item['url']}\n"
        news_block += f"   КОНТЕКСТ: {item['what']}"
        if item.get('available'):
            news_block += f" | Доступно: {item['available']}"
        if item.get('price'):
            news_block += f" | Цена: {item['price']}"
        news_block += "\n"
        features = item.get('features', '')
        web = item.get('web_details', '')
        if features or web:
            news_block += f"   ФИЧИ: {features}"
            if web:
                news_block += f" | Из интернета: {web}"
            news_block += "\n"

    prompt = f"""Ты — автор Telegram-канала @VAI_ART. CG-специалист с 15 годами опыта. Тон: свой парень, который в теме. Без пафоса.

Новости:
{news_block}

ВСТУПЛЕНИЕ (одна строка):
- Насыщенная неделя: "Рубрика самых интересных новостей в ИИ за неделю. Все по плану. Погнали!"
- Нейтральная: "Не меняя традиции. Пробежимся по новостям за неделю."
- Взрывная (>7): "Ох. Происходит очень много всего и везде. Быстро пробежимся по самому интересному."
- Спокойная (<4): "Немного ленивая неделя. На следующей побольше будет всего."

КАЖДАЯ НОВОСТЬ — ТРИ БЛОКА:

Блок 1: 🔹 Название — суть одной фразой

Блок 2: Общее описание — одно предложение. О чём новость В ЦЕЛОМ, без конкретных фич и деталей. Просто введение в контекст: что за продукт и что с ним произошло.

Блок 3: [Q]...[/Q] — конкретика и детали. Здесь ВМЕСТО блока 2 раскрываешь подробности: что именно умеет, цифры, платформы, цены, отличия. Каждый пункт — развёрнутая фраза, не голый термин.

ПРИМЕР ПРАВИЛЬНОГО РАЗДЕЛЕНИЯ:

🔹 Kling 2.0 — апдейт генерации видео
Вышла новая версия модели для генерации видео от Kuaishou.
[Q]
— генерирует ролики до 30 секунд в FHD-разрешении
— появился motion control для управления движением камеры и объектов
— доступна в Weavy AI за 10 кредитов за генерацию
[/Q]

ПРИМЕР НЕПРАВИЛЬНОГО (блоки дублируются):

🔹 Kling 2.0 — генерация видео до 30 секунд в FHD
Доступна в Weavy AI за 10 кредитов. Поддерживает motion control.
[Q]
— до 30 секунд видео (УЖЕ В ЗАГОЛОВКЕ)
— доступна в Weavy AI (УЖЕ В ОПИСАНИИ)
— motion control (УЖЕ В ОПИСАНИИ)
[/Q]

ПРАВИЛА:
- Блок 2 — общо. Блок 3 — конкретно. Никаких пересечений
- В [Q]: фразы простым языком. Плохо: "KV-кэши". Хорошо: "передаёт кэш между серверами — меньше задержка"
- Количество пунктов в [Q]: сколько есть реальных деталей. Может быть 1, может 5
- Нет деталей — не пиши [Q]...[/Q] вообще
- Не выдумывай то, чего нет в данных
- Никаких иероглифов и текста не на русском
- Только 🔹, никаких других эмодзи
- Нет HTML-тегов — только текст, [Q]...[/Q] и [L=URL]...[/L]
- Если у новости есть URL — оборачивай название в заголовке: 🔹 [L=URL]Название[/L] — суть. Если URL нет — просто 🔹 Название — суть
- Не упоминай TG-каналы
- Без воды: "это шаг вперёд", "открывает возможности", "может принести успех" — удалять
- Лимит 4096 символов

В конце:
@VAI_ART
#VAI_News

Выведи ТОЛЬКО готовый пост."""

    raw = ask_groq(client, prompt)
    return _convert_to_telegram_html(raw)


def main():
    if not GROQ_API_KEY:
        print("ERROR: GROQ_API_KEY не задан", file=sys.stderr)
        sys.exit(1)
    if not TG_TOKEN or not TG_CHAT_ID:
        print("ERROR: TG_TOKEN или TG_CHAT_ID не заданы", file=sys.stderr)
        sys.exit(1)

    client = Groq(api_key=GROQ_API_KEY)

    # === Шаг 1: Загружаем каналы ===
    all_html = []
    for ch in CHANNELS:
        html = fetch_channel(ch)
        if html:
            all_html.append(f"=== Канал: {ch} ===\n{html[:2500]}")
            print(f"  ✅ {ch}: {len(html)} символов загружено")
        else:
            print(f"  ⚠️  {ch}: не удалось загрузить")

    if not all_html:
        msg = "⚠️ AI Digest: не удалось загрузить ни один Telegram-канал"
        try:
            send_telegram(msg)
        except Exception:
            pass
        print("ERROR: нет данных", file=sys.stderr)
        sys.exit(1)

    channels_content = "\n\n".join(all_html)

    try:
        # === Шаг 2: Отбираем новости (JSON) ===
        print("Отбираю новости через Groq...")
        news_items = extract_news(client, channels_content)
        print(f"Отобрано новостей: {len(news_items)}")

        # === Шаг 2б: Скачиваем медиа для отобранных новостей ===
        print("Скачиваю медиа для новостей...")
        media_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '..', 'Digest_Media', datetime.now().strftime('%Y-%m-%d')
        )
        downloaded_media = download_news_media(news_items, media_dir)
        print(f"Медиа скачано: {len(downloaded_media)} файлов")

        # === Шаг 3: Обогащаем из интернета только если нужно ===
        print("Проверяю где нужен поиск...")
        for item in news_items:
            if item.get("needs_search", False):
                query = item.get("search_query", item["name"])
                details = search_product_details(query)
                item["web_details"] = details
                print(f"  🔍 {item['name']}: поиск → {'найдено' if details else 'нет данных'}")
                time.sleep(1)
            else:
                item["web_details"] = ""
                print(f"  ✅ {item['name']}: достаточно данных из поста")

        # === Шаг 4: Стилизация @VAI_ART ===
        print("Применяю стиль @VAI_ART...")
        final_post = apply_vai_style(client, news_items)
        print(f"Пост готов: {len(final_post)} символов")

        # === Шаг 5: Генерируем обложку ===
        print("Генерирую обложку...")
        cover_path = generate_cover()

        # === Шаг 6: Отправляем обложку + текст в Telegram ===
        send_telegram_photo(cover_path)
        print("Обложка отправлена")
        ok = send_telegram(final_post)
        print("OK" if ok else "FAILED — сообщение не отправлено")

    except Exception as e:
        error_msg = f"⚠️ AI Digest: ошибка при генерации\n{str(e)[:300]}"
        try:
            send_telegram(error_msg)
        except Exception:
            pass
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
