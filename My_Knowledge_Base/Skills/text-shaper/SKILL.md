---
name: text-shaper
description: Use when user wants to scaffold a gesture-driven text instrument — a single-page web tool where wrist roll + finger pinch (MediaPipe HandLandmarker) drive AI-rewriting of a text canvas via OpenRouter, with word-level diff highlighting. Triggers on text-shaper, шейпер текста, поворот кисти текст, hand-gesture text rewrite, embodied text instrument, biometric text, gesture text, text shaper, текст по жесту.
---

# скил про текст шейка
# text-shaper · gesture-driven text instrument

Один экран. Большая textarea чёрным по белому. Сверху — кнопки с seed-текстами. Внизу — два настраиваемых жеста (ROLL и PINCH) и камера 220×156 со скелетом руки. Когда рука стабильна, текст переписывается через OpenRouter. Изменённые слова инвертируются и плавно растворяются.

Минимализм геометричный, B&W. Этюд в линии style-graph (референс — сессия с Ксенией Ивановой).

Live reference (если есть доступ): https://style-graph-aimindset.netlify.app/shaper/

---

## ⛔ ШАГ 0 — INTERVIEW (до того, как создавать файлы)

Когда юзер запускает этот скил, **сначала задай ему вопросы по контексту** в этом порядке. По одному вопросу за раз. Не начинай файлы до полного интервью.

### Q1 — для какого домена?

> Опиши домен: что за тексты обычно проходят через это? (личный блог, product copy, манифесто, код-комментарии, поэзия, чат-сообщения, маркетинговая копия, заметки в Obsidian, что-то другое)
>
> Это нужно, чтобы подобрать seed-тексты, которые соответствуют твоему голосу. Без этого получится generic-демо.

Сохрани ответ как `{{domain}}`.

### Q2 — голос автора

> Опиши свой голос или voice-style бренда в одном-двух предложениях. Например: «прямо, без хеджей, иногда с матом, технические термины разрешены», или «лирично, личное, метафоры».

Сохрани как `{{voice}}`.

### Q3 — 5 seed-текстов

> Дай 5 коротких (60–150 слов) текстов, **сильно отличающихся по стилю**. Это будут пресеты-кнопки сверху инструмента. Хорошая палитра контрастов:
>
> 1. **Базовый** — твой обычный голос
> 2. **Жёсткий/манифесто** — декларативно, без воды
> 3. **Гонзо/raw** — энергично, пожалуй с матом если он у тебя в палитре (см. Хантер С. Томпсон)
> 4. **Мягкий/сказочный** — лирично, длинные предложения, метафоры
> 5. **Сухой/академический** — определения, термины, строгая структура
>
> Можешь дать свои или попросить меня сгенерировать на основе `{{domain}}` и `{{voice}}`.

Сохрани как `{{seed_texts}}` — массив из 5 объектов `{key, label, text}`.

### Q4 — параметры в configurator

> Дефолтный набор параметров для двух жестов: `tonality`, `length`, `formality`, `register`, `rhythm`, `imagery`. Если для твоего домена нужно что-то специфическое — назови. Например, для код-ревью могло бы быть `nitpick-level` или для рекламы `urgency`.
>
> Дефолт-маппинг: ROLL → `tonality`, PINCH → `length`. Хочешь поменять?

Сохрани как `{{params}}` (массив объектов с `name`, `minus_label`, `plus_label`, `prompt_minus`, `prompt_plus`) и `{{default_roll}}`, `{{default_pinch}}`.

### Q5 — язык интерфейса и контента

> RU / EN / mixed? Это влияет на placeholder-тексты и системные промпты к LLM.

Сохрани как `{{ui_lang}}`.

### Q6 — деплой

> Куда деплоим?
>
> - **A**: новый Netlify-сайт (нужен netlify CLI + аккаунт)
> - **B**: sub-route на существующий сайт (нужен path и доступ к его netlify.toml)
> - **C**: только локально через `netlify dev` (нужен только OpenRouter ключ)
> - **D**: статический хостинг + отдельный proxy для OpenRouter (опиши свой)

Сохрани как `{{deploy}}`.

### Q7 — OpenRouter ключ

> У тебя уже есть ключ OpenRouter (sk-or-v1-...)? Если да, где он лежит (`.env` файл, env var, manager)?
>
> Если нет — создай на https://openrouter.ai → settings → keys. Затем подскажу как положить в Netlify env (если деплой A/B) или в локальный `.env` (если C).

Сохрани как `{{openrouter_key_location}}`.

### Q8 — модель

> Дефолт — `meta-llama/llama-3.3-70b-instruct` через OpenRouter с `provider.order = ['Cerebras', 'SambaNova', 'Groq']` (быстрые провайдеры). Fallback — `anthropic/claude-haiku-4.5`.
>
> Если твой контент часто содержит мат/raw — Llama 3.3 НЕ добавляет мат, если его нет в исходнике. Альтернативы: `nousresearch/hermes-3-llama-3.1-405b` (uncensored), `gryphe/mythomax-l2-13b` (creative).
>
> Какие модели использовать?

Сохрани как `{{primary_model}}`, `{{fallback_model}}`, `{{provider_order}}`.

### Q9 — палитра

> Дефолт: чистый B&W (`#fff` фон, `#000` текст, JetBrains Mono). Геометрично и минималистично.
>
> Если твой бренд требует другую палитру — назови HEX и шрифт. Тогда я переключу tokens, но **советую держать B&W первой версией** — это часть концепта инструмента-этюда (контраст с teal-grid стилем других tools).

Сохрани как `{{palette}}` (объект с `bg`, `ink`, `muted`, `font`).

### Q10 — название и брендинг

> Как назвать инструмент в хедере? Дефолт — `SHAPER`. Хочешь свой бренд?
>
> URL слаг (имя папки) тоже укажи. Дефолт — `/shaper/`.

Сохрани как `{{brand}}`, `{{slug}}`.

---

После всех 10 ответов — переходи к шагу 1.

---

## ШАГ 1 — структура проекта

Создай эту структуру в директории, выбранной на Q6:

```
{{project_root}}/
├── {{slug}}/
│   ├── index.html        ← основной файл UI (1100+ LOC, см. ШАГ 2)
│   └── README.md         ← документация (ШАГ 5)
├── netlify/
│   └── functions/
│       └── text-shape.mjs ← OpenRouter proxy (ШАГ 3)
└── netlify.toml           ← конфиг (ШАГ 4)
```

Если деплой B (sub-route) — `index.html` идёт в `{{existing_site_path}}/{{slug}}/`, а `text-shape.mjs` — в `{{existing_site_path}}/netlify/functions/`. `netlify.toml` правится in-place (см. ШАГ 4).

Если деплой C (локально) — структура такая же, но `netlify.toml` опциональный, можно запустить `netlify dev` из корня проекта.

---

## ШАГ 2 — `{{slug}}/index.html`

Single-file UI. Заменяй `{{плейсхолдеры}}` на собранный контекст. Полный код:

