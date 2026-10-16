"""Panel sesi Claude Code untuk herdr (prefix+alt+c).

Menampilkan semua sesi dari ~/.claude/projects, menandai yang sedang terbuka
di herdr, lalu bisa membuka (resume di tab baru / fokus ke pane-nya) atau
menutup sesi. Menutup hanya menghentikan proses; transcript tetap tersimpan.
"""
import glob
import json
import msvcrt
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime

PROJECTS = os.path.join(os.path.expanduser("~"), ".claude", "projects")

# Dracula
C = {
    "reset": "\x1b[0m", "bold": "\x1b[1m", "dim": "\x1b[2m", "rev": "\x1b[7m",
    "green": "\x1b[38;2;80;250;123m", "yellow": "\x1b[38;2;241;250;140m",
    "red": "\x1b[38;2;255;85;85m", "purple": "\x1b[38;2;189;147;249m",
    "pink": "\x1b[38;2;255;121;198m", "cyan": "\x1b[38;2;139;233;253m",
    "comment": "\x1b[38;2;98;114;164m",
}
STATUS_STYLE = {
    "working": ("◐ kerja", "yellow"),
    "blocked": ("◆ tunggu", "pink"),
    "idle": ("● siap", "green"),
    "done": ("● selesai", "green"),
    "unknown": ("● terbuka", "cyan"),
}


def herdr(*args, timeout=15):
    r = subprocess.run(["herdr", *args], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=timeout)
    out = (r.stdout or r.stderr).strip()
    try:
        return r.returncode, json.loads(out) if out else {}
    except json.JSONDecodeError:
        return r.returncode, {"raw": out}


def open_agents():
    """session_id -> info agent herdr (pane, tab, status)."""
    _, data = herdr("agent", "list")
    agents = {}
    for a in data.get("result", {}).get("agents", []):
        sess = a.get("agent_session") or {}
        if a.get("agent") == "claude" and sess.get("value"):
            agents[sess["value"]] = a
    return agents


