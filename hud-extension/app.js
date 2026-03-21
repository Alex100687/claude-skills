'use strict';

// ════════════════════════════════════════
// UTILITIES
// ════════════════════════════════════════
function $(id) { return document.getElementById(id); }
function todayKey() { return new Date().toISOString().slice(0, 10); }
function save(key, val) { localStorage.setItem(key, JSON.stringify(val)); }
function load(key, def) {
  try { const v = JSON.parse(localStorage.getItem(key)); return v != null ? v : def; }
  catch { return def; }
}
function uid() { return Date.now().toString(36) + Math.random().toString(36).slice(2, 7); }

// ════════════════════════════════════════
// CLOCK
// ════════════════════════════════════════
function initClock() {
  const clockEl = $('clock');
  const dateEl  = $('date');
  const DAYS   = ['Воскресенье','Понедельник','Вторник','Среда','Четверг','Пятница','Суббота'];
  const MONTHS = ['января','февраля','марта','апреля','мая','июня','июля','августа','сентября','октября','ноября','декабря'];

  function tick() {
    const n = new Date();
    const hh = String(n.getHours()).padStart(2,'0');
    const mm = String(n.getMinutes()).padStart(2,'0');
    const ss = String(n.getSeconds()).padStart(2,'0');
    clockEl.textContent = `${hh}:${mm}:${ss}`;
    dateEl.textContent  = `${DAYS[n.getDay()]}, ${n.getDate()} ${MONTHS[n.getMonth()]} ${n.getFullYear()}`;
  }
  tick();
  setInterval(tick, 1000);
}

// ════════════════════════════════════════
// TASKS
// ════════════════════════════════════════
let tasks = [];
let taskFilter = 'all';
const PRI_ORDER = { high: 0, medium: 1, low: 2 };

function initTasks() {
  tasks = load('tasks-' + todayKey(), []);

  $('addTaskBtn').addEventListener('click', addTask);
  $('taskInput').addEventListener('keydown', (e) => { if (e.key === 'Enter') addTask(); });

  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      taskFilter = btn.dataset.filter;
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      renderTasks();
    });
  });

  initVoice();
  renderTasks();
}

function addTask() {
  const input = $('taskInput');
  const text  = input.value.trim();
  if (!text) return;
  const priority = $('prioritySelect').value;
  tasks.push({ id: uid(), text, completed: false, priority });
  saveTasks();
  renderTasks();
  input.value = '';
}

function saveTasks() { save('tasks-' + todayKey(), tasks); }

function renderTasks() {
  const list = $('taskList');
  list.innerHTML = '';

  let visible = taskFilter === 'all' ? tasks.slice() : tasks.filter(t => t.priority === taskFilter);
  visible.sort((a, b) => {
    if (a.completed !== b.completed) return a.completed ? 1 : -1;
    return PRI_ORDER[a.priority] - PRI_ORDER[b.priority];
  });

  visible.forEach(task => {
    const li = document.createElement('li');
    li.className = `task-item priority-${task.priority}${task.completed ? ' completed' : ''}`;

    const circle = document.createElement('div');
    circle.className = 'task-circle';
    circle.addEventListener('click', () => toggleTask(task.id));

    const span = document.createElement('span');
    span.className = 'task-text';
    span.textContent = task.text;
    span.title = task.text;
    span.addEventListener('click', () => startEditTask(task.id, span));

    const del = document.createElement('button');
    del.className = 'task-delete';
    del.textContent = '✕';
    del.title = 'Удалить';
    del.addEventListener('click', () => deleteTask(task.id));

    li.append(circle, span, del);
    list.appendChild(li);
  });

  const done  = tasks.filter(t => t.completed).length;
  const total = tasks.length;
  $('taskStats').textContent = total ? `${done} / ${total} выполнено` : 'Задач пока нет';
}

