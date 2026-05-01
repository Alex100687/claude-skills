---
name: tg-ai-digest
description: Создаёт еженедельный дайджест продуктовых AI-новостей из Telegram-каналов, генерирует обложку и отправляет в Telegram. Использовать когда пользователь просит сделать дайджест, выпуск или подборку AI-новостей за неделю, собрать посты из телеграм-каналов. Форматирует готовый пост в пределах 4096 символов.
---

# TG AI Digest — полный пайплайн

Собирает дайджест из Telegram-каналов, оформляет в стиле @VAI_ART, генерирует обложку и отправляет в Telegram.

**Порядок шагов критичен.** Медиа качаем ТОЛЬКО после утверждения списка пользователем — иначе тратим время на новости, которые могут быть заменены.

---

## Шаг 1: Сбор постов из каналов

Загрузи параллельно через WebFetch все каналы: `https://t.me/s/<channel_name>`

**Каналы по умолчанию:**
- `neyr0graph` — AI-видеогенерация, инструменты
- `cgevent` — AI CG, роботика, модели
- `data_secrets` — AI-политика, модели, корпоративные события
- `TochkiNadAI` — AI-инструменты, обновления
- `tips_ai` — AI-тулзы, новости
- `seeallochnaya` — AI-аналитика
- `AcidCrunch` — AI-видео, генерация
- `data_analysis_ml` — ML-инструменты, модели

Из каждого канала извлеки посты за последние **7 дней**.

**При сборе фиксируй для каждого поста:**
- Дату поста (важно для фильтрации свежих)
- Текст поста
- Все внешние URL из текста (ссылки на продукты, сайты, GitHub)

---

## Шаг 2: Проверить прошлый дайджест — исключить повторы

Перед отбором новостей посмотри, что уже было в предыдущем выпуске:

```bash
ls My_Knowledge_Base/Digest_Media/ | tail -3
ls My_Knowledge_Base/Digest_Media/<последняя_дата>/
```

Имена файлов = slug-и новостей из прошлого дайджеста. **Любую новость с таким же продуктом/моделью исключай**, даже если канал её снова упомянул на этой неделе. Аудитория уже видела.

Старые упоминания в постах ≠ свежий релиз. Если канал на этой неделе пересказывает релиз прошлой недели — это НЕ повод включать.

---

## Шаг 3: Отбор до 10 продуктовых новостей

**Что берём:**
1. Запуск новой модели (GPT, Claude, Gemini, Midjourney, Kling, Sora, Flux и др.)
2. Обновление существующей модели — новые возможности, улучшения
3. Запуск нового AI-продукта или инструмента (только реальный релиз, не анонс)
4. Изменение доступности или цен

**Что НЕ берём:**
- Релизы из прошлого дайджеста (см. Шаг 2)
- Корпоративные события, сделки, скандалы
- Исследования без выхода продукта
- Политика, регулирование
- Анонсы без релиза
- Реклама, курсы

Дубли — берём одно лучшее упоминание.

---

## Шаг 4: Оформление в стиле @VAI_ART

Прочитай скилл `.claude/commands/vai-style.md` и применяй его стиль. Дополнительно к стилю VAI — каждая новость включает **3 блока**:

```
🔹 [Название] — [хайлайт одной фразой]
[Общее описание: что произошло, где доступно, цена — 1-2 предложения]
<blockquote>— конкретная фича объяснённая простым языком
— ещё одна фича с объяснением</blockquote>
```

**Ссылки в заголовках:**
Если у новости есть URL из исходного поста — оборачивай название продукта в ссылку:
`🔹 <a href="https://example.com">Название</a> — хайлайт`
Если URL нет — просто текст без ссылки.

**Критичные правила блоков:**
- Блок 2 (описание) и Блок 3 (blockquote) НЕ должны пересекаться по содержанию
- Блок 2 = общее "что случилось" (контекст)
- Блок 3 = конкретные фичи и детали (конкретика)
- В blockquote: каждый пункт — фраза с объяснением, НЕ просто термин
  - Плохо: `— KV-кэши`
  - Хорошо: `— передаёт KV-кэши между серверами — меньше задержка при длинных контекстах`
- Количество пунктов гибкое (не всегда 3). Если нечего писать — пропусти blockquote
- Между пунктами одинарный перенос

**Лимит: 4096 символов.** Лучше 7 хороших пунктов, чем 10 обрезанных.

---

## Шаг 5: Показать пост пользователю и получить утверждение

Если запущен интерактивно:
1. Выведи готовый пост
2. Выведи **«Запасные новости»** — ещё до 10 новостей, которые прошли фильтр продуктовых (Шаг 3), но не вошли в топ. Формат: нумерованный список, каждая — одна строка с кратким описанием. Это нужно чтобы пользователь мог заметить пропущенное и попросить заменить.
3. Спроси подтверждение или замены.
4. **СТОП.** Не качай медиа, не генерируй обложку, не отправляй ничего, пока пользователь явно не подтвердит. Если он попросит замены — обнови пост и спроси снова.

