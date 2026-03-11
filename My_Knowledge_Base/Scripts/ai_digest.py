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


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip = True

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

    try:
        return _post({"chat_id": TG_CHAT_ID, "text": text, "parse_mode": "HTML"})
    except urllib.error.HTTPError as e:
        if e.code == 400:
            plain = re.sub(r"<[^>]+>", "", text)
            return _post({"chat_id": TG_CHAT_ID, "text": plain})
        raise


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

Из этих постов отбери до 8 продуктовых AI-новостей.

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
    "needs_search": true,
    "search_query": "Поисковый запрос на английском"
  }}
]

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


def _convert_to_telegram_html(text):
    """Конвертирует [Q]...[/Q] в <blockquote>, экранирует весь остальной HTML."""
    import html as _html
    parts = re.split(r'\[Q\](.*?)\[/Q\]', text, flags=re.DOTALL)
    result = []
    for i, part in enumerate(parts):
        if i % 2 == 0:
            result.append(_html.escape(part))
        else:
            content = _html.escape(part.strip())
            if content:
                result.append(f"<blockquote>{content}</blockquote>")
    final = "".join(result)
    # Одинарный перенос между пунктами, без пустых строк
    final = re.sub(r'\n{2,}', '\n', final)
    return final.strip()


def apply_vai_style(client, enriched_news):
    """Шаг 3: Форматируем новости в стиль @VAI_ART."""

    news_block = ""
    for i, item in enumerate(enriched_news, 1):
        news_block += f"\n{i}. {item['name']}\n"
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

    prompt = f"""Ты — автор Telegram-канала @VAI_ART. CG-специалист с 15 годами опыта. Пишешь для своей аудитории напрямую, без пафоса. Тон: свой парень, который в теме.

Переформатируй эти AI-новости в пост для канала:

{news_block}

ФОРМАТ ПОСТА:

Вступление (одна строка, выбери по контексту):
- Если неделя насыщена: "Рубрика самых интересных новостей в ИИ за неделю. Все по плану. Погнали!"
- Если нейтральная: "Не меняя традиции. Пробежимся по новостям за неделю."
- Если взрывная (>7): "Ох. Происходит очень много всего и везде. Быстро пробежимся по самому интересному."
- Если спокойная (<4): "Немного ленивая неделя. На следующей побольше будет всего."

Каждая новость — три блока:

БЛОК 1 (заголовок):
🔹 Название — суть одной фразой

БЛОК 2 (описание, 1-2 предложения):
Бери ТОЛЬКО из строки КОНТЕКСТ. Что вышло, где доступно, цена. Никаких фич тут. Никакой воды и оценочных суждений типа "это шаг вперёд", "теперь она более функциональна", "новый подход может принести успех". Только сухой факт.

БЛОК 3 (цитата [Q]...[/Q]):
Бери ТОЛЬКО из строки ФИЧИ. Каждый пункт — фраза простым языком, объясняющая что продукт умеет.
ПЛОХО: "— KV-кэши" (голый термин, ничего не понятно)
ХОРОШО: "— передаёт кэш между серверами, что уменьшает задержку при длинных контекстах"
ПЛОХО: "— без деплоя" (если это уже сказано в описании)
ХОРОШО: пропустить этот пункт, взять другую фичу

Количество пунктов в [Q] — сколько есть реальных фич. Может быть 1, может 5. НЕ подгоняй до 3.
Если строки ФИЧИ нет или она пустая — НЕ пиши блок [Q]...[/Q] вообще.

МЕЖДУ БЛОКОМ 2 И БЛОКОМ 3 НЕТ ПУСТОЙ СТРОКИ. Между новостями — одна пустая строка.

В конце поста:
@VAI_ART
#VAI_News

ЗАПРЕТЫ:
- Не дублировать информацию между блоками 2 и 3
- Не добавлять HTML-теги — только текст и [Q]...[/Q]
- Не использовать эмодзи кроме 🔹
- Не упоминать названия TG-каналов
- Не использовать текст с иероглифами или на других языках кроме русского
- Не выдумывать фичи которых нет в данных
- Не писать водянистые оценки ("это интересно", "может принести успех", "открывает новые возможности")
- Не более 4096 символов — лучше 6 хороших пунктов, чем 10 обрезанных

Выведи ТОЛЬКО готовый пост. Без пояснений, без комментариев."""

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

        # === Шаг 5: Отправляем в Telegram ===
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