```html
<!doctype html>
<html lang="{{ui_lang}}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{brand}} · gesture-driven text instrument</title>
<meta name="description" content="Минималистичный B&W инструмент. Поворот кисти и щип пальцев меняют параметры текста. Live-rewrite через OpenRouter. Diff-подсветка изменений.">
<style>
  :root {
    --bg: {{palette.bg}};        /* default #ffffff */
    --ink: {{palette.ink}};      /* default #000000 */
    --soft: #d9d9d9;
    --hair: #ececec;
    --muted: {{palette.muted}};  /* default #8a8a8a */
    --gutter: 22px;
    --frame: 1px;
    --mono: "{{palette.font}}", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  }

  * { box-sizing: border-box; }

  html, body {
    margin: 0;
    padding: 0;
    height: 100%;
    background: var(--bg);
    color: var(--ink);
    font-family: var(--mono);
    font-size: 14px;
    line-height: 1.55;
    font-weight: 400;
    -webkit-font-smoothing: antialiased;
    overflow: hidden;
  }

  body {
    display: grid;
    grid-template-rows: auto auto 1fr auto;
    height: 100vh;
    padding: var(--gutter);
    gap: 14px;
  }

  /* ─── header ─── */
  header {
    display: grid;
    grid-template-columns: auto 1fr auto;
    align-items: baseline;
    gap: 24px;
    border-bottom: var(--frame) solid var(--ink);
    padding-bottom: 12px;
    text-transform: lowercase;
    letter-spacing: 0.04em;
  }
  header .brand { font-weight: 600; letter-spacing: 0.12em; }
  header .crumb { color: var(--muted); font-size: 12px; }
  header .right {
    color: var(--muted);
    font-size: 12px;
    justify-self: end;
    display: flex;
    gap: 14px;
    align-items: center;
  }
  header .right .dot {
    width: 8px; height: 8px;
    border: 1px solid var(--ink);
    border-radius: 50%;
    background: var(--bg);
    transition: background 0.18s linear;
  }
  header .right.live .dot { background: var(--ink); }
  header .right .state { min-width: 110px; text-align: right; }

  /* ─── seeds row ─── */
  .seeds {
    display: flex;
    gap: 6px;
    align-items: center;
    overflow-x: auto;
    padding-bottom: 2px;
    scrollbar-width: none;
  }
  .seeds::-webkit-scrollbar { display: none; }
  .seeds .label {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--muted);
    margin-right: 6px;
    white-space: nowrap;
  }
  .seeds button {
    background: var(--bg);
    color: var(--ink);
    border: var(--frame) solid var(--ink);
    padding: 6px 12px;
    font-family: var(--mono);
    font-size: 12px;
    letter-spacing: 0.04em;
    cursor: pointer;
    transition: background 0.12s, color 0.12s;
    white-space: nowrap;
  }
  .seeds button:hover { background: var(--hair); }
  .seeds button.active { background: var(--ink); color: var(--bg); }

  /* ─── main stage ─── */
  main {
    display: grid;
    grid-template-rows: 1fr;
    overflow: hidden;
    border: var(--frame) solid var(--ink);
    position: relative;
  }

  #text {
    width: 100%;
    height: 100%;
    padding: 28px 36px;
    border: none;
    outline: none;
    background: transparent;
    color: var(--ink);
    font-family: var(--mono);
    font-size: 16px;
    line-height: 1.7;
    overflow-y: auto;
    white-space: pre-wrap;
    word-wrap: break-word;
    transition: opacity 0.22s ease;
    caret-color: var(--ink);
  }
  #text:empty::before {
    content: 'click a seed above or type your own…';
    color: var(--muted);
  }
  #text.thinking { opacity: 0.55; }
  #text.morphing { opacity: 0.20; }

  /* diff highlights — inverted, fade over 4s */
  .diff-new {
    background: var(--ink);
    color: var(--bg);
    padding: 0 3px;
    margin: 0 -1px;
    border-radius: 1px;
    transition: background 1.2s ease-out, color 1.2s ease-out;
  }
  .diff-new.faded {
    background: transparent;
    color: var(--ink);
  }

  main .corner {
    position: absolute;
    top: 12px; right: 16px;
    font-size: 10px;
    color: var(--muted);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    pointer-events: none;
    background: var(--bg);
    padding: 0 4px;
  }
  main .corner.live::before {
    content: "•";
    margin-right: 5px;
    color: var(--ink);
    animation: pulse 1.2s ease-in-out infinite;
  }
  @keyframes pulse {
    0%,100% { opacity: 0.3; }
    50% { opacity: 1; }
  }

  /* ─── footer / controls + cam ─── */
  footer {
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 28px;
    align-items: stretch;
    padding-top: 12px;
    border-top: var(--frame) solid var(--ink);
  }

  .controls {
    display: grid;
    grid-template-rows: 1fr 1fr;
    gap: 10px;
  }

  .ctrl-row {
    display: grid;
    grid-template-columns: 220px 1fr;
    gap: 18px;
    align-items: center;
  }

  .ctrl-assign {
    display: flex;
    align-items: center;
    gap: 8px;
    border: var(--frame) solid var(--ink);
    padding: 6px 10px;
    background: var(--bg);
  }
  .ctrl-assign .gesture {
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--ink);
    font-weight: 600;
    min-width: 44px;
  }
  .ctrl-assign select {
    flex: 1;
    border: none;
    outline: none;
    background: transparent;
    font-family: var(--mono);
    font-size: 12px;
    color: var(--ink);
    cursor: pointer;
    padding: 0;
    -webkit-appearance: none;
    appearance: none;
    text-overflow: ellipsis;
  }
  .ctrl-assign .arrow { color: var(--muted); font-size: 10px; }
  .ctrl-assign.off { opacity: 0.4; }

  .ctrl-scale {
    display: grid;
    grid-template-rows: auto auto auto;
    gap: 6px;
    user-select: none;
  }
  .ctrl-scale .legend {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    font-size: 10px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--muted);
  }
  .ctrl-scale .legend > :nth-child(1) { text-align: left; }
  .ctrl-scale .legend > :nth-child(2) { text-align: center; }
  .ctrl-scale .legend > :nth-child(3) { text-align: right; }

  .ctrl-scale .track {
    position: relative;
    height: 10px;
    border-top: var(--frame) solid var(--ink);
  }
  .ctrl-scale .track .mid {
    position: absolute;
    top: -7px; left: 50%;
    width: 1px; height: 14px;
    background: var(--ink);
  }
  .ctrl-scale .track .lo, .ctrl-scale .track .hi {
    position: absolute;
    top: -4px;
    width: 1px; height: 8px;
    background: var(--ink);
    opacity: 0.5;
  }
  .ctrl-scale .track .lo { left: 0; }
  .ctrl-scale .track .hi { right: 0; }
  .ctrl-scale .track .dot {
    position: absolute;
    top: -8px; left: 50%;
    width: 10px; height: 10px;
    border-radius: 50%;
    background: var(--ink);
    transform: translate(-50%, 0);
    transition: left 0.10s linear;
    box-shadow: 0 0 0 3px var(--bg);
  }
  .ctrl-scale .track .dot.idle { background: var(--bg); border: 1px solid var(--ink); }

  .ctrl-scale .label {
    font-size: 11px;
    letter-spacing: 0.04em;
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    color: var(--muted);
  }
  .ctrl-scale .label .name { font-weight: 600; color: var(--ink); }

  /* ─── camera preview ─── */
  .cam {
    width: 220px;
    align-self: end;
    height: 156px;
    position: relative;
    border: var(--frame) solid var(--ink);
    overflow: hidden;
    background: var(--bg);
  }
  .cam video { display: none; }
  .cam canvas {
    width: 100%; height: 100%;
    display: block;
  }
  .cam .label {
    position: absolute;
    top: 5px; left: 7px;
    font-size: 9px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--ink);
    background: var(--bg);
    padding: 2px 5px;
    border: 1px solid var(--ink);
  }
  .cam .pinch-hud {
    position: absolute;
    bottom: 5px; right: 7px;
    font-size: 9px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--ink);
    background: var(--bg);
    padding: 2px 5px;
    border: 1px solid var(--ink);
    pointer-events: none;
  }
  .cam .hint {
    position: absolute;
    inset: 0;
    display: grid;
    place-items: center;
    text-align: center;
    color: var(--muted);
    font-size: 11px;
    padding: 16px;
    background: var(--bg);
    cursor: pointer;
    line-height: 1.5;
  }
  .cam.ready .hint { display: none; }
  .cam .hint b { display: block; color: var(--ink); margin-bottom: 6px; font-size: 12px; }

  /* ─── overlay states ─── */
  .toast {
    position: fixed;
    bottom: 14px; left: 50%;
    transform: translateX(-50%);
    background: var(--ink);
    color: var(--bg);
    padding: 10px 18px;
    font-size: 12px;
    letter-spacing: 0.04em;
    text-transform: lowercase;
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.2s ease;
    z-index: 50;
  }
  .toast.show { opacity: 1; }

  /* responsive */
  @media (max-width: 820px) {
    body { padding: 14px; gap: 10px; }
    #text { font-size: 14px; padding: 18px; }
    .cam { width: 130px; height: 92px; }
    footer { grid-template-columns: 1fr; gap: 12px; }
    .ctrl-row { grid-template-columns: 1fr; gap: 6px; }
    .ctrl-assign { width: 100%; }
  }
</style>
</head>
<body>

<header>
  <div class="brand">{{brand}}</div>
  <div class="crumb">gesture text instrument</div>
  <div class="right" id="status-row">
    <span class="state" id="ai-state">idle</span>
    <span class="dot" id="ai-dot"></span>
  </div>
</header>

<div class="seeds" id="seeds-row">
  <span class="label">seeds</span>
  <!-- buttons injected by JS from SEEDS const -->
</div>

<main>
  <div id="text" contenteditable="true" spellcheck="false"></div>
  <div class="corner" id="live-mark">live</div>
</main>

<footer>
  <div class="controls">
    <div class="ctrl-row">
      <div class="ctrl-assign" id="assign-roll">
        <span class="gesture">ROLL</span>
        <select id="param-roll" aria-label="parameter for wrist roll"></select>
        <span class="arrow">▾</span>
      </div>
      <div class="ctrl-scale">
        <div class="legend" id="legend-roll"><span>−</span><span>·</span><span>+</span></div>
        <div class="track">
          <span class="lo"></span><span class="mid"></span><span class="hi"></span>
          <span class="dot idle" id="dot-roll"></span>
        </div>
        <div class="label">
          <span class="name" id="name-roll">наклони кисть</span>
          <span id="val-roll">0.00</span>
        </div>
      </div>
    </div>
    <div class="ctrl-row">
      <div class="ctrl-assign" id="assign-pinch">
        <span class="gesture">PINCH</span>
        <select id="param-pinch" aria-label="parameter for pinch"></select>
        <span class="arrow">▾</span>
      </div>
      <div class="ctrl-scale">
        <div class="legend" id="legend-pinch"><span>−</span><span>·</span><span>+</span></div>
        <div class="track">
          <span class="lo"></span><span class="mid"></span><span class="hi"></span>
          <span class="dot idle" id="dot-pinch"></span>
        </div>
        <div class="label">
          <span class="name" id="name-pinch">щип / раскрытие</span>
          <span id="val-pinch">0.00</span>
        </div>
      </div>
    </div>
  </div>

  <div class="cam" id="cam-frame">
    <span class="label">camera</span>
    <span class="pinch-hud" id="pinch-hud" style="display:none">pinch —</span>
    <video id="video" playsinline autoplay muted></video>
    <canvas id="cam-canvas" width="440" height="312"></canvas>
    <div class="hint" id="cam-hint">
      <div>
        <b>включи камеру</b>
        кисть в кадре · поворот + щип
      </div>
    </div>
  </div>
</footer>

<div class="toast" id="toast"></div>

<script type="module">
/* ═════════════════════════════════════════════════
   SEEDS — replace with {{seed_texts}} from interview Q3
   ═════════════════════════════════════════════════ */

const SEEDS = {
  // EXAMPLE seeds — replace these with answers from Q3
  base: {
    label: '{{seed_texts[0].label}}',
    text: `{{seed_texts[0].text}}`
  },
  hard: {
    label: '{{seed_texts[1].label}}',
    text: `{{seed_texts[1].text}}`
  },
  raw: {
    label: '{{seed_texts[2].label}}',
    text: `{{seed_texts[2].text}}`
  },
  soft: {
    label: '{{seed_texts[3].label}}',
    text: `{{seed_texts[3].text}}`
  },
  dry: {
    label: '{{seed_texts[4].label}}',
    text: `{{seed_texts[4].text}}`
  },
};

/* ═════════════════════════════════════════════════
   PARAMS — replace with {{params}} from interview Q4
   Each param has: client-side label trio (neg/mid/pos)
   ═════════════════════════════════════════════════ */

const PARAM_OPTIONS = [
  { value: 'tonality',  label: 'tonality · sharp ↔ soft' },
  { value: 'length',    label: 'length · compact ↔ expand' },
  { value: 'formality', label: 'formality · casual ↔ formal' },
  { value: 'register',  label: 'register · vernacular ↔ literary' },
  { value: 'rhythm',    label: 'rhythm · staccato ↔ legato' },
  { value: 'imagery',   label: 'imagery · literal ↔ lyrical' },
  { value: 'off',       label: '— off —' },
];

const PARAM_LABELS = {
  tonality:  { neg: 'острее',     mid: 'нейтрально', pos: 'мягче'    },
  length:    { neg: 'короче',     mid: 'как есть',   pos: 'длиннее'  },
  formality: { neg: 'casual',     mid: 'нейтрально', pos: 'formal'   },
  register:  { neg: 'street',     mid: 'нейтрально', pos: 'literary' },
  rhythm:    { neg: 'staccato',   mid: 'как есть',   pos: 'legato'   },
  imagery:   { neg: 'literal',    mid: 'как есть',   pos: 'lyrical'  },
  off:       { neg: '—',          mid: '—',          pos: '—'        },
};

/* ═════════════════════════════════════════════════
   REFS / STATE
   ═════════════════════════════════════════════════ */

const refs = {
  seedsRow: document.getElementById('seeds-row'),
  textEl: document.getElementById('text'),
  aiState: document.getElementById('ai-state'),
  statusRow: document.getElementById('status-row'),
  liveMark: document.getElementById('live-mark'),
  paramRoll: document.getElementById('param-roll'),
  paramPinch: document.getElementById('param-pinch'),
  assignRoll: document.getElementById('assign-roll'),
  assignPinch: document.getElementById('assign-pinch'),
  legendRoll: document.getElementById('legend-roll'),
  legendPinch: document.getElementById('legend-pinch'),
  dotRoll: document.getElementById('dot-roll'),
  dotPinch: document.getElementById('dot-pinch'),
  nameRoll: document.getElementById('name-roll'),
  namePinch: document.getElementById('name-pinch'),
  valRoll: document.getElementById('val-roll'),
  valPinch: document.getElementById('val-pinch'),
  camFrame: document.getElementById('cam-frame'),
  camHint: document.getElementById('cam-hint'),
  video: document.getElementById('video'),
  camCanvas: document.getElementById('cam-canvas'),
  pinchHud: document.getElementById('pinch-hud'),
  toast: document.getElementById('toast'),
};

const ctx = refs.camCanvas.getContext('2d');

const app = {
  ai: { pending: false, lastSent: null, lastSentAt: 0, inflight: null },
  hand: {
    landmarker: null, ready: false, loading: false, present: false,
    landmarks: null,
    rollRaw: 0, rollSmooth: 0,
    pinchRaw: 0, pinchSmooth: 0,
    lastChangeAt: 0,
  },
  axes: {
    roll:  { param: localStorage.getItem('shaper.axis.roll')  || '{{default_roll}}'  /* e.g. tonality */ },
    pinch: { param: localStorage.getItem('shaper.axis.pinch') || '{{default_pinch}}' /* e.g. length */ },
  },
  user: { typingUntil: 0 },
  cfg: {
    smoothAlpha: 0.20,
    rollChangeThreshold: 0.04,
    pinchChangeThreshold: 0.04,
    stillMs: 380,
    minIntervalMs: 1500,
    minAxisDelta: 0.10,
    typingPauseMs: 1500,
    diffFadeMs: 4500,
  },
};

/* ═════════════════════════════════════════════════
   UI helpers
   ═════════════════════════════════════════════════ */

function setAiState(s, live = false) {
  refs.aiState.textContent = s;
  refs.statusRow.classList.toggle('live', live);
}
function setLiveMark(on) { refs.liveMark.classList.toggle('live', on); }
function toast(msg, ms = 1800) {
  refs.toast.textContent = msg;
  refs.toast.classList.add('show');
  clearTimeout(toast._t);
  toast._t = setTimeout(() => refs.toast.classList.remove('show'), ms);
}
function escapeHtml(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

/* ═════════════════════════════════════════════════
   SEEDS UI
   ═════════════════════════════════════════════════ */

function renderSeeds() {
  for (const [key, seed] of Object.entries(SEEDS)) {
    const btn = document.createElement('button');
    btn.dataset.seed = key;
    btn.textContent = seed.label;
    btn.addEventListener('click', () => loadSeed(key));
    refs.seedsRow.appendChild(btn);
  }
}

function loadSeed(key) {
  const seed = SEEDS[key];
  if (!seed) return;
  refs.textEl.textContent = seed.text;
  app.ai.lastSent = null;
  refs.seedsRow.querySelectorAll('button').forEach(b => {
    b.classList.toggle('active', b.dataset.seed === key);
  });
  setAiState('seed loaded', app.hand.ready);
}

/* ═════════════════════════════════════════════════
   PARAM SELECTORS (configurator)
   ═════════════════════════════════════════════════ */

function populateSelect(selEl, currentValue) {
  for (const opt of PARAM_OPTIONS) {
    const o = document.createElement('option');
    o.value = opt.value;
    o.textContent = opt.label;
    if (opt.value === currentValue) o.selected = true;
    selEl.appendChild(o);
  }
}
function syncLegend(legendEl, param) {
  const lab = PARAM_LABELS[param] || PARAM_LABELS.off;
  legendEl.children[0].textContent = lab.neg;
  legendEl.children[1].textContent = lab.mid;
  legendEl.children[2].textContent = lab.pos;
}
function setupParams() {
  populateSelect(refs.paramRoll, app.axes.roll.param);
  populateSelect(refs.paramPinch, app.axes.pinch.param);
  syncLegend(refs.legendRoll, app.axes.roll.param);
  syncLegend(refs.legendPinch, app.axes.pinch.param);
  refs.assignRoll.classList.toggle('off', app.axes.roll.param === 'off');
  refs.assignPinch.classList.toggle('off', app.axes.pinch.param === 'off');

  refs.paramRoll.addEventListener('change', () => {
    app.axes.roll.param = refs.paramRoll.value;
    localStorage.setItem('shaper.axis.roll', refs.paramRoll.value);
    syncLegend(refs.legendRoll, app.axes.roll.param);
    refs.assignRoll.classList.toggle('off', app.axes.roll.param === 'off');
    app.ai.lastSent = null;
  });
  refs.paramPinch.addEventListener('change', () => {
    app.axes.pinch.param = refs.paramPinch.value;
    localStorage.setItem('shaper.axis.pinch', refs.paramPinch.value);
    syncLegend(refs.legendPinch, app.axes.pinch.param);
    refs.assignPinch.classList.toggle('off', app.axes.pinch.param === 'off');
    app.ai.lastSent = null;
  });
}

function updateScales() {
  const tRoll  = app.hand.present ? app.hand.rollSmooth  : 0;
  const tPinch = app.hand.present ? app.hand.pinchSmooth : 0;

  refs.dotRoll.style.left  = `${(tRoll + 1) * 50}%`;
  refs.dotPinch.style.left = `${(tPinch + 1) * 50}%`;
  refs.dotRoll.classList.toggle('idle',  !app.hand.present);
  refs.dotPinch.classList.toggle('idle', !app.hand.present);

  refs.valRoll.textContent  = tRoll.toFixed(2);
  refs.valPinch.textContent = tPinch.toFixed(2);

  const labRoll  = PARAM_LABELS[app.axes.roll.param]  || PARAM_LABELS.off;
  const labPinch = PARAM_LABELS[app.axes.pinch.param] || PARAM_LABELS.off;
  refs.nameRoll.textContent  = pickLabel(tRoll,  labRoll,  'наклони кисть');
  refs.namePinch.textContent = pickLabel(tPinch, labPinch, 'щип / раскрытие');
}
function pickLabel(v, lab, fallback) {
  if (!app.hand.present) return fallback;
  if (Math.abs(v) < 0.10) return lab.mid;
  return v < 0 ? lab.neg : lab.pos;
}

/* ═════════════════════════════════════════════════
   CAMERA + MEDIAPIPE HandLandmarker
   ═════════════════════════════════════════════════ */

async function startCamera() {
  if (app.hand.loading || app.hand.ready) return;
  app.hand.loading = true;
  refs.camHint.querySelector('b').textContent = 'загружаю модель…';

  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: false,
      video: { facingMode: 'user', width: { ideal: 640 }, height: { ideal: 480 } },
    });
    refs.video.srcObject = stream;
    await refs.video.play();
  } catch (e) {
    console.warn('[shaper] camera denied', e);
    refs.camHint.querySelector('b').textContent = 'нет доступа к камере';
    refs.camHint.querySelector('div').lastChild.textContent =
      'разреши камеру в настройках браузера и обнови страницу';
    app.hand.loading = false;
    return;
  }

  try {
    const vision = await import('https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.18/vision_bundle.mjs');
    const fileset = await vision.FilesetResolver.forVisionTasks(
      'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.18/wasm'
    );
    app.hand.landmarker = await vision.HandLandmarker.createFromOptions(fileset, {
      baseOptions: {
        modelAssetPath: 'https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task',
        delegate: 'GPU',
      },
      runningMode: 'VIDEO',
      numHands: 1,
      minHandDetectionConfidence: 0.5,
      minTrackingConfidence: 0.5,
    });
    app.hand.ready = true;
    refs.camFrame.classList.add('ready');
    refs.pinchHud.style.display = '';
    setAiState('ready', true);
    setLiveMark(true);
  } catch (e) {
    console.error('[shaper] mediapipe load failed', e);
    refs.camHint.querySelector('b').textContent = 'не удалось загрузить mediapipe';
    refs.camHint.querySelector('div').lastChild.textContent = 'проверь подключение и обнови страницу';
  } finally {
    app.hand.loading = false;
  }
}

refs.camHint.addEventListener('click', startCamera);

const CONNECTIONS = [
  [0,1],[1,2],[2,3],[3,4],
  [0,5],[5,6],[6,7],[7,8],
  [5,9],[9,10],[10,11],[11,12],
  [9,13],[13,14],[14,15],[15,16],
  [13,17],[17,18],[18,19],[19,20],[0,17],
];

const dist = (a, b) => Math.hypot(a.x - b.x, a.y - b.y);

/* ═════════════════════════════════════════════════
   HAND PROCESSING
   ROLL  = palm-vector tilt from vertical (atan2-based)
   PINCH = thumb-tip ↔ index-tip / hand-span
   ═════════════════════════════════════════════════ */

function onHandResult(result) {
  const hands = result.landmarks || [];
  if (!hands.length) {
    app.hand.present = false;
    app.hand.landmarks = null;
    return;
  }
  app.hand.present = true;
  const lm = hands[0];
  app.hand.landmarks = lm;

  // ROLL — palm-vector angle relative to vertical
  const wrist = lm[0];
  const palm  = lm[9];                    // middle finger MCP
  const dx = wrist.x - palm.x;            // mirrored: +x = user's right
  const dy = palm.y - wrist.y;
  const angle = Math.atan2(dx, -dy);      // 0 = up, +π/2 = user's right
  const roll = Math.max(-1, Math.min(1, angle / (Math.PI / 3))); // ±60° = ±1

  // PINCH — thumb tip (4) ↔ index tip (8), normalized by hand span
  const span    = dist(wrist, lm[12]);    // wrist → middle finger tip
  const pinchD  = dist(lm[4], lm[8]);
  const ratio   = span > 0 ? pinchD / span : 0;
  const pinchN  = (ratio - 0.05) / 0.50;  // closed≈0.05, open≈0.55
  const pinch   = Math.max(-1, Math.min(1, pinchN * 2 - 1)); // -1 closed, +1 open

  if (Math.abs(roll - app.hand.rollRaw)   > app.cfg.rollChangeThreshold)  app.hand.lastChangeAt = performance.now();
  if (Math.abs(pinch - app.hand.pinchRaw) > app.cfg.pinchChangeThreshold) app.hand.lastChangeAt = performance.now();

  app.hand.rollRaw   = roll;
  app.hand.pinchRaw  = pinch;
  app.hand.rollSmooth  += (roll  - app.hand.rollSmooth)  * app.cfg.smoothAlpha;
  app.hand.pinchSmooth += (pinch - app.hand.pinchSmooth) * app.cfg.smoothAlpha;

  const pinchPct = Math.round((app.hand.pinchSmooth + 1) * 50);
  refs.pinchHud.textContent = `pinch ${pinchPct}%`;
}

function drawCam() {
  const W = refs.camCanvas.width;
  const H = refs.camCanvas.height;
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(0, 0, W, H);

  if (!app.hand.landmarks) {
    if (app.hand.ready) {
      ctx.fillStyle = '#999999';
      ctx.font = '11px monospace';
      ctx.textAlign = 'center';
      ctx.fillText('покажи кисть', W / 2, H / 2);
    }
    return;
  }

  const lm = app.hand.landmarks;
  const px = (p) => (1 - p.x) * W;       // mirror x for selfie display
  const py = (p) => p.y * H;

  ctx.strokeStyle = '#000000';
  ctx.lineWidth = 1.4;
  ctx.lineCap = 'round';
  ctx.beginPath();
  for (const [a, b] of CONNECTIONS) {
    ctx.moveTo(px(lm[a]), py(lm[a]));
    ctx.lineTo(px(lm[b]), py(lm[b]));
  }
  ctx.stroke();

  ctx.fillStyle = '#000000';
  for (let i = 0; i < lm.length; i++) {
    const r = (i === 0 || i === 9) ? 4 : 2;
    ctx.beginPath();
    ctx.arc(px(lm[i]), py(lm[i]), r, 0, Math.PI * 2);
    ctx.fill();
  }

  // emphasize palm-vector (the "needle")
  ctx.lineWidth = 2.6;
  ctx.beginPath();
  ctx.moveTo(px(lm[0]), py(lm[0]));
  ctx.lineTo(px(lm[9]), py(lm[9]));
  ctx.stroke();

  // emphasize pinch line (thumb-index)
  ctx.lineWidth = 2.4;
  ctx.beginPath();
  ctx.moveTo(px(lm[4]), py(lm[4]));
  ctx.lineTo(px(lm[8]), py(lm[8]));
  ctx.stroke();
}

/* ═════════════════════════════════════════════════
   MAIN LOOP
   ═════════════════════════════════════════════════ */

function loop() {
  if (app.hand.ready && refs.video.readyState >= 2) {
    try {
      const result = app.hand.landmarker.detectForVideo(refs.video, performance.now());
      onHandResult(result);
    } catch (_) {}
  }
  drawCam();
  updateScales();
  maybeRequestShape();
  requestAnimationFrame(loop);
}
requestAnimationFrame(loop);

/* ═════════════════════════════════════════════════
   AI request loop
   ═════════════════════════════════════════════════ */

function activeAxes() {
  const out = [];
  if (app.axes.roll.param  !== 'off') out.push({ name: app.axes.roll.param,  value: app.hand.rollSmooth  });
  if (app.axes.pinch.param !== 'off') out.push({ name: app.axes.pinch.param, value: app.hand.pinchSmooth });
  return out;
}

function maybeRequestShape() {
  if (!app.hand.ready)            return;
  if (app.ai.pending)             return;
  if (!app.hand.present)          return;
  if (Date.now() < app.user.typingUntil) return;
  if (performance.now() - app.hand.lastChangeAt < app.cfg.stillMs) return;
  if (Date.now() - app.ai.lastSentAt < app.cfg.minIntervalMs) return;

  const axes = activeAxes();
  if (axes.length === 0) return;

  const text = currentPlainText().trim();
  if (!text) return;

  if (app.ai.lastSent) {
    let movedEnough = false;
    for (const a of axes) {
      const prev = app.ai.lastSent.axes.find(x => x.name === a.name);
      if (!prev || Math.abs(a.value - prev.value) >= app.cfg.minAxisDelta) {
        movedEnough = true; break;
      }
    }
    if (!movedEnough && app.ai.lastSent.text === text) return;
  }
  fireShape(text, axes);
}

async function fireShape(text, axes) {
  app.ai.pending = true;
  app.ai.lastSentAt = Date.now();
  app.ai.lastSent = { axes: axes.map(a => ({ ...a })), text };
  refs.textEl.classList.add('thinking');
  setAiState('shaping…', true);
  refs.liveMark.textContent = 'shaping';

  const ctrl = new AbortController();
  app.ai.inflight = ctrl;
  const tmo = setTimeout(() => ctrl.abort(), 16000);

  try {
    const resp = await fetch('/.netlify/functions/text-shape', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ text, axes }),
      signal: ctrl.signal,
    });
    const data = await resp.json().catch(() => ({}));
    if (!resp.ok) {
      const msg = data.error || `${resp.status}`;
      console.warn('[shaper] shape error:', msg);
      if (msg.toLowerCase().includes('openrouter_api_key')) {
        toast('сервер: ключ openrouter не настроен');
      } else {
        toast(`сбой: ${msg}`);
      }
      setAiState('error', false);
      return;
    }
    if (data.text && data.text.trim() !== text) {
      if (Date.now() < app.user.typingUntil) {
        toast('пропустил — ты редактируешь');
      } else {
        applyShape(text, data.text);
        setAiState(`${data.source || 'ok'}`, true);
      }
    } else {
      setAiState('no change', true);
    }
  } catch (e) {
    if (e.name === 'AbortError') setAiState('timeout', false);
    else { console.warn('[shaper] fetch failed', e); setAiState('offline', false); }
  } finally {
    clearTimeout(tmo);
    app.ai.pending = false;
    app.ai.inflight = null;
    refs.textEl.classList.remove('thinking');
    refs.liveMark.textContent = 'live';
  }
}

/* ═════════════════════════════════════════════════
   DIFF (word-level LCS) — inverted span on changes
   ═════════════════════════════════════════════════ */

function tokenize(text) {
  return text.split(/(\s+|[.,!?;:—–"«»()\[\]])/).filter(t => t !== '');
}

function diffWords(oldText, newText) {
  const oldT = tokenize(oldText);
  const newT = tokenize(newText);
  if (oldT.length > 600 || newT.length > 600) {
    return newT.map(t => ({ token: t, changed: !/^\s+$/.test(t) }));
  }
  const m = oldT.length, n = newT.length;
  const dp = new Uint16Array((m + 1) * (n + 1));
  const W = n + 1;
  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      if (oldT[i - 1] === newT[j - 1]) {
        dp[i * W + j] = dp[(i - 1) * W + (j - 1)] + 1;
      } else {
        const a = dp[(i - 1) * W + j];
        const b = dp[i * W + (j - 1)];
        dp[i * W + j] = a > b ? a : b;
      }
    }
  }
  const inLcs = new Array(n).fill(false);
  let i = m, j = n;
  while (i > 0 && j > 0) {
    if (oldT[i - 1] === newT[j - 1]) { inLcs[j - 1] = true; i--; j--; }
    else if (dp[(i - 1) * W + j] >= dp[i * W + (j - 1)]) i--;
    else j--;
  }
  return newT.map((t, k) => ({ token: t, changed: !inLcs[k] && !/^\s+$/.test(t) }));
}

function renderDiffHTML(diff) {
  let out = '';
  for (const { token, changed } of diff) {
    if (token.includes('\n')) { out += token.replace(/\n/g, '<br>'); continue; }
    if (changed) out += `<span class="diff-new">${escapeHtml(token)}</span>`;
    else out += escapeHtml(token);
  }
  return out;
}

function applyShape(oldText, newText) {
  const diff = diffWords(oldText, newText);
  refs.textEl.classList.add('morphing');
  setTimeout(() => {
    if (Date.now() < app.user.typingUntil) {
      refs.textEl.classList.remove('morphing');
      return;
    }
    refs.textEl.innerHTML = renderDiffHTML(diff);
    refs.textEl.classList.remove('morphing');
    setTimeout(() => {
      refs.textEl.querySelectorAll('.diff-new').forEach(el => el.classList.add('faded'));
    }, 80);
    setTimeout(() => {
      const plain = currentPlainText();
      setPlainText(plain);
    }, app.cfg.diffFadeMs);
  }, 220);
}

/* ═════════════════════════════════════════════════
   text get/set (preserves line breaks)
   ═════════════════════════════════════════════════ */

function currentPlainText() { return refs.textEl.innerText || ''; }
function setPlainText(s) {
  refs.textEl.textContent = '';
  s.split('\n').forEach((line, i) => {
    if (i > 0) refs.textEl.appendChild(document.createElement('br'));
    refs.textEl.appendChild(document.createTextNode(line));
  });
}

/* ═════════════════════════════════════════════════
   user typing — abort in-flight
   ═════════════════════════════════════════════════ */

refs.textEl.addEventListener('input', () => {
  app.user.typingUntil = Date.now() + app.cfg.typingPauseMs;
  if (app.ai.inflight) app.ai.inflight.abort();
});
refs.textEl.addEventListener('focus', () => { app.user.typingUntil = Date.now() + 600; });
refs.textEl.addEventListener('paste', (e) => {
  e.preventDefault();
  const t = (e.clipboardData || window.clipboardData).getData('text');
  document.execCommand('insertText', false, t);
});

/* ═════════════════════════════════════════════════
   INIT
   ═════════════════════════════════════════════════ */

renderSeeds();
setupParams();
loadSeed(Object.keys(SEEDS)[0]);
updateScales();
setAiState('click to start', false);

let autoPrompted = false;
window.addEventListener('pointerdown', () => {
  if (!autoPrompted && !app.hand.ready && !app.hand.loading) {
    autoPrompted = true;
    startCamera();
  }
});

</script>
</body>
</html>
```

