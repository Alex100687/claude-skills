"""
Voice Launcher — запуск программ голосом.
Говори команду из config.json и приложение откроет нужную программу.
"""

import json
import os
import sys
import subprocess
import threading
import queue
import tkinter as tk
from tkinter import scrolledtext

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")


# ── Config ───────────────────────────────────────────────────────────

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


# ── Voice Engine ─────────────────────────────────────────────────────

class VoiceEngine:
    def __init__(self, language, commands, mic_index=None):
        import speech_recognition as sr
        import sounddevice as sd
        import numpy as np
        self.sr = sr
        self.sd = sd
        self.np = np
        self.language = language
        self.commands = {k.lower(): v for k, v in commands.items()}
        self.sample_rate = 16000
        self.chunk_size = 1024
        self.mic_index = mic_index
        # Set default device if specified
        if mic_index is not None:
            self.sd.default.device[0] = mic_index
        # Calibrate noise threshold on init
        self.energy_threshold = self._calibrate()

    def _calibrate(self, duration=0.5):
        """Record ambient noise and set threshold above it."""
        frames = int(duration * self.sample_rate)
        kw = {"samplerate": self.sample_rate, "channels": 1, "dtype": "int16"}
        if self.mic_index is not None:
            kw["device"] = self.mic_index
        ambient = self.sd.rec(frames, **kw)
        self.sd.wait()
        rms = self.np.sqrt(self.np.mean(ambient.astype(self.np.float64) ** 2))
        # Threshold = 2x ambient noise (minimum 300 to avoid ultra-sensitive mic)
        return max(rms * 2, 300)

    def listen_once(self, timeout=6, phrase_limit=5):
        """Stream from mic, detect voice, record speech, send to Google."""
        q = queue.Queue()

        def callback(indata, frames, time_info, status):
            q.put(indata.copy())

        speech_chunks = []
        silent_chunks = 0
        speech_started = False
        max_silent = int(self.sample_rate / self.chunk_size * 1.2)  # ~1.2s silence = end
        max_total = int(self.sample_rate / self.chunk_size * phrase_limit)
        wait_chunks = int(self.sample_rate / self.chunk_size * timeout)
        waited = 0

        stream_kw = {"samplerate": self.sample_rate, "channels": 1,
                     "dtype": "int16", "blocksize": self.chunk_size,
                     "callback": callback}
        if self.mic_index is not None:
            stream_kw["device"] = self.mic_index
        with self.sd.InputStream(**stream_kw):
            while True:
                try:
                    chunk = q.get(timeout=0.5)
                except Exception:
                    waited += 1
                    if waited > wait_chunks:
                        raise self.sr.WaitTimeoutError("Timeout")
                    continue

                rms = self.np.sqrt(self.np.mean(chunk.astype(self.np.float64) ** 2))

                if rms > self.energy_threshold:
                    speech_started = True
                    silent_chunks = 0
                    speech_chunks.append(chunk)
                elif speech_started:
                    silent_chunks += 1
                    speech_chunks.append(chunk)
                    if silent_chunks >= max_silent:
                        break  # Speech ended
                else:
                    waited += 1
                    if waited > wait_chunks:
                        raise self.sr.WaitTimeoutError("Timeout")

                if speech_started and len(speech_chunks) >= max_total:
                    break

        if not speech_chunks:
            raise self.sr.UnknownValueError()

        audio_np = self.np.concatenate(speech_chunks)
        raw = audio_np.tobytes()
        audio = self.sr.AudioData(raw, self.sample_rate, 2)

        text = self.sr.Recognizer().recognize_google(audio, language=self.language)
        return text.lower()

    def match_command(self, text):
        """Return (command_key, exe_path) if text matches any command."""
        best = None
        best_len = 0
        for key, exe in self.commands.items():
            if key in text and len(key) > best_len:
                best = (key, exe)
                best_len = len(key)
        return best

    @staticmethod
    def launch(exe_path):
        """Launch the program. Returns error string or None."""
        try:
            subprocess.Popen(exe_path, shell=False)
            return None
        except FileNotFoundError:
            return f"Не найден: {exe_path}"
        except OSError as e:
            return str(e)


# ── GUI ──────────────────────────────────────────────────────────────