def read_session(path):
    sid = os.path.splitext(os.path.basename(path))[0]
    info = {"id": sid, "path": path, "cwd": None, "title": None, "name": None,
            "last_prompt": None, "first_prompt": None, "turns": 0,
            "mtime": os.path.getmtime(path), "continued_in": None}
    with open(path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            if '"type":"api-request' in line[:40]:
                continue  # baris besar, tidak berisi metadata
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            t = d.get("type")
            if info["cwd"] is None and d.get("cwd"):
                info["cwd"] = d["cwd"]
            if t == "ai-title":
                info["title"] = d.get("aiTitle")
            elif t == "agent-name":
                info["name"] = d.get("agentName")
            elif t == "last-prompt":
                info["last_prompt"] = d.get("lastPrompt")
            elif t == "continued-in":
                info["continued_in"] = d.get("continuedInSessionId")
            elif t == "user" and not d.get("isMeta"):
                c = (d.get("message") or {}).get("content")
                if isinstance(c, str) and not c.lstrip().startswith("<"):
                    info["turns"] += 1
                    if info["first_prompt"] is None:
                        info["first_prompt"] = c.strip()
    info["label"] = (info["name"] or info["title"] or info["first_prompt"]
                     or info["last_prompt"] or "(tanpa judul)").replace("\n", " ")
    return info


def load_sessions():
    files = [p for p in glob.glob(os.path.join(PROJECTS, "*", "*.jsonl"))]
    sessions = [read_session(p) for p in files]
    sessions = [s for s in sessions if s["turns"] > 0]
    sessions.sort(key=lambda s: s["mtime"], reverse=True)
    return sessions


def width():
    return shutil.get_terminal_size((100, 30))


def cut(text, n):
    text = text or ""
    return text if len(text) <= n else text[: max(n - 1, 0)] + "…"


def read_key():
    ch = msvcrt.getwch()
    if ch in ("\x00", "\xe0"):
        return {"H": "up", "P": "down", "I": "pgup", "Q": "pgdn",
                "G": "home", "O": "end", "S": "del"}.get(msvcrt.getwch(), "")
    return {"\r": "enter", "\x1b": "esc", "\x08": "bs", "\t": "tab"}.get(ch, ch)


class Panel:
    def __init__(self):
        self.sessions, self.agents = [], {}
        self.sel, self.top = 0, 0
        self.filter, self.filtering = "", False
        self.only_open = False
        self.msg = ""
        self.refresh()

    def refresh(self):
        self.sessions = load_sessions()
        self.agents = open_agents()

    def visible(self):
        rows = self.sessions
        if self.only_open:
            rows = [s for s in rows if s["id"] in self.agents]
        if self.filter:
            q = self.filter.lower()
            rows = [s for s in rows if q in (s["label"] + " " + (s["cwd"] or "")
                                               + " " + s["id"]).lower()]
        return rows

    def draw(self):
        cols, lines = width()
        rows = self.visible()
        self.sel = max(0, min(self.sel, len(rows) - 1))
        list_h = max(lines - 9, 3)
        if self.sel < self.top:
            self.top = self.sel
        elif self.sel >= self.top + list_h:
            self.top = self.sel - list_h + 1

        n_open = sum(1 for s in self.sessions if s["id"] in self.agents)
        out = ["\x1b[H\x1b[2J"]
        head = f" Sesi Claude Code  {C['comment']}{len(self.sessions)} sesi · {n_open} terbuka"
        if self.only_open:
            head += " · hanya yang terbuka"
        out.append(f"{C['bold']}{C['purple']}{head}{C['reset']}\n")
        flt = (f"{C['yellow']}/{self.filter}{'▏' if self.filtering else ''}{C['reset']}"
               if (self.filter or self.filtering) else f"{C['comment']}/ untuk cari{C['reset']}")
        out.append(f" {flt}\n\n")

        title_w = max(cols - 40, 20)
        for i in range(self.top, min(self.top + list_h, len(rows))):
            s = rows[i]
            ag = self.agents.get(s["id"])
            if ag:
                text, color = STATUS_STYLE.get(ag.get("agent_status"), STATUS_STYLE["unknown"])
                status = f"{C[color]}{text:<10}{C['reset']}"
            else:
                status = f"{C['comment']}{'○ tutup':<10}{C['reset']}"
            when = datetime.fromtimestamp(s["mtime"]).strftime("%d %b %H:%M")
            folder = os.path.basename((s["cwd"] or "").rstrip("\\/")) or "~"
            line = f" {status} {when:<12} {cut(s['label'], title_w):<{title_w}} {C['comment']}{cut(folder, 14)}{C['reset']}"
            if i == self.sel:
                line = f"{C['rev']}{line.replace(C['reset'], C['reset'] + C['rev'])}{C['reset']}"
            out.append(line + "\x1b[K\n")
        if not rows:
            out.append(f" {C['comment']}(tidak ada sesi yang cocok){C['reset']}\n")

        # detail sesi terpilih
        out.append(f"\x1b[{lines - 5};1H{C['comment']}{'─' * cols}{C['reset']}")
        if rows:
            s = rows[self.sel]
            ag = self.agents.get(s["id"])
            where = f"pane {ag['pane_id']}" if ag else "tidak terbuka"
            out.append(f"\x1b[{lines - 4};1H {C['cyan']}{s['id']}{C['reset']}  {C['comment']}{cut(s['cwd'] or '', 40)} · {s['turns']} prompt · {where}{C['reset']}\x1b[K")
            out.append(f"\x1b[{lines - 3};1H {C['comment']}terakhir:{C['reset']} {cut(s['last_prompt'] or s['first_prompt'], cols - 12)}\x1b[K")
        out.append(f"\x1b[{lines - 2};1H {C['yellow']}{cut(self.msg, cols - 2)}{C['reset']}\x1b[K")
        keys = "↑↓ pilih · Enter buka · x tutup sesi · o hanya terbuka · r muat ulang · / cari · q keluar"
        out.append(f"\x1b[{lines - 1};1H {C['comment']}{cut(keys, cols - 2)}{C['reset']}\x1b[K")
        sys.stdout.write("".join(out))
        sys.stdout.flush()

    def confirm(self, question):
        self.msg = question + " (y/n)"
        self.draw()
        return read_key().lower() == "y"

    # ── aksi ──────────────────────────────────────────────────────────
    def open_session(self, s):
        ag = self.agents.get(s["id"])
        if ag:
            herdr("tab", "focus", ag["tab_id"])
            herdr("agent", "focus", ag["pane_id"])
            return True  # keluar dari panel, langsung ke sesinya
        cwd = s["cwd"] if s["cwd"] and os.path.isdir(s["cwd"]) else os.path.expanduser("~")
        code, res = herdr("tab", "create", "--cwd", cwd, "--label", cut(s["label"], 28), "--focus")
        pane = (res.get("result", {}).get("root_pane") or {}).get("pane_id")
        if code or not pane:
            self.msg = f"Gagal membuat tab: {res}"
            return False
        time.sleep(0.8)  # tunggu prompt shell siap
        herdr("pane", "run", pane, f"claude --resume {s['id']}")
        return True

    def close_session(self, s):
        ag = self.agents.get(s["id"])
        if not ag:
            self.msg = "Sesi ini memang sudah tertutup."
            return
        pane = ag["pane_id"]
        status = ag.get("agent_status")
        if pane == os.environ.get("HERDR_PANE_ID") or ag.get("focused"):
            if not self.confirm("Ini sesi di pane yang sedang Anda pakai. Tetap tutup?"):
                self.msg = "Batal."
                return
        if status == "working" and not self.confirm("Sesi sedang bekerja; pekerjaannya akan terhenti. Tetap tutup?"):
            self.msg = "Batal."
            return
        self.msg = "Menutup sesi..."
        self.draw()
        if status == "blocked":
            herdr("agent", "send-keys", pane, "esc")
            time.sleep(0.5)
        elif status == "working":
            herdr("agent", "send-keys", pane, "ctrl+c")
            time.sleep(1)
        herdr("agent", "prompt", pane, "/exit")
        for _ in range(16):  # tunggu Claude keluar dengan rapi (maks ~8 detik)
            time.sleep(0.5)
            if s["id"] not in open_agents():
                break
        herdr("pane", "close", pane)  # tutup pane-nya juga supaya shell tidak makan RAM
        self.agents = open_agents()
        self.msg = f"Sesi ditutup. Buka lagi kapan saja dengan Enter."

    def run(self):
        os.system("")  # aktifkan escape sequence ANSI di konsol Windows
        sys.stdout.write("\x1b[?25l")
        try:
            while True:
                self.draw()
                k = read_key()
                rows = self.visible()
                if self.filtering:
                    if k in ("enter", "esc", "tab"):
                        self.filtering = False
                        if k == "esc":
                            self.filter = ""
                    elif k == "bs":
                        self.filter = self.filter[:-1]
                    elif k in ("up", "down"):
                        self.filtering = False
                    elif len(k) == 1 and k.isprintable():
                        self.filter += k
                        self.sel = 0
                    if k not in ("up", "down"):
                        continue
                self.msg = ""
                if k in ("q", "esc"):
                    if self.filter and k == "esc":
                        self.filter = ""
                        continue
                    return
                elif k in ("up", "k"):
                    self.sel = max(self.sel - 1, 0)
                elif k in ("down", "j"):
                    self.sel = min(self.sel + 1, len(rows) - 1)
                elif k == "pgup":
                    self.sel = max(self.sel - 10, 0)
                elif k == "pgdn":
                    self.sel = min(self.sel + 10, len(rows) - 1)
                elif k == "home":
                    self.sel = 0
                elif k == "end":
                    self.sel = len(rows) - 1
                elif k == "/":
                    self.filtering = True
                elif k == "o":
                    self.only_open = not self.only_open
                    self.sel = 0
                elif k == "r":
                    self.refresh()
                    self.msg = "Daftar dimuat ulang."
                elif rows and k == "enter":
                    if self.open_session(rows[self.sel]):
                        return
                elif rows and k in ("x", "del"):
                    self.close_session(rows[self.sel])
        finally:
            sys.stdout.write("\x1b[?25h\x1b[0m\x1b[H\x1b[2J")
            sys.stdout.flush()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if os.environ.get("HERDR_ENV") != "1":
        print("Jalankan dari dalam herdr (prefix+alt+c).")
        sys.exit(1)
    Panel().run()