**Важно при подстановке плейсхолдеров:**
- `{{seed_texts}}` — замени блок `const SEEDS = { ... }` на 5 объектов из ответа Q3. Ключи объекта могут быть любые (base/hard/raw/soft/dry — это шаблон). Тексты экранируй для template-literal: backslash перед `` ` `` и `${`.
- `{{params}}` — если юзер добавляет custom параметры, обнови оба массива (`PARAM_OPTIONS` и `PARAM_LABELS`) И серверную функцию (`PARAMS` объект в text-shape.mjs, см. ШАГ 3).
- `{{default_roll}}`, `{{default_pinch}}` — ставь имя дефолтного параметра, например `'tonality'` и `'length'`.
- `{{palette.bg}}`, `{{palette.ink}}`, `{{palette.muted}}`, `{{palette.font}}` — дефолты `#ffffff`, `#000000`, `#8a8a8a`, `JetBrains Mono`.
- `{{brand}}` — например `SHAPER`.
- `{{ui_lang}}` — `ru` или `en`.

---

## ШАГ 3 — `netlify/functions/text-shape.mjs`

OpenRouter proxy. Принимает `{text, axes}`, возвращает `{text, model, source}`. Этот файл универсален — править нужно только массив `PARAMS` (если юзер добавил custom параметры в Q4) и primary/fallback модели (Q8).

```javascript
const JSON_HEADERS = {
  'Content-Type': 'application/json; charset=utf-8',
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
  'Cache-Control': 'no-store',
};

function jsonResponse(body, status = 200) {
  return new Response(JSON.stringify(body), { status, headers: JSON_HEADERS });
}

/**
 * PARAMS — declarative registry. Each parameter has anchor descriptions
 * for what -1 (minus) and +1 (plus) directions mean.
 *
 * To add a custom parameter from interview Q4: drop a new entry here AND
 * mirror it in client-side PARAM_OPTIONS / PARAM_LABELS in index.html.
 */
const PARAMS = {
  tonality: {
    minus: 'sharper, declarative, drop hedges and softeners',
    zero: 'unchanged tonality',
    plus: 'softer, warmer, more conversational and flowing',
  },
  length: {
    minus: 'compact, trim by ~30% (or more at extreme), remove non-essential phrases',
    zero: 'preserve length ±10%',
    plus: 'expanded by ~30% (or more at extreme), allow connective tissue and elaboration',
  },
  formality: {
    minus: 'casual, conversational, slang allowed',
    zero: 'preserve register',
    plus: 'formal, academic, precise terminology',
  },
  register: {
    minus: 'vernacular, street, raw, profanity preserved/intensified if present',
    zero: 'preserve register',
    plus: 'literary, elevated, refined diction',
  },
  rhythm: {
    minus: 'staccato — short sentences, hard stops, punchy',
    zero: 'preserve rhythm',
    plus: 'legato — flowing, periodic sentences, soft transitions',
  },
  imagery: {
    minus: 'literal, concrete nouns, no metaphor',
    zero: 'preserve imagery level',
    plus: 'metaphorical, sensory, lyrical, allow figurative language',
  },
  // ADD CUSTOM PARAMS FROM INTERVIEW Q4 HERE
};

function buildDirectives(axes) {
  const lines = [];
  for (const a of axes) {
    if (!a || !a.name || a.name === 'off') continue;
    const param = PARAMS[a.name];
    if (!param) continue;
    const v = Math.max(-1, Math.min(1, Number(a.value) || 0));
    if (Math.abs(v) < 0.10) continue;
    const direction = v < 0 ? param.minus : param.plus;
    const magnitude = Math.abs(v).toFixed(2);
    lines.push(`- ${a.name.toUpperCase()} ${v >= 0 ? '+' : ''}${v.toFixed(2)} → ${direction} (intensity ${magnitude})`);
  }
  return lines;
}

function tonalityFallback(t) {
  return [{ name: 'tonality', value: t }];
}

const SYSTEM_PROMPT = [
  'You are a real-time text shaper. Apply the requested style adjustments to the user text.',
  '',
  'Each adjustment is on a -1.0..+1.0 axis. Magnitude controls how aggressive the change is.',
  '',
  'Output rules:',
  '- Output ONLY the rewritten text. No preamble, no quotes, no explanation, no metadata.',
  '- Same language as the input.',
  '- Preserve concrete facts, names, numbers, links exactly.',
  '- Preserve original line breaks and paragraph structure.',
  '- If the input contains profanity (mat) and the user did not ask to clean it, KEEP it. Do not sanitize.',
  '- If no axes are listed (all in deadzone), only fix obvious typos and grammar.',
  '- If multiple axes are active, blend them naturally — do not just stack changes.',
].join('\n');

async function callOpenRouter({ apiKey, model, provider, messages, temperature, maxTokens, signal }) {
  const body = { model, messages, temperature, max_tokens: maxTokens };
  if (provider) body.provider = provider;
  const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
    method: 'POST',
    signal,
    headers: {
      Authorization: `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
      'HTTP-Referer': '{{deploy_url}}',
      'X-OpenRouter-Title': '{{brand}} text shaper',
    },
    body: JSON.stringify(body),
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const errMsg = data?.error?.message || `openrouter ${response.status}`;
    const err = new Error(errMsg);
    err.status = response.status;
    err.data = data;
    throw err;
  }
  const content = data?.choices?.[0]?.message?.content;
  if (typeof content !== 'string' || !content.trim()) {
    throw new Error('empty completion');
  }
  return { text: content.trim(), model: data.model || model };
}