class LauncherApp(tk.Tk):
    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg
        self.title("Voice Launcher")
        self.geometry("460x520")
        self.resizable(False, False)
        self.configure(bg="#1e1e2e")

        self.msg_queue = queue.Queue()
        self.listening = False
        self.always_on = False
        self.stop_event = threading.Event()
        self.engine = None

        self._init_engine()
        self._build_ui()
        self._poll_queue()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── engine init ──

    def _init_engine(self):
        try:
            self.engine = VoiceEngine(
                self.cfg.get("language", "ru-RU"),
                self.cfg.get("commands", {}),
                mic_index=self.cfg.get("mic_index"),
            )
            thr = int(self.engine.energy_threshold)
            self.after(200, lambda: self._log(f"[MIC] Порог шума: {thr}. Говори громче этого."))
        except Exception as e:
            self.engine = None
            self.after(200, lambda: self._log(f"[ОШИБКА] {e}"))

    # ── UI ──

    def _build_ui(self):
        style = {"bg": "#1e1e2e", "fg": "#cdd6f4", "font": ("Segoe UI", 11)}
        btn_style = {
            "bg": "#45475a", "fg": "#cdd6f4", "activebackground": "#585b70",
            "activeforeground": "#cdd6f4", "font": ("Segoe UI", 12, "bold"),
            "relief": "flat", "cursor": "hand2", "bd": 0,
        }

        # Status
        self.status_var = tk.StringVar(value="Готов")
        tk.Label(
            self, textvariable=self.status_var,
            font=("Segoe UI", 13, "bold"), bg="#1e1e2e", fg="#a6e3a1",
        ).pack(pady=(18, 6))

        # Recognized text
        self.recog_var = tk.StringVar(value="")
        tk.Label(
            self, textvariable=self.recog_var,
            font=("Segoe UI", 10), bg="#1e1e2e", fg="#89b4fa",
            wraplength=420,
        ).pack(pady=(0, 10))

        # Push-to-talk button
        self.btn = tk.Button(self, text="🎤  Нажми и говори", width=26, height=2, **btn_style)
        self.btn.pack(pady=(4, 10))
        self.btn.bind("<ButtonPress-1>", self._on_press)
        self.btn.bind("<ButtonRelease-1>", self._on_release)

        # Always-listening toggle
        self.always_var = tk.BooleanVar(value=self.cfg.get("mode") == "always_listening")
        chk = tk.Checkbutton(
            self, text="Постоянное прослушивание", variable=self.always_var,
            command=self._toggle_mode, selectcolor="#313244", **style,
        )
        chk.pack(pady=(0, 10))

        # Command list
        tk.Label(self, text="Команды:", **style).pack(anchor="w", padx=18)
        frame = tk.Frame(self, bg="#313244")
        frame.pack(padx=18, fill="x")
        for cmd, exe in self.cfg.get("commands", {}).items():
            exe_short = os.path.basename(exe) if "\\" in exe or "/" in exe else exe
            tk.Label(
                frame, text=f"  \"{cmd}\"  →  {exe_short}",
                anchor="w", bg="#313244", fg="#bac2de",
                font=("Consolas", 10),
            ).pack(anchor="w", padx=6, pady=1)

        # Log
        tk.Label(self, text="Лог:", **style).pack(anchor="w", padx=18, pady=(10, 2))
        self.log_box = scrolledtext.ScrolledText(
            self, height=5, state="disabled",
            bg="#313244", fg="#cdd6f4", font=("Consolas", 9),
            relief="flat", bd=0, wrap="word",
        )
        self.log_box.pack(padx=18, fill="x", pady=(0, 12))

        # Start always-listening if configured
        if self.always_var.get():
            self.after(500, self._start_always_listening)

    # ── Logging ──

    def _log(self, text):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", text + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    # ── Queue polling ──

    def _poll_queue(self):
        while not self.msg_queue.empty():
            msg_type, data = self.msg_queue.get_nowait()
            if msg_type == "status":
                self.status_var.set(data)
            elif msg_type == "recog":
                self.recog_var.set(data)
            elif msg_type == "log":
                self._log(data)
            elif msg_type == "color":
                self.status_var.set(self.status_var.get())  # refresh
        self.after(100, self._poll_queue)

    def _send(self, msg_type, data):
        self.msg_queue.put((msg_type, data))

    # ── Push-to-talk ──

    def _on_press(self, event=None):
        if self.always_on or self.engine is None:
            return
        self.listening = True
        self._send("status", "🎤 Слушаю...")
        self._send("recog", "")
        threading.Thread(target=self._listen_thread, daemon=True).start()

    def _on_release(self, event=None):
        self.listening = False

    def _listen_thread(self):
        if self.engine is None:
            self._send("log", "[ОШИБКА] Движок не инициализирован")
            return
        try:
            text = self.engine.listen_once(timeout=6, phrase_limit=5)
            self._send("recog", f"Распознано: «{text}»")
            self._send("log", f">> {text}")
            match = self.engine.match_command(text)
            if match:
                cmd_key, exe = match
                err = self.engine.launch(exe)
                if err:
                    self._send("status", f"Ошибка: {err}")
                    self._send("log", f"[ОШИБКА] {err}")
                else:
                    self._send("status", f"✅ Запущено: {cmd_key}")
                    self._send("log", f"[OK] {cmd_key} → {os.path.basename(exe)}")
            else:
                self._send("status", "Команда не найдена")
                self._send("log", f"[?] Нет совпадений для «{text}»")
        except Exception as e:
            name = type(e).__name__
            if "UnknownValueError" in name:
                self._send("status", "Не распознано")
                self._send("log", "[—] Речь не распознана")
            elif "WaitTimeoutError" in name:
                self._send("status", "Тишина (таймаут)")
                self._send("log", "[—] Таймаут")
            else:
                self._send("status", "Ошибка")
                self._send("log", f"[ОШИБКА] {e}")

        if not self.always_on:
            self._send("status", "Готов")

    # ── Always-listening ──

    def _toggle_mode(self):
        if self.always_var.get():
            self._start_always_listening()
        else:
            self._stop_always_listening()

    def _start_always_listening(self):
        if self.engine is None:
            self._log("[ОШИБКА] Движок не инициализирован")
            self.always_var.set(False)
            return
        self.always_on = True
        self.stop_event.clear()
        self.btn.configure(state="disabled")
        self._send("status", "🔊 Слушаю постоянно...")
        threading.Thread(target=self._always_loop, daemon=True).start()

    def _stop_always_listening(self):
        self.always_on = False
        self.stop_event.set()
        self.btn.configure(state="normal")
        self._send("status", "Готов")

    def _always_loop(self):
        while not self.stop_event.is_set():
            self._listen_thread()
            if self.stop_event.wait(0.5):
                break

    # ── Window close ──

    def _on_close(self):
        self.stop_event.set()
        self.destroy()


# ── Entry ────────────────────────────────────────────────────────────

def main():
    cfg = load_config()
    app = LauncherApp(cfg)
    app.mainloop()


if __name__ == "__main__":
    main()
