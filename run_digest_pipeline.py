import sys, os, json, urllib.request, uuid
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# ── Шаг 5: Генерация обложки ──────────────────────────────────────────────
sys.path.insert(0, 'My_Knowledge_Base/Scripts')
import cover_gen
cover_gen.OUTPUT_PATH = os.path.join('My_Knowledge_Base', 'Cover_Elements', 'output', 'cover.png')
os.makedirs(os.path.dirname(cover_gen.OUTPUT_PATH), exist_ok=True)
print("Генерирую обложку...")
cover_gen.generate_cover()
cover_path = cover_gen.OUTPUT_PATH
print(f"Обложка: {cover_path}")

# ── Шаг 6: Отправка в Telegram ────────────────────────────────────────────
TOKEN = '8784420556:AAH-9kjv374fgDcHRX_UwXv4C_m2YBuZ9a4'
CHAT  = '-1003790798162'
TOPIC = '7'

POST_TEXT = """Рубрика самых интересных новостей в ИИ за неделю. Все по плану. Погнали!

🔹 <a href="https://openai.com/index/introducing-gpt-5-4/">GPT-5.4</a> — контекст до 1 миллиона токенов
OpenAI выпустили новую версию, немного дороже предыдущей. Доступна в API и ChatGPT.
<blockquote>— 1M токенов в окне — можно загрузить целую кодовую базу или книгу за раз
— подорожание небольшое, разрыв с конкурентами по контексту закрывает</blockquote>

🔹 <a href="https://claude.com/blog/code-review">Claude Code Review</a> — агент ревьюит PR автоматически
Anthropic запустили сервис ревью кода. Находит баги в 84% пулл-реквестов. Бета для Team/Enterprise, $15–25 за ревью.
<blockquote>— группирует замечания по приоритету, не просто список ошибок
— параллельный запуск, не блокирует разработчика</blockquote>

🔹 <a href="https://dev.runwayml.com/">Runway Characters</a> — встраиваемые AI-аватары с API
Runway выпустили персонажей с кастомным голосом, базой знаний и компьютерным зрением. $10 за 1000 кредитов (~50 мин).
<blockquote>— аватар знает о вашем продукте, отвечает в реальном времени
— встраивается в сайт или приложение через API</blockquote>

🔹 <a href="https://grok.com/">Grok References</a> — до 7 референсов для генерации видео
xAI добавили поддержку нескольких референсных изображений при создании видео. Бесплатно в нативном интерфейсе.
<blockquote>— до 7 картинок-референсов — персонаж держит консистентность по всему видео
— работает и для генерации изображений</blockquote>

🔹 <a href="https://3d.hunyuanglobal.com/studio">Tencent HY 3D Studio</a> — из фото в полноценную 3D-модель
Глобальный запуск: Image→3D с топологией, UV, текстурами, риггингом и анимацией. 20 бесплатных генераций/день.
<blockquote>— полный пайплайн от одной фотки до анимированной модели без ручной работы
— 20 бесплатных для новых пользователей</blockquote>

🔹 Photoshop Beta — вращение 3D-объектов прямо в 2D-сцене
Adobe добавили Rotate Object: крутишь объект в пространстве, Harmonize корректирует освещение. Всё локально, без облака.
<blockquote>— вращаешь до нужного ракурса — AI перегенерирует с правильным светом
— работает на устройстве без отправки в облако</blockquote>

🔹 <a href="https://www.perplexity.ai/ja/hub/blog/everything-is-computer">Perplexity Personal Computer</a> — постоянно работающий AI на Mac mini
Новая система: мультимодальный агент с постоянной активностью и удалённым доступом к файлам.
<blockquote>— живёт на машине, видит файлы, экран, уведомления — контекст не теряется между сессиями
— несколько задач параллельно через мультиагентную архитектуру</blockquote>

🔹 <a href="https://code.claude.com/docs/en/memory">Claude Code Auto Memory</a> — агент сам запоминает проект
В Claude Code появилась автопамять: агент создаёт и обновляет markdown-файлы с контекстом между сессиями.
<blockquote>— больше не нужно каждый раз объяснять проект — агент помнит
— MEMORY.md хранит структурированные заметки о проекте, предпочтениях и фидбэке</blockquote>

@VAI_ART
#VAI_News"""

print(f"\nДлина поста: {len(POST_TEXT)} символов")

# sendPhoto
print("\nОтправляю обложку...")
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
with urllib.request.urlopen(req) as r:
    resp = json.loads(r.read())
    if resp.get('ok'):
        print("Обложка отправлена OK")
    else:
        print(f"Ошибка sendPhoto: {resp}")

# sendMessage
print("Отправляю текст дайджеста...")
payload = json.dumps({
    'chat_id': CHAT,
    'message_thread_id': int(TOPIC),
    'text': POST_TEXT,
    'parse_mode': 'HTML',
    'disable_web_page_preview': True
}).encode('utf-8')
req = urllib.request.Request(
    f'https://api.telegram.org/bot{TOKEN}/sendMessage',
    data=payload,
    headers={'Content-Type': 'application/json'}
)
with urllib.request.urlopen(req) as r:
    resp = json.loads(r.read())
    if resp.get('ok'):
        print("Дайджест отправлен OK!")
        print(f"Message ID: {resp['result']['message_id']}")
    else:
        print(f"Ошибка sendMessage: {resp}")