export default async (req) => {
  if (req.method === 'OPTIONS') return new Response(null, { status: 204, headers: JSON_HEADERS });
  if (req.method !== 'POST')    return jsonResponse({ error: 'method not allowed' }, 405);

  let payload;
  try { payload = await req.json(); }
  catch { return jsonResponse({ error: 'invalid json body' }, 400); }

  const text = (payload.text || '').toString().slice(0, 4000);
  if (!text.trim()) return jsonResponse({ text: '', source: 'noop' });

  let axes = Array.isArray(payload.axes) ? payload.axes : [];
  if (axes.length === 0 && Number.isFinite(Number(payload.tonality))) {
    axes = tonalityFallback(payload.tonality);
  }

  const directives = buildDirectives(axes);

  const apiKey = process.env.OPENROUTER_API_KEY || process.env.OPENROUTER_KEY || '';
  if (!apiKey) {
    return jsonResponse({ error: 'OPENROUTER_API_KEY missing on server', text, source: 'passthrough' }, 503);
  }

  const userMsg = directives.length
    ? `Style adjustments to apply:\n${directives.join('\n')}\n\nText:\n${text}`
    : `No active style adjustments (all axes in deadzone). Just fix typos and grammar.\n\nText:\n${text}`;

  const messages = [
    { role: 'system', content: SYSTEM_PROMPT },
    { role: 'user', content: userMsg },
  ];

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 14000);

  try {
    let result;
    try {
      result = await callOpenRouter({
        apiKey,
        model: '{{primary_model}}',  /* default: meta-llama/llama-3.3-70b-instruct */
        provider: { order: {{provider_order}}, allow_fallbacks: true },  /* default: ['Cerebras','SambaNova','Groq'] */
        messages,
        temperature: 0.45,
        maxTokens: 1500,
        signal: controller.signal,
      });
      result.source = 'primary';
    } catch (primaryErr) {
      console.warn('[text-shape] primary failed, falling back:', primaryErr.message);
      result = await callOpenRouter({
        apiKey,
        model: '{{fallback_model}}', /* default: anthropic/claude-haiku-4.5 */
        messages,
        temperature: 0.45,
        maxTokens: 1500,
        signal: controller.signal,
      });
      result.source = 'fallback';
    }
    return jsonResponse({
      text: result.text,
      model: result.model,
      axes,
      directives,
      source: result.source,
    });
  } catch (err) {
    console.error('[text-shape] all providers failed', err);
    return jsonResponse({ error: err.message || 'shape failed', text, source: 'passthrough' }, 502);
  } finally {
    clearTimeout(timeoutId);
  }
};