function toggleTask(id) {
  const t = tasks.find(t => t.id === id);
  if (t) { t.completed = !t.completed; saveTasks(); renderTasks(); }
}

function deleteTask(id) {
  tasks = tasks.filter(t => t.id !== id);
  saveTasks();
  renderTasks();
}

function startEditTask(id, span) {
  const t = tasks.find(t => t.id === id);
  if (!t) return;
  const inp = document.createElement('input');
  inp.className = 'task-text-edit';
  inp.value = t.text;
  span.replaceWith(inp);
  inp.focus();
  inp.select();
  function commit() {
    const v = inp.value.trim();
    if (v) t.text = v;
    saveTasks();
    renderTasks();
  }
  inp.addEventListener('keydown', (e) => { if (e.key === 'Enter') commit(); if (e.key === 'Escape') renderTasks(); });
  inp.addEventListener('blur', commit);
}

// ════════════════════════════════════════
// VOICE INPUT
// ════════════════════════════════════════
function initVoice() {
  const SR  = window.SpeechRecognition || window.webkitSpeechRecognition;
  const btn = $('voiceBtn');

  if (!SR) {
    btn.title   = 'Голосовой ввод не поддерживается браузером';
    btn.style.opacity = '0.35';
    return;
  }

  const rec = new SR();
  rec.lang             = 'ru-RU';
  rec.interimResults   = false;
  rec.maxAlternatives  = 1;
  let listening = false;

  btn.addEventListener('click', () => { listening ? rec.stop() : rec.start(); });

  rec.addEventListener('start', () => {
    listening = true;
    btn.classList.add('listening');
    btn.textContent = '⬤ СЛУШАЮ';
  });

  rec.addEventListener('result', (e) => {
    const text = e.results[0][0].transcript.trim();
    $('taskInput').value = text;
    $('taskInput').focus();
  });

  rec.addEventListener('end', () => {
    listening = false;
    btn.classList.remove('listening');
    btn.textContent = '⬤ REC';
  });

  rec.addEventListener('error', () => {
    listening = false;
    btn.classList.remove('listening');
    btn.textContent = '⬤ REC';
  });
}

// ════════════════════════════════════════
// QUICK LINKS
// ════════════════════════════════════════
const COLORS = [
  { name:'red',    hex:'#ef4444' },
  { name:'blue',   hex:'#3b82f6' },
  { name:'green',  hex:'#22c55e' },
  { name:'purple', hex:'#a855f7' },
  { name:'pink',   hex:'#ec4899' },
  { name:'yellow', hex:'#eab308' },
  { name:'indigo', hex:'#6366f1' },
  { name:'gray',   hex:'#737373' },
];

const DEFAULT_LINKS = [
  { id: uid(), title: 'LinkedIn',   url: 'https://linkedin.com',    color: 'blue',   order: 0 },
  { id: uid(), title: 'ArtStation', url: 'https://artstation.com',  color: 'indigo', order: 1 },
  { id: uid(), title: 'Gmail',      url: 'https://mail.google.com', color: 'red',    order: 2 },
];

let links = [];
let selectedColor = 'blue';
let editingLinkId = null;

function initLinks() {
  links = load('links', null);
  if (!links) { links = DEFAULT_LINKS; save('links', links); }

  buildColorPicker();
  renderLinks();

  $('addLinkBtn').addEventListener('click', () => {
    editingLinkId = null;
    $('linkTitle').value = '';
    $('linkUrl').value   = '';
    selectedColor = 'blue';
    refreshSwatches();
    $('linkForm').classList.remove('hidden');
    $('linkTitle').focus();
  });

  $('saveLinkBtn').addEventListener('click', saveLink);
  $('cancelLinkBtn').addEventListener('click', () => $('linkForm').classList.add('hidden'));
  $('linkTitle').addEventListener('keydown', (e) => { if (e.key === 'Enter') saveLink(); });
  $('linkUrl').addEventListener('keydown',   (e) => { if (e.key === 'Enter') saveLink(); });
}