Если запущен в автоматическом режиме (`-p` флаг, headless) — пропусти ожидание и переходи к Шагу 6.

---

## Шаг 6: Скачивание медиа ⚠️ ТОЛЬКО после утверждения

После того как пользователь подтвердил финальный список — записать JSON и запустить `fetch_media.py`.

**Slug** = название новости в lower_snake_case, например `gpt_5_4`, `runway_characters`, `photoshop_rotate`.

**Шаг 6.1** — записать файл `My_Knowledge_Base/Digest_Media/media_selected.json`:

**Правила формирования ключевых слов:**
- `channel` — ОБЯЗАТЕЛЬНО: точное название канала где найден пост (из Шага 1)
- `must_all` — 2-3 слова, которые ТОЧНО есть в тексте поста (скопируй из поста дословно)
- `any_of` — уточняющие слова если must_all слишком общий, иначе `[]`

```python
import json, os
os.makedirs("My_Knowledge_Base/Digest_Media", exist_ok=True)

# ВАЖНО: channel — точное название канала из Шага 1 где найден пост
# must_all — слова из РЕАЛЬНОГО текста поста (не придумывай)
news = [
    {"slug": "название_slug", "channel": "имя_канала", "must_all": ["Слово из поста", "Ещё слово"], "any_of": []},
    # ... по одной записи на новость
]

with open("My_Knowledge_Base/Digest_Media/media_selected.json", "w", encoding="utf-8") as f:
    json.dump(news, f, ensure_ascii=False, indent=2)
print("JSON записан:", len(news), "новостей")
```

**Шаг 6.2** — запустить скрипт (он прочитает JSON и скачает медиа):

```python
import subprocess
result = subprocess.run(
    ["python", "-X", "utf8", "My_Knowledge_Base/Scripts/fetch_media.py"],
    capture_output=True, text=True, encoding="utf-8", timeout=120
)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr[:500])
```

Выведи список сохранённых файлов пользователю.

---

## Шаг 7: Генерация обложки

Запусти скрипт `My_Knowledge_Base/Scripts/cover_gen.py`:

```python
import sys, os
sys.path.insert(0, 'My_Knowledge_Base/Scripts')
import cover_gen
cover_gen.OUTPUT_PATH = os.path.join('My_Knowledge_Base', 'Cover_Elements', 'output', 'cover.png')
os.makedirs(os.path.dirname(cover_gen.OUTPUT_PATH), exist_ok=True)
cover_gen.generate_cover()
```

---

## Шаг 8: Отправка в Telegram

**Реквизиты** берутся из памяти (memory/reference_telegram_bot.md):
- Token: из памяти
- Chat ID: из памяти
- Topic ID: из памяти

**Порядок отправки:**
1. Сначала обложка через `sendPhoto` (с `message_thread_id`)
2. Затем пост через `sendMessage` (с `parse_mode=HTML` и `message_thread_id`)

Для отправки фото использовать multipart/form-data через Python:
```python
import urllib.request, json, uuid

TOKEN = '...'  # из памяти
CHAT = '...'   # из памяти
TOPIC = '...'  # из памяти

# sendPhoto — multipart
boundary = uuid.uuid4().hex
parts = []
for name, val in [('chat_id', CHAT), ('message_thread_id', TOPIC)]:
    parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{val}'.encode())
with open(cover_path, 'rb') as f:
    photo_data = f.read()
parts.append(
    f'--{boundary}\r\nContent-Disposition: form-data; name="photo"; filename="cover.png"\r\nContent-Type: image/png\r\n\r\n'.encode()
    + photo_data
)
body = b'\r\n'.join(parts) + f'\r\n--{boundary}--\r\n'.encode()
req = urllib.request.Request(
    f'https://api.telegram.org/bot{TOKEN}/sendPhoto',
    data=body,
    headers={'Content-Type': f'multipart/form-data; boundary={boundary}'}
)
urllib.request.urlopen(req)

# sendMessage — JSON
payload = json.dumps({
    'chat_id': CHAT,
    'message_thread_id': int(TOPIC),
    'text': post_text,
    'parse_mode': 'HTML'
}).encode('utf-8')
req = urllib.request.Request(
    f'https://api.telegram.org/bot{TOKEN}/sendMessage',
    data=payload,
    headers={'Content-Type': 'application/json'}
)
urllib.request.urlopen(req)
```

---

## Частые ситуации

**Мало новостей**: 5-6 качественных лучше чем добавлять мусор.

**Нет деталей для blockquote**: пропусти blockquote для этого пункта.

**Пост больше 4096 символов**: сокращай блоки 2-3 у менее важных новостей.

**Пользователь просит замены**: обнови пост, покажи снова, дождись ОК. Только потом качай медиа.