export const config = {
  path: '/.netlify/functions/text-shape',
};
```

---

## ШАГ 4 — `netlify.toml`

Если деплой A (новый сайт) — создай файл на корне:

```toml
[build]
  publish = "."
  functions = "netlify/functions"

[[headers]]
  for = "/*"
  [headers.values]
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"
    Permissions-Policy = "camera=(), microphone=(), geolocation=()"

[[headers]]
  for = "/{{slug}}/*"
  [headers.values]
    X-Frame-Options = "ALLOWALL"
    Cache-Control = "public, max-age=300"
    Permissions-Policy = "camera=(self), microphone=(), geolocation=()"

[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/:splat"
  status = 200
```

Если деплой B (sub-route на существующий сайт) — добавь в текущий `netlify.toml`:

```toml
[[headers]]
  for = "/{{slug}}/*"
  [headers.values]
    X-Frame-Options = "ALLOWALL"
    Cache-Control = "public, max-age=300"
    Permissions-Policy = "camera=(self), microphone=(), geolocation=()"

[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/:splat"
  status = 200
```

⛔ Не добавляй редирект `/{{slug}}` → `/{{slug}}/` с `force=true` — Netlify сам обрабатывает trailing slash, а `force=true` создаёт redirect-loop.

---

## ШАГ 5 — `{{slug}}/README.md`

Положи краткий README в папку, чтобы проект был самодокументируемым. Шаблон:

````markdown
# {{brand}} · gesture text instrument

Минималистичный B&W инструмент. ROLL и PINCH кисти меняют параметры текста через OpenRouter.

**Live:** https://{{deploy_url}}/{{slug}}/

## жесты

- **ROLL** — поворот кисти от вертикали (±60° = ±1.0)
- **PINCH** — расстояние thumb-tip ↔ index-tip / hand-span. Закрытый = −1, открытый = +1.

Каждому жесту назначается параметр через configurator (dropdown). Дефолты: ROLL→`{{default_roll}}`, PINCH→`{{default_pinch}}`.

## триггеры запроса

Сервер вызывается, когда:
1. Рука в кадре
2. Стабильна (Δsignal < 0.04) ≥ 380ms
3. Хотя бы один axis изменился на ≥0.10
4. ≥1500ms с прошлого запроса
5. Юзер не печатает (>1500ms)

## endpoint

```
POST /api/text-shape
{ "text": "...", "axes": [{ "name": "tonality", "value": -0.5 }, ...] }
→
{ "text": "rewritten...", "model": "...", "source": "primary" }
```

## модели

- primary: `{{primary_model}}` через `provider.order={{provider_order}}`
- fallback: `{{fallback_model}}`

API key: `OPENROUTER_API_KEY` в Netlify env (production, scope: functions).

## known limitations

- Llama 3.3 не добавляет мат, если в исходнике его нет
- Pinch + Roll одновременно — поворот кисти искажает проекцию пинча
- Diff highlighting на >600 токенов выключается (LCS дороговат)
````

---

## ШАГ 6 — wiring OpenRouter ключа

### Деплой A или B (Netlify)

```bash
# Из директории {{project_root}}
netlify env:set OPENROUTER_API_KEY "sk-or-v1-..." --context production --scope functions
```

⛔ Quirks:
- Если переменная уже существует и нужно сменить scope/context — сначала `netlify env:unset OPENROUTER_API_KEY`, потом `:set`. Иначе CLI ругается «cannot combine context and scope on existing var».
- `netlify env:set` **печатает полный ключ** в stdout. Если терминальные логи где-то сохраняются — маскируй через `sed` или передавай через временную переменную.

### Деплой C (локально)

Создай `.env` в корне:

```
OPENROUTER_API_KEY=sk-or-v1-...
```

Запуск:

```bash
netlify dev   # serves at http://localhost:8888 with functions live
```

### Проверка ключа

```bash
curl -sS -X POST "https://openrouter.ai/api/v1/chat/completions" \
  -H "Authorization: Bearer sk-or-v1-..." \
  -H "Content-Type: application/json" \
  -d '{"model":"meta-llama/llama-3.3-70b-instruct","messages":[{"role":"user","content":"PONG?"}],"max_tokens":5}'
```

Ожидаемое: `{"choices":[{"message":{"content":"PONG"...}}]}`. Если `{"error":"User not found"}` — ключ протух или revoked, создай новый на openrouter.ai.

---

## ШАГ 7 — DEPLOY

### Деплой A (новый сайт)

```bash
cd {{project_root}}
netlify init       # link to your team, name the site
netlify deploy --prod --dir=.
```

### Деплой B (sub-route)

```bash
cd {{existing_site_path}}
netlify deploy --prod --dir=. --message="add {{slug}} text shaper"
```

### Проверка после deploy

```bash
# 1. Page returns 200
curl -s -o /dev/null -w "%{http_code}\n" "https://{{deploy_url}}/{{slug}}/"

# 2. Camera permission header present
curl -sI "https://{{deploy_url}}/{{slug}}/" | grep -i permissions-policy
# expected: permissions-policy: camera=(self), ...

# 3. Function works
curl -sS -X POST "https://{{deploy_url}}/api/text-shape" \
  -H "Content-Type: application/json" \
  -d '{"text":"AI Mindset — это рабочая система.","axes":[{"name":"tonality","value":-0.7}]}' \
  --max-time 25
# expected: { "text": "<rewritten>", "model": "...", "source": "primary" }
```

---

## ШАГ 8 — пользовательский гайд

Когда деплой готов, покажи юзеру:

1. **Открыть** https://{{deploy_url}}/{{slug}}/
2. **Кликнуть в любом месте** → разрешить камеру (требование браузера)
3. **Поднять одну руку перед камерой**, ладонью к себе
4. **Поворот кисти как ключа в замке** = ROLL → param из ROLL-dropdown
5. **Сжать/разжать большой+указательный** = PINCH → param из PINCH-dropdown
6. **Когда рука стабильна** ~380ms — текст переписывается, изменения подсвечиваются инверсией
7. **Если печатаешь** — tracking замораживается, активный запрос отменяется
8. **Кнопки seeds сверху** — переключают между пресетами текстов
9. **Dropdown'ы** — назначают любой параметр на любой жест

---

## CUSTOMIZATION KNOBS

### Добавить 6-й параметр (custom для домена)

1. В `index.html` → `PARAM_OPTIONS` массив, добавь:
   ```js
   { value: 'urgency', label: 'urgency · calm ↔ alarming' },
   ```
2. В `index.html` → `PARAM_LABELS` объект, добавь:
   ```js
   urgency: { neg: 'спокойнее', mid: 'нейтрально', pos: 'тревожнее' },
   ```
3. В `text-shape.mjs` → `PARAMS` объект, добавь:
   ```js
   urgency: {
     minus: 'calmer, less time pressure, allow pauses and qualifications',
     zero: 'preserve urgency',
     plus: 'increase time pressure, add deadline language, intensify call-to-action',
   },
   ```

### Добавить 3-й жест (например, открытая ладонь)

В index.html, в `onHandResult`:
```js
// Open hand: average of fingertip-to-wrist distances
const fingerTips = [4, 8, 12, 16, 20];
const avgReach = fingerTips.reduce((s,i) => s + dist(wrist, lm[i]), 0) / fingerTips.length;
const open = Math.max(-1, Math.min(1, (avgReach / span - 0.6) / 0.4));
```

Добавь в state, controls UI, и в activeAxes(). Маппинг к параметру через тот же configurator dropdown.

### Сменить палитру (bg/ink/font)

В `:root` блоке CSS:
```css
:root {
  --bg: #YOUR_BG;
  --ink: #YOUR_INK;
  --font: "YourFont";
}
```

Если делаешь не-B&W, **поменяй также** диff-highlight стиль (сейчас `background: var(--ink)` чтобы инвертировать). На цветной палитре инверсия может выглядеть глючно — попробуй `background: rgba(0,0,0,0.08); border-bottom: 1px solid var(--ink)`.

### Использовать uncensored модель

Замени в `text-shape.mjs`:
```js
model: 'nousresearch/hermes-3-llama-3.1-405b',  // или 'gryphe/mythomax-l2-13b'
```

Llama 3.3 70B — стандартная модель — добавит мат только если он уже есть в исходнике. Hermes / MythoMax менее RLHF'нуты.

### Модель по интенсивности axis

Если нужен Haiku для extreme tones (Llama leak'ает английский в RU при +0.7+):

```js
const totalIntensity = axes.reduce((s, a) => s + Math.abs(a.value), 0);
const useHaiku = totalIntensity > 1.0;
const model = useHaiku ? 'anthropic/claude-haiku-4.5' : '{{primary_model}}';
```

---

## TROUBLESHOOTING

| симптом | причина | фикс |
|---|---|---|
| `/api/text-shape` → 503 `OPENROUTER_API_KEY missing` | ключ не в env | `netlify env:set OPENROUTER_API_KEY ... --context production --scope functions` + redeploy |
| `{"error":"User not found"}` от OpenRouter | ключ revoked | новый ключ на openrouter.ai |
| `/shaper/` redirect loop | force=true редирект на trailing slash | убрать `[[redirects]] from="/shaper" to="/shaper/" force=true` |
| Камера не запускается | not HTTPS | использовать https:// или localhost (file:// не работает) |
| MediaPipe не грузится | CDN заблокирован | проверить cdn.jsdelivr.net и storage.googleapis.com |
| Pinch скачет при повороте | проекция пинча искажается | нормализация на span помогает; для 3D-точности использовать `landmark.z` |
| Diff highlighting не работает на длинных текстах | >600 токенов LCS отключен | поднять лимит в `diffWords` или использовать Myers diff |
| Llama добавляет английские слова | known artifact в RU при +0.7+ | переключиться на Haiku 4.5 при `|tonality|>0.5` (см. customization) |
| Custom domain DNS не резолвится | CNAME pending | использовать `*.netlify.app` URL пока CNAME не пропагнется |
| Llama не добавляет мат | RLHF censoring | использовать Hermes-3 или explicit prompt с `register: -0.7` |

---

## ARCHITECTURE NOTES

### Почему contenteditable, не textarea

`<textarea>` не поддерживает inline-spans. Чтобы подсветить word-level diff после rewrite, нужен `<div contenteditable>`. Цена: spans остаются в DOM пока не очистишь, и при типизации внутри них поведение слегка отличается. Поэтому:
- На `input` стартуем таймер очистки spans
- Через `app.cfg.diffFadeMs` (4500ms) делаем `setPlainText(currentPlainText())` — стрипает все теги, оставляет text+`<br>`

### Почему debounce + still-detection

Hand tracking даёт сигнал на каждом фрейме (~30 fps). Если запрашивать LLM на каждое движение, будет:
1. Лишние costs
2. Нестабильный текст (LLM не успевает закончить — следующий запрос его прервёт)
3. Раздражение от мерцания

Алгоритм:
- `lastChangeAt` обновляется при заметном изменении сигнала
- Запрос разрешён только когда `now - lastChangeAt > stillMs` (380ms)
- Дополнительно: `minIntervalMs` (1500ms) между запросами + `minAxisDelta` (0.10) изменения axis

### Почему provider.order

OpenRouter маршрутизирует к разным backend'ам Llama 3.3 70B. Cerebras / SambaNova / Groq дают **2k+ tok/s** (ответ за 150ms на абзац). Novita / Together / DeepInfra — обычная скорость (~50 tok/s, 2-3s на абзац). Указание `provider.order` склоняет роутинг к быстрым, но `allow_fallbacks: true` оставляет fallback на медленные если быстрые перегружены.

### Почему LCS, не Myers

Word-level LCS — O(n×m) по памяти и времени. Для текстов <600 токенов — мгновенно. Myers diff лучше для длинных текстов, но требует больше кода. Безопасный fallback: при >600 токенов помечаем весь новый текст как changed.

### Почему не stream response

OpenRouter поддерживает SSE streaming. Проще было бы:
1. Открыть EventSource
2. Подменять текст token-by-token
3. После окончания — посчитать diff vs original

Но: client side LCS не работает на partial text, и diff вычисляется только в конце. Стрим даёт «typewriter» feel но усложняет diff на 30-50% LOC. Для v1 batch проще.

---

## PHILOSOPHY

Это **инструмент-этюд**, не production-ready editor. Цель — дать ощутить, что текст можно лепить рукой как глину, что параметры стиля — это не флажки, а continuous spectrum, и что граница между «корректура» и «переписывание» — вопрос магнитуды одного и того же сигнала.

Корни:
- Style-graph protocol (decision-trace approach к авторскому голосу)
- MediaPipe HandLandmarker (commodity hand tracking, GPU-accelerated)
- Cerebras inference (2k tok/s = real-time-feel)
- Hunter S. Thompson, Сорокин, Лимонов как референс «raw register»
- Geometric B&W aesthetic (контраст с teal-grid, debrand'инг)

YAGNI:
- Нет presets/save/share
- Нет multi-user collaboration
- Нет history slider
- Нет audio/mic input (это уже было в `/loop/live.html`)
- Нет export

Если что-то из YAGNI потребуется — лучше не добавлять в этот файл, а сделать v3 как отдельный fork.

---

## END

После успешного деплоя:
1. Открой URL в браузере
2. Подними руку
3. Покрути кистью
4. Если работает — поделись с тем, кто оценит инструмент-этюд (Ксения Иванова, твой style-graph community)
5. Если что-то не работает — в `app.netlify.com/projects/<name>/logs/functions` есть логи функции

Конец скилла. Подставь {{плейсхолдеры}} из interview-ответов и иди.