function buildColorPicker() {
  const picker = $('colorPicker');
  COLORS.forEach(c => {
    const sw = document.createElement('div');
    sw.className = 'color-swatch';
    sw.style.background = c.hex;
    sw.dataset.color = c.name;
    sw.title = c.name;
    if (c.name === selectedColor) sw.classList.add('selected');
    sw.addEventListener('click', () => { selectedColor = c.name; refreshSwatches(); });
    picker.appendChild(sw);
  });
}

function refreshSwatches() {
  document.querySelectorAll('.color-swatch').forEach(sw => {
    sw.classList.toggle('selected', sw.dataset.color === selectedColor);
  });
}

function saveLink() {
  let title = $('linkTitle').value.trim();
  let url   = $('linkUrl').value.trim();
  if (!title || !url) return;
  if (!/^https?:\/\//i.test(url)) url = 'https://' + url;

  if (editingLinkId) {
    const l = links.find(l => l.id === editingLinkId);
    if (l) Object.assign(l, { title, url, color: selectedColor });
    editingLinkId = null;
  } else {
    links.push({ id: uid(), title, url, color: selectedColor, order: links.length });
  }

  save('links', links);
  renderLinks();
  $('linkForm').classList.add('hidden');
}

function renderLinks() {
  const grid = $('linksGrid');
  grid.innerHTML = '';
  const sorted = links.slice().sort((a, b) => a.order - b.order);

  sorted.forEach(link => {
    const a = document.createElement('a');
    a.className = `link-item link-${link.color}`;
    a.href      = link.url;
    a.target    = '_blank';
    a.rel       = 'noopener noreferrer';
    a.title     = link.url;

    const label = document.createElement('span');
    label.textContent = link.title;

    const actions = document.createElement('div');
    actions.className = 'link-actions';

    const editBtn = document.createElement('button');
    editBtn.className = 'link-action-btn';
    editBtn.textContent = '✎';
    editBtn.title = 'Редактировать';
    editBtn.addEventListener('click', (e) => {
      e.preventDefault(); e.stopPropagation();
      editingLinkId = link.id;
      $('linkTitle').value = link.title;
      $('linkUrl').value   = link.url;
      selectedColor = link.color;
      refreshSwatches();
      $('linkForm').classList.remove('hidden');
      $('linkTitle').focus();
    });

    const delBtn = document.createElement('button');
    delBtn.className = 'link-action-btn';
    delBtn.textContent = '✕';
    delBtn.title = 'Удалить';
    delBtn.addEventListener('click', (e) => {
      e.preventDefault(); e.stopPropagation();
      links = links.filter(l => l.id !== link.id);
      save('links', links);
      renderLinks();
    });

    actions.append(editBtn, delBtn);
    a.append(label, actions);
    grid.appendChild(a);
  });
}

// ════════════════════════════════════════
// DOOM — RAYCASTER ENGINE
// ════════════════════════════════════════
const DOOM = (() => {

  // 0 = empty, 1-5 = wall type
  const MAP = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,2,2,2,2,0,0,0,0,0,3,3,3,0,0,0,0,1],
    [1,0,0,2,0,0,0,0,0,0,0,0,0,0,3,0,0,0,0,1],
    [1,0,0,2,0,0,0,0,0,0,0,0,0,0,3,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,4,4,4,4,0,0,0,0,0,5,5,0,1],
    [1,0,0,0,0,0,0,4,0,0,0,0,0,0,0,0,5,0,0,1],
    [1,0,0,0,0,0,0,4,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
  ];
  const MAP_W = MAP[0].length;
  const MAP_H = MAP.length;

  // [bright face, dark face]
  const WALL_C = {
    1: ['#8B1818','#5a0f0f'],
    2: ['#585858','#323232'],
    3: ['#1e7a1e','#114a11'],
    4: ['#7a4a15','#4a2a08'],
    5: ['#1a1a8b','#0e0e55'],
  };

  const FOV   = Math.PI / 3;  // 60°
  const SPEED = 0.055;
  const ROT   = 0.042;

  let canvas, ctx, W, H;
  let px = 2, py = 2, pa = 0;
  let keys = {};
  let running = false;
  let raf;

  function wallAt(mx, my) {
    if (mx < 0 || mx >= MAP_W || my < 0 || my >= MAP_H) return 1;
    return MAP[my][mx];
  }

  function update() {
    // Block keyboard when an input is focused
    const ae = document.activeElement;
    if (ae && (ae.tagName === 'INPUT' || ae.tagName === 'TEXTAREA' || ae.tagName === 'SELECT')) return;

    let nx = px, ny = py;
    if (keys['ArrowUp']   || keys['w'] || keys['W']) { nx += Math.cos(pa)*SPEED; ny += Math.sin(pa)*SPEED; }
    if (keys['ArrowDown'] || keys['s'] || keys['S']) { nx -= Math.cos(pa)*SPEED; ny -= Math.sin(pa)*SPEED; }
    if (keys['ArrowLeft'] || keys['a'] || keys['A']) pa -= ROT;
    if (keys['ArrowRight']|| keys['d'] || keys['D']) pa += ROT;

    const M = 0.18;
    if (!wallAt(Math.floor(nx), Math.floor(py))) px = nx;
    else if (!wallAt(Math.floor(px + M * Math.sign(nx - px)), Math.floor(py))) px += M * Math.sign(nx - px);
    if (!wallAt(Math.floor(px), Math.floor(ny))) py = ny;
    else if (!wallAt(Math.floor(px), Math.floor(py + M * Math.sign(ny - py)))) py += M * Math.sign(ny - py);
  }

  function render() {
    // Sky (ceiling)
    const skyGrad = ctx.createLinearGradient(0, 0, 0, H * 0.5);
    skyGrad.addColorStop(0, '#1a0000');
    skyGrad.addColorStop(1, '#080000');
    ctx.fillStyle = skyGrad;
    ctx.fillRect(0, 0, W, H * 0.5);

    // Floor
    const floorGrad = ctx.createLinearGradient(0, H * 0.5, 0, H);
    floorGrad.addColorStop(0, '#0d0d0d');
    floorGrad.addColorStop(1, '#1c1c1c');
    ctx.fillStyle = floorGrad;
    ctx.fillRect(0, H * 0.5, W, H * 0.5);

    // Raycasting — DDA
    for (let col = 0; col < W; col++) {
      const rayA = pa - FOV / 2 + (FOV * col) / W;
      const rdx  = Math.cos(rayA);
      const rdy  = Math.sin(rayA);

      let mx = Math.floor(px);
      let my = Math.floor(py);

      const eps    = 1e-10;
      const ddx    = Math.abs(1 / (rdx || eps));
      const ddy    = Math.abs(1 / (rdy || eps));
      const stepX  = rdx < 0 ? -1 : 1;
      const stepY  = rdy < 0 ? -1 : 1;
      let sdx      = rdx < 0 ? (px - mx) * ddx : (mx + 1 - px) * ddx;
      let sdy      = rdy < 0 ? (py - my) * ddy : (my + 1 - py) * ddy;

      let side = 0, wt = 0;
      for (let i = 0; i < 80; i++) {
        if (sdx < sdy) { sdx += ddx; mx += stepX; side = 0; }
        else           { sdy += ddy; my += stepY; side = 1; }
        wt = wallAt(mx, my);
        if (wt !== 0) break;
      }

      // Perpendicular wall distance (already fisheye-corrected by DDA)
      const perp = side === 0 ? sdx - ddx : sdy - ddy;
      const wallH = Math.min(H * 8, Math.floor(H / Math.max(perp, 0.001)));
      const top   = Math.floor((H - wallH) / 2);

      const colors = WALL_C[wt] || WALL_C[1];
      ctx.fillStyle = side === 0 ? colors[0] : colors[1];
      ctx.fillRect(col, top, 1, wallH);
    }

    drawCrosshair();
    drawMinimap();
  }

  function drawCrosshair() {
    ctx.strokeStyle = 'rgba(255,50,50,0.9)';
    ctx.lineWidth   = 1;
    const cx = W / 2, cy = H / 2;
    ctx.beginPath();
    ctx.moveTo(cx - 8, cy); ctx.lineTo(cx + 8, cy);
    ctx.moveTo(cx, cy - 8); ctx.lineTo(cx, cy + 8);
    ctx.stroke();
  }

  function drawMinimap() {
    const sz = 4, ox = 6, oy = 6;
    ctx.globalAlpha = 0.72;
    for (let y = 0; y < MAP_H; y++) {
      for (let x = 0; x < MAP_W; x++) {
        const wt = MAP[y][x];
        ctx.fillStyle = wt ? (WALL_C[wt] ? WALL_C[wt][0] : '#8B1818') : 'rgba(0,0,0,0.55)';
        ctx.fillRect(ox + x * sz, oy + y * sz, sz - 1, sz - 1);
      }
    }
    // Player dot
    ctx.fillStyle = '#00ff88';
    ctx.fillRect(ox + px * sz - 2, oy + py * sz - 2, 4, 4);
    // Direction ray
    ctx.strokeStyle = '#00ff88';
    ctx.lineWidth   = 1;
    ctx.beginPath();
    ctx.moveTo(ox + px * sz, oy + py * sz);
    ctx.lineTo(ox + (px + Math.cos(pa) * 2) * sz, oy + (py + Math.sin(pa) * 2) * sz);
    ctx.stroke();
    ctx.globalAlpha = 1;
  }

  function loop() {
    if (!running) return;
    update();
    render();
    raf = requestAnimationFrame(loop);
  }

  function onKeyDown(e) {
    keys[e.key] = true;
    // Prevent arrow keys from scrolling the page while playing
    const ae = document.activeElement;
    if (ae && (ae.tagName === 'INPUT' || ae.tagName === 'TEXTAREA' || ae.tagName === 'SELECT')) return;
    if (['ArrowUp','ArrowDown','ArrowLeft','ArrowRight'].includes(e.key)) e.preventDefault();
  }
  function onKeyUp(e) { keys[e.key] = false; }

  function init(c) {
    canvas = c;
    ctx    = canvas.getContext('2d');
    W      = canvas.width;
    H      = canvas.height;
    px = 1.5; py = 1.5; pa = 0.4;
    running = true;
    document.addEventListener('keydown', onKeyDown);
    document.addEventListener('keyup',   onKeyUp);
    loop();
  }

  function stop() {
    running = false;
    if (raf) cancelAnimationFrame(raf);
    document.removeEventListener('keydown', onKeyDown);
    document.removeEventListener('keyup',   onKeyUp);
  }

  return { init, stop };
})();

function initDoom() {
  const canvas  = $('doomCanvas');
  const wrapper = $('doomWrapper');
  const overlay = $('doomOverlay');

  // Set fixed pixel resolution (CSS will scale it)
  canvas.width  = 320;
  canvas.height = 200;

  overlay.addEventListener('click', () => {
    overlay.style.display = 'none';
    DOOM.init(canvas);
  });

  // Re-click on canvas to refocus (if tabbing away)
  canvas.addEventListener('click', () => {
    // Blur any focused input so DOOM gets keys
    if (document.activeElement && document.activeElement !== document.body) {
      document.activeElement.blur();
    }
  });
}

// ════════════════════════════════════════
// BOOT
// ════════════════════════════════════════
document.addEventListener('DOMContentLoaded', () => {
  initClock();
  initTasks();
  initLinks();
  initDoom();
});
