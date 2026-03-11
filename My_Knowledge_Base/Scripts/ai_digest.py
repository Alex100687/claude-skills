#!/usr/bin/env python3
"""
Еженедельный AI-дайджест для @VAI_ART.
Пайплайн: TG-каналы → отбор новостей (Groq) → стилизация @VAI_ART (Groq) → Telegram.
Использование: python ai_digest.py
"""
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone, timedelta
from html.parser import HTMLParser

from groq import Groq

# === НАСТРОЙКИ ===
CHANNELS = ["neyr0graph", "cgevent", "data_secrets"]

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
        # Убираем множественные пробелы и пустые строки
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
        # Извлекаем чистый текст из HTML
        parser = TextExtractor()
        parser.feed(html)
        return parser.get_text()
    except Exception as e:
        print(f"Warning: не удалось загрузить {channel}: {e}", file=sys.stderr)
        return ""


def send_telegram(text):
    payload = json.dumps({
        "chat_id": TG_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }).encode("utf-8")
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read()).get("ok", False)


def ask_groq(client, prompt):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000,
    )
    return response.choices[0].message.content.strip()


def extract_news(client, channels_content):
    """Шаг 1: Отбираем продуктовые новости из HTML каналов."""
    now = datetime.now(timezone.utc)

    prompt = f"""Сегодня {now.strftime('%d.%m.%Y')}.

Вот HTML-страницы публичных Telegram-каналов за последние 7 дней:

{channels_content}

---

Из этих постов отбери до 10 продуктовых AI-новостей.

ЧТО БЕРЁМ:
1. Запуск новой модели — GPT, Claude, Gemini, Midjourney, Sora, Flux, Kling и любые другие AI-модели
2. Обновление существующей модели — новые возможности, улучшение качества, расширение контекста, новые модальности
3. Запуск нового AI-продукта или инструмента — только реальный релиз, не анонс
4. Изменение доступности или цен — стало бесплатным, открытым, дешевле, появилось в новом регионе

ЧТО НЕ БЕРЁМ: корпоративные события, сделки, скандалы, исследования без релиза, политика, регулирование, анонсы без выхода, реклама, курсы авторов каналов.

Если одна модель в нескольких каналах — одно лучшее упоминание.
Если мало продуктовых новостей — 5-6 качественных, не добавляй нерелевантное.

Для каждой новости выведи:
- Название модели/продукта
- Что именно вышло (1 предложение)
- Где доступно и сколько стоит (если есть в постах — цена, платформа, API)
- 3-5 конкретных особенностей: цифры, скорость, качество, сравнения

ВАЖНО: "где доступно" — это платформа продукта (ChatGPT, Midjourney сайт, API, App Store и т.д.),
а НЕ название Telegram-канала откуда взята новость.
Если реальных деталей нет в постах — напиши только то что есть, не придумывай.

Формат — просто нумерованный список с деталями. Это промежуточный результат."""

    return ask_groq(client, prompt)


def apply_vai_style(client, news_list):
    """Шаг 2: Переформатируем список новостей в стиль @VAI_ART."""

    prompt = f"""Переформатируй этот список AI-новостей в стиль Telegram-канала @VAI_ART.

СПИСОК НОВОСТЕЙ:
{news_list}

---

ПРАВИЛА СТИЛЯ @VAI_ART:

Автор — CG-специалист с 15 годами опыта. Пишет для своей аудитории напрямую, без пафоса. Тон: "свой парень, который в теме". Аудитория знает терминологию — разжёвывать не нужно.

ВСТУПЛЕНИЕ (выбери одно по контексту):
- Если неделя насыщена: "Рубрика самых интересных новостей в ИИ за неделю. Все по плану. Погнали!"
- Если нейтральная: "Не меняя традиции. Пробежимся по новостям за неделю."
- Если взрывная (больше 8 новостей): "Ох. Происходит очень много всего и везде. Быстро пробежимся по самому интересному."
- Если спокойная (меньше 5 новостей): "Немного ленивая неделя. На следующей побольше будет всего."

ФОРМАТ КАЖДОГО ПУНКТА (строго):

🔹 [Название] — [хайлайт одной фразой, самое главное]
[Описание: что именно вышло, где доступно, цена — 1-2 предложения]
<blockquote>— особенность 1
— особенность 2
— особенность 3</blockquote>

Между пунктами — пустая строка.

ПРИМЕР:
🔹 GPT-5.4 — три версии флагмана OpenAI, по кодингу новый топ
OpenAI выпустила GPT-5.4 в версиях Standard, Thinking и Pro. Доступна в API и ChatGPT (Plus, Team, Pro).
<blockquote>— контекст до 1 млн токенов в API
— на 33% меньше фактических ошибок чем у GPT-5.2
— Thinking: показывает план рассуждений, можно корректировать на ходу
— нативное управление компьютером из коробки</blockquote>

ПРАВИЛА:
- Начинай хайлайт с сути — что изменилось или почему важно
- В описании: факты, цена, платформа — без воды
- В blockquote: 3-5 пунктов через тире, конкретика и цифры
- Можно добавить короткую личную ноту после blockquote: "выглядит очень круто", "стоит попробовать" — органично, не везде
- Нет жирного текста, нет подзаголовков
- Только 🔹 в заголовках пунктов, никаких других эмодзи
- Не упоминать названия TG-каналов как место доступности
- Не придумывать детали которых нет

ЗАКРЫТИЕ — обязательно в конце, на отдельных строках:
@VAI_ART
#VAI_News

ЛИМИТ: не более 4096 символов. Лучше 6 хороших пунктов, чем 10 обрезанных.

Выведи только готовый пост в HTML-формате для Telegram, без пояснений."""

    return ask_groq(client, prompt)


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
            all_html.append(f"=== Канал: {ch} ===\n{html[:8000]}")
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
        # === Шаг 2: Отбираем новости ===
        print("Отбираю новости через Groq...")
        news_list = extract_news(client, channels_content)
        print(f"Новости отобраны: {len(news_list)} символов")

        # === Шаг 3: Стилизация @VAI_ART ===
        print("Применяю стиль @VAI_ART...")
        final_post = apply_vai_style(client, news_list)
        print(f"Пост готов: {len(final_post)} символов")

        # === Шаг 4: Отправляем в Telegram ===
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
