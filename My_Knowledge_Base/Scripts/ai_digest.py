#!/usr/bin/env python3
"""
Еженедельный AI-дайджест для @VAI_ART.
Пайплайн: TG-каналы → отбор новостей (Gemini) → стилизация @VAI_ART (Gemini) → Telegram.
Использование: python ai_digest.py
"""
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta

import google.generativeai as genai

# === НАСТРОЙКИ ===
CHANNELS = ["neyr0graph", "cgevent", "data_secrets"]

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
TG_TOKEN = os.environ.get("TG_TOKEN", "")
TG_CHAT_ID = os.environ.get("TG_CHAT_ID", "")


def fetch_channel(channel):
    url = f"https://t.me/s/{channel}"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; bot)"}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.read().decode("utf-8", errors="replace")
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


def ask_gemini(prompt):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text.strip()


def extract_news(channels_content):
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
- Где доступно и сколько стоит (если есть)
- 3-5 конкретных особенностей: цифры, сравнения, факты

Формат — просто нумерованный список с деталями. Это промежуточный результат, финальное форматирование будет отдельно."""

    return ask_gemini(prompt)


def apply_vai_style(news_list):
    """Шаг 2: Переформатируем список новостей в стиль @VAI_ART."""
    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)

    prompt = f"""Переформатируй этот список AI-новостей в стиль Telegram-канала @VAI_ART.

СПИСОК НОВОСТЕЙ:
{news_list}

---

ПРАВИЛА СТИЛЯ @VAI_ART:

Автор — CG-специалист с 15 годами опыта. Пишет для своей аудитории напрямую, без пафоса. Тон: "свой парень, который в теме". Аудитория знает терминологию — разжёвывать не нужно.

ШАГ 1 — ВСТУПЛЕНИЕ (выбери одно по контексту):
- Если неделя насыщена: "Рубрика самых интересных новостей в ИИ за неделю. Все по плану. Погнали!"
- Если нейтральная: "Не меняя традиции. Пробежимся по новостям за неделю."
- Если взрывная (больше 8 новостей): "Ох. Происходит очень много всего и везде. Быстро пробежимся по самому интересному."
- Если спокойная (меньше 5 новостей): "Немного ленивая неделя. На следующей побольше будет всего."

ШАГ 2 — СПИСОК НОВОСТЕЙ:
Каждый пункт:
🔹 [Название модели или продукта] — [что вышло и чем примечательно, 1-2 предложения]

Правила пунктов:
- Начинай с сути — что именно вышло, что изменилось
- Если есть конкретная цифра (цена, длина видео, скорость) — добавь
- Можно короткую личную ноту: "выглядит очень круто", "интересная штука", "стоит попробовать" — органично, не в каждом пункте
- Нет bold-текста, нет подзаголовков, нет вложенных списков
- Между пунктами — пустая строка

ШАГ 3 — ЗАКРЫТИЕ:
@VAI_ART
#VAI_News

ЧТО НЕ ДЕЛАТЬ:
- Не использовать шапку "ИИ-дайджест | дата"
- Не использовать жирный текст внутри пунктов
- Не делать подзаголовки между пунктами
- Не использовать маркетинговые фразы: "революционный", "инновационный", "прорывной"
- Только 🔹 в пунктах, никаких других эмодзи

ЛИМИТ: не более 4096 символов. Если превышает — сокращай описания, начиная с менее важных. Лучше 6 хороших пунктов, чем 10 обрезанных.

Выведи только готовый пост, без пояснений."""

    return ask_gemini(prompt)


def main():
    if not GEMINI_API_KEY:
        print("ERROR: GEMINI_API_KEY не задан", file=sys.stderr)
        sys.exit(1)
    if not TG_TOKEN or not TG_CHAT_ID:
        print("ERROR: TG_TOKEN или TG_CHAT_ID не заданы", file=sys.stderr)
        sys.exit(1)

    genai.configure(api_key=GEMINI_API_KEY)

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
        print("Отбираю новости через Gemini...")
        news_list = extract_news(channels_content)
        print(f"Новости отобраны: {len(news_list)} символов")

        # === Шаг 3: Стилизация @VAI_ART ===
        print("Применяю стиль @VAI_ART...")
        final_post = apply_vai_style(news_list)
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
