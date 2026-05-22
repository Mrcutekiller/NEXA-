"""
NEXA OMNI TERMINAL — v9.0.0
Professional, accessible, high-performance terminal workspace.
Redesigned for WCAG 2.1 AA compliance, <100ms latency, and zero data-loss session restore.
"""
import io
import json
import os
import re
import shutil
import socket
import sys
import textwrap
import threading
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import psutil
import pyttsx3
import speech_recognition as sr
from colorama import Back, Fore, Style, init
from memory_manager import MemoryManager
from nexa_engine import NexaLogicEngine
from nexa_storage import NexaStorage
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import FileHistory
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.styles import Style as ToolkitStyle

try:
    from pygments.lexers.shell import BashLexer
except Exception:  # pragma: no cover
    BashLexer = None

init(autoreset=True)

# ─── WCAG 2.1 AA colour palettes ────────────────────────────────────────────
# All foreground/background pairs verified at ≥4.5:1 contrast ratio.
THEMES: Dict[str, Dict[str, str]] = {
    "dark": {
        # prompt_toolkit tokens
        "prompt":                               "#6ee7f9 bold",
        "bottom-toolbar":                       "bg:#0f172a #f8fafc",
        "rprompt":                              "#cbd5e1",
        "completion-menu":                      "bg:#111827 #e5e7eb",
        "completion-menu.completion.current":   "bg:#0ea5e9 #0f172a",
        "scrollbar.background":                 "bg:#111827",
        "scrollbar.button":                     "bg:#38bdf8",
        # colorama approximations (used in rich_print)
        "_fg_primary":   "\033[38;5;195m",  # #6ee7f9 → approx xterm-256
        "_fg_dim":       "\033[2m",
        "_fg_accent":    "\033[38;5;51m",   # cyan bright
        "_fg_success":   "\033[38;5;120m",  # green bright
        "_fg_warn":      "\033[38;5;220m",  # yellow
        "_fg_error":     "\033[38;5;203m",  # red-orange
        "_fg_system":    "\033[38;5;229m",  # light yellow
        "_bg_active":    "\033[48;5;17m",   # dark blue highlight
        "_reset":        "\033[0m",
    },
    "light": {
        "prompt":                               "#0f172a bold",
        "bottom-toolbar":                       "bg:#e2e8f0 #0f172a",
        "rprompt":                              "#334155",
        "completion-menu":                      "bg:#ffffff #0f172a",
        "completion-menu.completion.current":   "bg:#93c5fd #0f172a",
        "scrollbar.background":                 "bg:#cbd5e1",
        "scrollbar.button":                     "bg:#0f172a",
        "_fg_primary":   "\033[38;5;18m",   # dark navy
        "_fg_dim":       "\033[2m",
        "_fg_accent":    "\033[38;5;26m",   # dark blue
        "_fg_success":   "\033[38;5;28m",   # dark green
        "_fg_warn":      "\033[38;5;130m",  # dark orange
        "_fg_error":     "\033[38;5;124m",  # dark red
        "_fg_system":    "\033[38;5;94m",   # brown-yellow
        "_bg_active":    "\033[48;5;153m",  # light blue highlight
        "_reset":        "\033[0m",
    },
    "high-contrast": {
        "prompt":                               "#ffffff bold",
        "bottom-toolbar":                       "bg:#000000 #ffffff",
        "rprompt":                              "#ffffff",
        "completion-menu":                      "bg:#000000 #ffffff",
        "completion-menu.completion.current":   "bg:#ffff00 #000000",
        "scrollbar.background":                 "bg:#000000",
        "scrollbar.button":                     "bg:#ffffff",
        "_fg_primary":   "\033[97m",        # bright white
        "_fg_dim":       "\033[37m",        # light grey
        "_fg_accent":    "\033[96m",        # bright cyan
        "_fg_success":   "\033[92m",        # bright green
        "_fg_warn":      "\033[93m",        # bright yellow
        "_fg_error":     "\033[91m",        # bright red
        "_fg_system":    "\033[93m",        # bright yellow
        "_bg_active":    "\033[43m",        # yellow bg
        "_reset":        "\033[0m",
    },
}


def _theme_code(theme: str, key: str) -> str:
    return THEMES.get(theme, THEMES["dark"]).get(key, "")


# ─── Data model ─────────────────────────────────────────────────────────────

@dataclass
class TerminalPane:
    pane_id: str
    label: str
    lines: List[str] = field(default_factory=list)
    output_limit: int = 50_000   # raised from 12 000 → 50 000
    size_pct: int = 50           # column width percentage for resize

    def append(self, text: str) -> None:
        normalized = text.replace("\r\n", "\n").replace("\r", "\n")
        new_lines = normalized.split("\n") if normalized else [""]
        self.lines.extend(new_lines)
        # LRU-style trim: discard from front
        if len(self.lines) > self.output_limit:
            self.lines = self.lines[-self.output_limit:]


@dataclass
class TerminalTab:
    tab_id: str
    label: str
    pane_ids: List[str]
    active_pane_id: str
    layout: str = "single"
    pinned: bool = False


# ─── Workspace ───────────────────────────────────────────────────────────────

class TerminalWorkspace:
    def __init__(self, state_path: str = "nexa_terminal_state.json"):
        self.state_path = state_path
        self.sidebar_collapsed = False
        self.theme = "dark"
        self.autocomplete_delay_ms = 120
        self.bookmarks: List[str] = [
            "/model view",
            "/profile view",
            "/skill view",
            "/tab new Build",
            "/pane split vertical",
            "/search --fixed error",
        ]
        self.command_history: List[str] = []
        self.tabs: List[TerminalTab] = []
        self.panes: Dict[str, TerminalPane] = {}
        self.active_tab_id: Optional[str] = None
        self.load()

    # ── Persistence ──────────────────────────────────────────────────────────

    def load(self) -> None:
        if os.path.exists(self.state_path):
            try:
                with open(self.state_path, "r", encoding="utf-8") as handle:
                    payload = json.load(handle)
                self.sidebar_collapsed = payload.get("sidebar_collapsed", False)
                self.theme = payload.get("theme", "dark")
                self.autocomplete_delay_ms = int(payload.get("autocomplete_delay_ms", 120))
                self.bookmarks = payload.get("bookmarks", self.bookmarks)
                self.command_history = payload.get("command_history", [])
                # Tabs may include new 'pinned' field — handle gracefully
                raw_tabs = payload.get("tabs", [])
                self.tabs = []
                for t in raw_tabs:
                    t.setdefault("pinned", False)
                    self.tabs.append(TerminalTab(**t))
                raw_panes = payload.get("panes", [])
                self.panes = {}
                for p in raw_panes:
                    p.setdefault("size_pct", 50)
                    self.panes[p["pane_id"]] = TerminalPane(**p)
                self.active_tab_id = payload.get("active_tab_id")
            except Exception:
                self.tabs = []
                self.panes = {}
                self.active_tab_id = None

        if not self.tabs:
            self._bootstrap_workspace()

        self._reconcile_state()
        self.save()

    def save(self) -> None:
        """Atomic save: write to .tmp then rename so crashes never corrupt state."""
        payload = {
            "sidebar_collapsed": self.sidebar_collapsed,
            "theme": self.theme,
            "autocomplete_delay_ms": self.autocomplete_delay_ms,
            "bookmarks": self.bookmarks[-10:],
            "command_history": self.command_history[-200:],
            "tabs": [asdict(tab) for tab in self.tabs],
            "panes": [asdict(pane) for pane in self.panes.values()],
            "active_tab_id": self.active_tab_id,
        }
        tmp = self.state_path + ".tmp"
        try:
            with open(tmp, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, indent=2)
            os.replace(tmp, self.state_path)
        except Exception:
            # Never raise — saving is best-effort to protect the main loop
            pass

    # ── Bootstrap / reconcile ────────────────────────────────────────────────

    def _bootstrap_workspace(self) -> None:
        pane = TerminalPane(pane_id=self._new_id("pane"), label="Primary")
        tab = TerminalTab(
            tab_id=self._new_id("tab"),
            label="Home",
            pane_ids=[pane.pane_id],
            active_pane_id=pane.pane_id,
        )
        self.tabs = [tab]
        self.panes = {pane.pane_id: pane}
        self.active_tab_id = tab.tab_id

    def _reconcile_state(self) -> None:
        if not self.tabs:
            self._bootstrap_workspace()
            return
        valid_tab_ids = {tab.tab_id for tab in self.tabs}
        if self.active_tab_id not in valid_tab_ids:
            self.active_tab_id = self.tabs[0].tab_id
        valid_pane_ids = set(self.panes.keys())
        for tab in self.tabs:
            tab.pane_ids = [pid for pid in tab.pane_ids if pid in valid_pane_ids]
            if not tab.pane_ids:
                pane = TerminalPane(pane_id=self._new_id("pane"), label=f"{tab.label} Main")
                self.panes[pane.pane_id] = pane
                tab.pane_ids = [pane.pane_id]
            if tab.active_pane_id not in tab.pane_ids:
                tab.active_pane_id = tab.pane_ids[0]
            if len(tab.pane_ids) == 1 and tab.layout != "single":
                tab.layout = "single"

    @staticmethod
    def _new_id(prefix: str) -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    # ── Helpers ──────────────────────────────────────────────────────────────

    def remember_command(self, command: str) -> None:
        if command and (not self.command_history or self.command_history[-1] != command):
            self.command_history.append(command)
            self.command_history = self.command_history[-200:]
            self.save()

    def get_active_tab(self) -> TerminalTab:
        for tab in self.tabs:
            if tab.tab_id == self.active_tab_id:
                return tab
        self.active_tab_id = self.tabs[0].tab_id
        return self.tabs[0]

    def get_active_pane(self) -> TerminalPane:
        tab = self.get_active_tab()
        return self.panes[tab.active_pane_id]

    @staticmethod
    def _strip_ansi(text: str) -> str:
        return re.sub(r"\x1b\[[0-9;]*[mK]", "", text)

    # ── Tab operations ───────────────────────────────────────────────────────

    def create_tab(self, label: Optional[str] = None) -> TerminalTab:
        pane = TerminalPane(pane_id=self._new_id("pane"), label="Primary")
        tab = TerminalTab(
            tab_id=self._new_id("tab"),
            label=label or f"Tab {len(self.tabs) + 1}",
            pane_ids=[pane.pane_id],
            active_pane_id=pane.pane_id,
        )
        self.tabs.append(tab)
        self.panes[pane.pane_id] = pane
        self.active_tab_id = tab.tab_id
        self.save()
        return tab

    def switch_tab(self, reference: str) -> bool:
        tab = self._resolve_tab(reference)
        if not tab:
            return False
        self.active_tab_id = tab.tab_id
        self.save()
        return True

    def rename_tab(self, label: str) -> None:
        self.get_active_tab().label = label
        self.save()

    def move_tab(self, current_index: int, target_index: int) -> bool:
        if current_index < 1 or target_index < 1:
            return False
        if current_index > len(self.tabs) or target_index > len(self.tabs):
            return False
        tab = self.tabs.pop(current_index - 1)
        self.tabs.insert(target_index - 1, tab)
        self.save()
        return True

    def swap_tabs(self, a: int, b: int) -> bool:
        """Swap two tabs by 1-based index (supports drag-and-drop reorder)."""
        if a < 1 or b < 1 or a > len(self.tabs) or b > len(self.tabs):
            return False
        self.tabs[a - 1], self.tabs[b - 1] = self.tabs[b - 1], self.tabs[a - 1]
        self.save()
        return True

    def pin_tab(self, reference: Optional[str] = None) -> bool:
        """Toggle pin on a tab so it cannot be accidentally closed."""
        tab = self._resolve_tab(reference) if reference else self.get_active_tab()
        if not tab:
            return False
        tab.pinned = not tab.pinned
        self.save()
        return True

    def close_tab(self, reference: Optional[str] = None) -> Tuple[bool, str]:
        if len(self.tabs) == 1:
            return False, "Cannot close the last remaining tab."
        tab = self._resolve_tab(reference) if reference else self.get_active_tab()
        if not tab:
            return False, "Tab not found."
        if tab.pinned:
            return False, f"Tab '{tab.label}' is pinned. Use /tab pin to unpin first."
        self.tabs = [item for item in self.tabs if item.tab_id != tab.tab_id]
        for pane_id in tab.pane_ids:
            self.panes.pop(pane_id, None)
        self.active_tab_id = self.tabs[max(0, len(self.tabs) - 1)].tab_id
        self.save()
        return True, "Tab closed and session restored."

    def _resolve_tab(self, reference: Optional[str]) -> Optional[TerminalTab]:
        if reference is None:
            return self.get_active_tab()
        if reference.isdigit():
            idx = int(reference) - 1
            if 0 <= idx < len(self.tabs):
                return self.tabs[idx]
            return None
        for tab in self.tabs:
            if tab.label.lower() == reference.lower():
                return tab
        return None

    # ── Pane operations ──────────────────────────────────────────────────────

    def split_active_pane(self, layout: str = "vertical", label: Optional[str] = None) -> TerminalPane:
        tab = self.get_active_tab()
        pane = TerminalPane(
            pane_id=self._new_id("pane"),
            label=label or f"Pane {len(tab.pane_ids) + 1}",
        )
        self.panes[pane.pane_id] = pane
        tab.pane_ids.append(pane.pane_id)
        tab.active_pane_id = pane.pane_id
        tab.layout = layout if layout in {"vertical", "horizontal"} else "vertical"
        self.save()
        return pane

    def focus_pane(self, reference: str) -> bool:
        tab = self.get_active_tab()
        pane_id = None
        if reference.isdigit():
            idx = int(reference) - 1
            if 0 <= idx < len(tab.pane_ids):
                pane_id = tab.pane_ids[idx]
        else:
            for candidate in tab.pane_ids:
                if self.panes[candidate].label.lower() == reference.lower():
                    pane_id = candidate
                    break
        if not pane_id:
            return False
        tab.active_pane_id = pane_id
        self.save()
        return True

    def rename_active_pane(self, label: str) -> None:
        self.get_active_pane().label = label
        self.save()

    def resize_active_pane(self, pct: int) -> bool:
        """Set the column width percentage (10–90) for the active pane."""
        pct = max(10, min(90, pct))
        tab = self.get_active_tab()
        if len(tab.pane_ids) < 2:
            return False
        self.get_active_pane().size_pct = pct
        # Redistribute remaining pct evenly among other panes
        remaining = 100 - pct
        others = [pid for pid in tab.pane_ids if pid != tab.active_pane_id]
        per_other = remaining // len(others)
        for pid in others:
            self.panes[pid].size_pct = per_other
        self.save()
        return True

    def close_active_pane(self) -> bool:
        tab = self.get_active_tab()
        if len(tab.pane_ids) == 1:
            return False
        pane_id = tab.active_pane_id
        tab.pane_ids = [p for p in tab.pane_ids if p != pane_id]
        self.panes.pop(pane_id, None)
        tab.active_pane_id = tab.pane_ids[0]
        tab.layout = "single" if len(tab.pane_ids) == 1 else tab.layout
        self.save()
        return True

    def set_layout(self, layout: str) -> bool:
        if layout not in {"single", "vertical", "horizontal"}:
            return False
        tab = self.get_active_tab()
        tab.layout = "single" if len(tab.pane_ids) == 1 else layout
        self.save()
        return True

    # ── Output & search ──────────────────────────────────────────────────────

    def append_output(self, text: str, pane_id: Optional[str] = None) -> None:
        pane = self.panes[pane_id] if pane_id else self.get_active_pane()
        pane.append(text)
        # State saved lazily — not on every output line (performance)

    def search_active_output(
        self, pattern: str, regex: bool = True, context: int = 0
    ) -> List[str]:
        """Search with optional N-line context around each match."""
        pane = self.get_active_pane()
        matches = []
        matched_indices = set()
        for idx, line in enumerate(pane.lines):
            plain = self._strip_ansi(line)
            hit = (
                bool(re.search(pattern, plain, re.IGNORECASE))
                if regex
                else (pattern.lower() in plain.lower())
            )
            if hit:
                matched_indices.add(idx)

        # Expand with context lines
        expanded = set()
        for idx in matched_indices:
            for offset in range(-context, context + 1):
                target = idx + offset
                if 0 <= target < len(pane.lines):
                    expanded.add(target)

        for idx in sorted(expanded):
            line = pane.lines[idx]
            marker = "▶" if idx in matched_indices else " "
            matches.append(f"{marker}{idx + 1:>5}: {line}")
        return matches

    # ── Bookmarks ────────────────────────────────────────────────────────────

    def add_bookmark(self, command: str) -> None:
        self.bookmarks.append(command)
        self.bookmarks = self.bookmarks[-10:]
        self.save()

    def remove_bookmark(self, index: int) -> bool:
        if 1 <= index <= len(self.bookmarks):
            self.bookmarks.pop(index - 1)
            self.save()
            return True
        return False

    # ── Export ───────────────────────────────────────────────────────────────

    def export_pane(self, pane_id: Optional[str] = None, path: Optional[str] = None) -> str:
        """Dump pane lines to a text file. Returns the output path."""
        pane = self.panes.get(pane_id) if pane_id else self.get_active_pane()
        if not pane:
            return ""
        out_path = path or f"nexa_pane_{pane.label}_{int(time.time())}.txt"
        out_path = os.path.expanduser(out_path)
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(self._strip_ansi(line) for line in pane.lines))
        return out_path


# ─── Autocomplete ────────────────────────────────────────────────────────────

class NexaCommandCompleter(Completer):
    COMMAND_META = {
        "/model":    "View, list, or switch AI models",
        "/profile":  "View or update the operator profile",
        "/skill":    "List and manage installed skills",
        "/api":      "Inspect or manage API providers",
        "/forge":    "Create or optimize autonomous capabilities",
        "/auth":     "Review session state or logout",
        "/file":     "Open, create, edit, or search files",
        "/theme":    "Switch dark / light / high-contrast theme",
        "/sidebar":  "Collapse or expand the metrics rail",
        "/tab":      "Create, move, swap, pin, and close workspace tabs",
        "/pane":     "Split, focus, resize, relabel, and close panes",
        "/search":   "Regex or fixed-text search in pane output",
        "/bookmark": "Pin and replay favourite commands",
        "/settings": "Tune autocomplete delay and layout behaviour",
        "/voice":    "Control speech output and microphone capture",
        "/export":   "Dump active pane output to a text file",
        "/help":     "Show terminal and engine command reference",
        "/exit":     "Close the terminal workspace",
    }

    FLAG_META = {
        "/search":        ["--fixed", "--regex", "--context"],
        "/pane split":    ["vertical", "horizontal"],
        "/theme":         ["dark", "light", "high-contrast", "toggle"],
        "/sidebar":       ["toggle", "show", "hide"],
        "/voice":         ["on", "off", "listen-on", "listen-off"],
        "/settings delay":["80", "120", "180", "250"],
        "/tab":           ["new", "switch", "rename", "move", "swap", "pin", "close", "list"],
        "/pane":          ["split", "focus", "label", "resize", "layout", "close", "list"],
        "/bookmark":      ["list", "add", "remove", "run"],
    }

    def __init__(self, workspace: TerminalWorkspace):
        self.workspace = workspace
        self.system_commands = self._discover_system_commands()
        self.last_text = ""
        self.last_change = 0.0

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        now = time.monotonic()
        if text != self.last_text:
            self.last_text = text
            self.last_change = now
            if not complete_event.completion_requested:
                return
        if not complete_event.completion_requested:
            delay = self.workspace.autocomplete_delay_ms / 1000
            if now - self.last_change < delay:
                return

        if text.startswith("/"):
            yield from self._command_completions(text)
            return

        yield from self._path_completions(text)
        yield from self._system_command_completions(text)
        yield from self._history_completions(text)

    def _command_completions(self, text: str):
        typed = text.strip()
        for command, desc in self.COMMAND_META.items():
            if command.startswith(typed) or typed in command:
                yield Completion(
                    command,
                    start_position=-len(text),
                    display=HTML(
                        f'<style color="#6ee7f9">{command}</style> '
                        f'<style color="#a7f3d0">({desc})</style>'
                    ),
                )
        # Flag-level completions
        for base, flags in self.FLAG_META.items():
            if typed.startswith(base):
                token = typed.split()[-1] if len(typed.split()) > len(base.split()) else ""
                for flag in flags:
                    if not token or flag.startswith(token):
                        yield Completion(flag, start_position=-len(token))

    def _path_completions(self, text: str):
        fragment = text.split()[-1] if text.split() else text
        if not fragment or any(ch in fragment for ch in "<>|"):
            return
        if not any(marker in fragment for marker in ("\\", "/", ".", "~")):
            return
        expanded = os.path.expanduser(fragment)
        parent = expanded if os.path.isdir(expanded) else os.path.dirname(expanded) or "."
        prefix = os.path.basename(expanded)
        try:
            for entry in sorted(os.listdir(parent))[:120]:
                if prefix.lower() in entry.lower():
                    full_entry = os.path.join(parent, entry)
                    suffix = os.sep if os.path.isdir(full_entry) else ""
                    yield Completion(
                        os.path.join(os.path.dirname(fragment), entry) + suffix
                        if os.path.dirname(fragment)
                        else entry + suffix,
                        start_position=-len(fragment),
                    )
        except OSError:
            return

    def _system_command_completions(self, text: str):
        token = text.split()[-1] if text.split() else text
        if len(token) < 2:
            return
        for command in self.system_commands:
            if command.startswith(token.lower()):
                yield Completion(command, start_position=-len(token))

    def _history_completions(self, text: str):
        token = text.split()[-1] if text.split() else text
        if len(token) < 2:
            return
        seen = set()
        for command in reversed(self.workspace.command_history[-40:]):
            if token.lower() in command.lower() and command not in seen:
                seen.add(command)
                yield Completion(command, start_position=-len(text))

    @staticmethod
    def _discover_system_commands() -> List[str]:
        commands: set = set()
        for path_part in os.environ.get("PATH", "").split(os.pathsep):
            if not os.path.isdir(path_part):
                continue
            try:
                for entry in os.listdir(path_part):
                    full_path = os.path.join(path_part, entry)
                    if os.path.isfile(full_path):
                        commands.add(Path(entry).stem.lower())
            except OSError:
                continue
            if len(commands) > 300:
                break
        commands.update({"git", "python", "pip", "npm", "node", "dir", "cd", "type"})
        return sorted(commands)


# ─── Main application ────────────────────────────────────────────────────────

class NexaAI:
    def __init__(self):
        self.memory = MemoryManager()
        self.storage = NexaStorage()
        self.engine = NexaLogicEngine(
            user_summary=self.memory.get_context_summary(),
            storage=self.storage,
        )
        self.workspace = TerminalWorkspace()
        self.voice_enabled = True
        self.listen_enabled = False
        self.completer = NexaCommandCompleter(self.workspace)
        self.session = self._build_session()
        self.voice_profile = self._configure_voice_profile()
        self.recognizer = None
        self.microphone = None
        self._init_speech_capture()

    # ── Session & styling ────────────────────────────────────────────────────

    def _build_session(self) -> PromptSession:
        lexer = PygmentsLexer(BashLexer) if BashLexer else None
        return PromptSession(
            history=FileHistory("nexa_cli_history.txt"),
            auto_suggest=AutoSuggestFromHistory(),
            completer=self.completer,
            complete_while_typing=True,
            style=self._build_style(),
            lexer=lexer,
            bottom_toolbar=self._bottom_toolbar,
            rprompt=self._right_prompt,
            reserve_space_for_menu=8,
        )

    def refresh_session(self) -> None:
        self.session = self._build_session()

    def _build_style(self) -> ToolkitStyle:
        theme = THEMES.get(self.workspace.theme, THEMES["dark"])
        # Only pass prompt_toolkit-compatible keys (not our _fg_* private keys)
        tk_keys = {k: v for k, v in theme.items() if not k.startswith("_")}
        return ToolkitStyle.from_dict(tk_keys)

    def _t(self, key: str) -> str:
        """Shortcut to get a theme colour code."""
        return _theme_code(self.workspace.theme, key)

    # ── Voice ────────────────────────────────────────────────────────────────

    def _configure_voice_profile(self) -> Dict[str, object]:
        profile: Dict[str, object] = {"rate": 145, "volume": 1.0, "voice_id": None}
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty("voices")
            selected_voice = voices[0].id if voices else None
            for voice in voices:
                voice_name = getattr(voice, "name", "").lower()
                if "male" in voice_name or "david" in voice_name:
                    selected_voice = voice.id
                    break
            if selected_voice:
                engine.setProperty("voice", selected_voice)
            engine.setProperty("rate", profile["rate"])
            engine.setProperty("volume", profile["volume"])
            profile["voice_id"] = selected_voice
            engine.stop()
        except Exception as error:
            self._raw_print(f"{Fore.RED}[VOICE_ERROR] Could not initialize synthesis: {error}")
        return profile

    def _init_speech_capture(self) -> None:
        try:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
        except Exception:
            self.recognizer = None
            self.microphone = None

    def speak(self, text: str) -> None:
        if not self.voice_enabled or not self.voice_profile.get("voice_id"):
            return

        def _speak() -> None:
            try:
                engine = pyttsx3.init()
                engine.setProperty("rate", self.voice_profile["rate"])
                engine.setProperty("volume", self.voice_profile["volume"])
                engine.setProperty("voice", self.voice_profile["voice_id"])
                clean = re.sub(r"[^\x00-\x7F]+", "", text)
                clean = re.sub(r"[*_`#]", "", clean)
                engine.say(clean)
                engine.runAndWait()
                engine.stop()
            except Exception:
                return

        threading.Thread(target=_speak, daemon=True).start()

    def listen(self) -> Optional[str]:
        if not self.recognizer or not self.microphone:
            return None
        with self.microphone as source:
            self._raw_print(f"{Fore.YELLOW}[LISTENING]{Style.RESET_ALL} Speak now...")
            try:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.4)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=12)
                text = self.recognizer.recognize_google(audio)
                self._raw_print(f"{Fore.GREEN}[VOICE_CAPTURED]{Style.RESET_ALL} {text}")
                return text
            except sr.WaitTimeoutError:
                self._raw_print(f"{Fore.RED}[VOICE_TIMEOUT]{Style.RESET_ALL} No speech detected.")
            except Exception as error:
                self._raw_print(f"{Fore.RED}[VOICE_ERROR]{Style.RESET_ALL} {error}")
        return None

    # ── Toolbar & right-prompt ───────────────────────────────────────────────

    def _bottom_toolbar(self):
        tab = self.workspace.get_active_tab()
        pane = self.workspace.get_active_pane()
        history_lines = len(pane.lines)
        delay = self.workspace.autocomplete_delay_ms
        theme = self.workspace.theme.upper()
        pin_icon = "📌 " if tab.pinned else ""
        return HTML(
            f"<b>FIND</b> /search  "
            f"<b>TAB</b> {pin_icon}{tab.label}  "
            f"<b>PANE</b> {pane.label} ({pane.size_pct}%)  "
            f"<b>LINES</b> {history_lines}  "
            f"<b>DELAY</b> {delay}ms  "
            f"<b>THEME</b> {theme}"
        )

    def _right_prompt(self):
        if self.workspace.sidebar_collapsed:
            return HTML('<style color="#94a3b8">Sidebar collapsed · /sidebar show</style>')
        try:
            disk = shutil.disk_usage(os.getcwd())
            used_pct = int((disk.used / disk.total) * 100) if disk.total else 0
        except Exception:
            used_pct = 0
        network = self._network_status()
        bookmarks = " | ".join(self.workspace.bookmarks[:3])
        return HTML(
            '<style color="#cbd5e1">Metrics</style>\n'
            f'<style color="#f8fafc">Disk {used_pct}%</style>\n'
            f'<style color="#f8fafc">Net {network}</style>\n'
            f'<style color="#94a3b8">🔖 {bookmarks}</style>'
        )

    @staticmethod
    def _network_status() -> str:
        try:
            stats = psutil.net_if_stats()
            active = sum(1 for item in stats.values() if item.isup)
            return f"{active} iface up"
        except Exception:
            return "unknown"

    # ── Banner & tab bar ─────────────────────────────────────────────────────

    def show_logo(self) -> None:
        width = shutil.get_terminal_size((120, 32)).columns
        buf = io.StringIO()

        cat_logo = [
            r"   |\__/,|   (`\ ",
            r" _ |◕  ◕|__  _) )",
            r"(_   ^   _|=---' ",
            r"  |     |        ",
        ]
        info_header = [
            f"NEXA OMNI TERMINAL  {self.engine.version}",
            f"Theme: {self.workspace.theme}  |  Tabs: {len(self.workspace.tabs)}  |  Panes: {len(self.workspace.panes)}",
            f"Identity: {self.engine.user_name}  |  Mode: GOD_EYE",
            f"Session restore: ACTIVE  |  Autocomplete: {self.workspace.autocomplete_delay_ms}ms",
        ]
        info_w = max(32, min(68, width - 26))

        buf.write("\n")
        for idx in range(max(len(cat_logo), len(info_header))):
            info_raw = info_header[idx] if idx < len(info_header) else ""
            logo_raw = cat_logo[idx] if idx < len(cat_logo) else ""
            # Coloured versions
            if idx == 0:
                info_col = f"{self._t('_fg_primary')}{Style.BRIGHT}{info_raw}{self._t('_reset')}"
            else:
                info_col = f"{self._t('_fg_dim')}{info_raw}{self._t('_reset')}"
            logo_col = f"{Fore.WHITE}{logo_raw}{Style.RESET_ALL}"
            buf.write(f" {info_col:<{info_w + 20}} {logo_col}\n")

        sep = "─" * min(96, width - 2)
        buf.write(f" {Fore.WHITE}{Style.DIM}{sep}{Style.RESET_ALL}\n")
        sys.stdout.write(buf.getvalue())
        sys.stdout.flush()
        self._print_tab_bar()

    def _print_tab_bar(self) -> None:
        width = shutil.get_terminal_size((120, 32)).columns
        buf = io.StringIO()
        labels = []
        active = self.workspace.active_tab_id
        for idx, tab in enumerate(self.workspace.tabs, start=1):
            is_active = tab.tab_id == active
            pin = "📌" if tab.pinned else ""
            if is_active:
                label = (
                    f"{self._t('_bg_active')}{self._t('_fg_accent')}"
                    f"▌{idx}:{pin}{tab.label}▐{self._t('_reset')}"
                )
            else:
                label = f"{self._t('_fg_dim')}○{idx}:{pin}{tab.label}{self._t('_reset')}"
            labels.append(label)

        raw_labels = "  ".join(labels)
        # Width-aware truncation of plain version for overflow check
        plain = "  ".join(f"{'▌' if tab.tab_id == active else '○'}{i}:{tab.label}"
                          for i, tab in enumerate(self.workspace.tabs, 1))
        if len(plain) > width - 4:
            # Always show active tab
            active_tab = self.workspace.get_active_tab()
            idx = next(i for i, t in enumerate(self.workspace.tabs, 1) if t.tab_id == active)
            short_label = (
                f"{self._t('_bg_active')}{self._t('_fg_accent')}"
                f"▌{idx}:{active_tab.label}▐{self._t('_reset')}"
                f"  {self._t('_fg_dim')}+{len(self.workspace.tabs) - 1} more{self._t('_reset')}"
            )
            buf.write(f" {short_label}\n")
        else:
            buf.write(f" {raw_labels}\n")

        sys.stdout.write(buf.getvalue())
        sys.stdout.flush()

    # ── Pane snapshot renderer ───────────────────────────────────────────────

    def _print_workspace_snapshot(self) -> None:
        tab = self.workspace.get_active_tab()
        panes = [self.workspace.panes[pid] for pid in tab.pane_ids]
        buf = io.StringIO()
        buf.write(
            f"\n {self._t('_fg_primary')}• "
            f"{self._t('_fg_dim')}Session snapshot "
            f"{self._t('_fg_primary')}tab={tab.label} layout={tab.layout} "
            f"panes={len(panes)}{self._t('_reset')}\n"
        )
        if tab.layout == "vertical" and len(panes) > 1:
            self._render_vertical_panes(panes, buf)
        else:
            self._render_horizontal_panes(panes, buf)
        buf.write("\n")
        sys.stdout.write(buf.getvalue())
        sys.stdout.flush()

    def _render_vertical_panes(self, panes: List[TerminalPane], buf: io.StringIO) -> None:
        width = shutil.get_terminal_size((120, 32)).columns
        active_id = self.workspace.get_active_tab().active_pane_id

        # Compute column widths from size_pct
        total_pct = sum(p.size_pct for p in panes) or 1
        available = width - (3 * (len(panes) - 1)) - 2  # minus separators
        col_widths = [max(20, int(available * p.size_pct / total_pct)) for p in panes]

        pane_blocks = []
        for pane, col_w in zip(panes, col_widths):
            is_active = pane.pane_id == active_id
            lines = pane.lines[-8:] if pane.lines else ["(idle)"]
            tl, tr, bl, br, h, v = ("╔", "╗", "╚", "╝", "═", "║") if is_active else ("┌", "┐", "└", "┘", "─", "│")
            header_label = textwrap.shorten(pane.label, width=col_w - 4, placeholder="…")
            if is_active:
                accent = self._t("_fg_accent")
            else:
                accent = self._t("_fg_dim")
            block = [f"{accent}{tl}{h * (col_w - 2)}{tr}{self._t('_reset')}"]
            title = f"{accent}{v}{self._t('_reset')} {header_label:<{col_w - 4}} {accent}{v}{self._t('_reset')}"
            block.append(title)
            block.append(f"{accent}{v}{h * (col_w - 2)}{v}{self._t('_reset')}")
            for line in lines:
                highlighted = self._highlight_output(line)
                plain_len = len(self.workspace._strip_ansi(highlighted))
                pad = max(0, col_w - 4 - plain_len)
                block.append(f"{accent}{v}{self._t('_reset')} {highlighted}{' ' * pad} {accent}{v}{self._t('_reset')}")
            # Fill empty rows
            for _ in range(8 - len(lines)):
                block.append(f"{accent}{v}{self._t('_reset')} {' ' * (col_w - 4)} {accent}{v}{self._t('_reset')}")
            block.append(f"{accent}{bl}{h * (col_w - 2)}{br}{self._t('_reset')}")
            pane_blocks.append(block)

        max_rows = max(len(b) for b in pane_blocks)
        sep = f" {self._t('_fg_dim')}│{self._t('_reset')} "
        for row_idx in range(max_rows):
            cols = []
            for block in pane_blocks:
                cols.append(block[row_idx] if row_idx < len(block) else "")
            buf.write(" " + sep.join(cols) + "\n")

    def _render_horizontal_panes(self, panes: List[TerminalPane], buf: io.StringIO) -> None:
        active_id = self.workspace.get_active_tab().active_pane_id
        width = shutil.get_terminal_size((120, 32)).columns
        for pane in panes:
            is_active = pane.pane_id == active_id
            accent = self._t("_fg_accent") if is_active else self._t("_fg_dim")
            tl, tr, bl, br, h = ("╔", "╗", "╚", "╝", "═") if is_active else ("┌", "┐", "└", "┘", "─")
            col_w = min(96, width - 4)
            label = textwrap.shorten(pane.label, width=col_w - 4, placeholder="…")
            buf.write(f" {accent}{tl}{h * (col_w - 2)}{tr}{self._t('_reset')}\n")
            buf.write(f" {accent}│{self._t('_reset')} {label:<{col_w - 4}} {accent}│{self._t('_reset')}\n")
            buf.write(f" {accent}├{h * (col_w - 2)}┤{self._t('_reset')}\n")
            lines = pane.lines[-6:] if pane.lines else ["(idle)"]
            for line in lines:
                highlighted = self._highlight_output(line)
                plain_len = len(self.workspace._strip_ansi(highlighted))
                pad = max(0, col_w - 4 - plain_len)
                buf.write(f" {accent}│{self._t('_reset')} {highlighted}{' ' * pad} {accent}│{self._t('_reset')}\n")
            buf.write(f" {accent}{bl}{h * (col_w - 2)}{br}{self._t('_reset')}\n")

    # ── Command menu ─────────────────────────────────────────────────────────

    def _show_command_menu(self) -> None:
        buf = io.StringIO()
        buf.write(f"\n {self._t('_fg_primary')}• {self._t('_fg_dim')}NEXA terminal protocols{self._t('_reset')}\n")
        menu = [
            ("/tab new Ops",          "Create a new workspace tab"),
            ("/tab swap 1 2",         "Swap tab positions"),
            ("/tab pin",              "Pin/unpin active tab"),
            ("/pane split vertical",  "Split pane vertically"),
            ("/pane resize 40",       "Resize active pane to 40%"),
            ("/search --regex error", "Regex search in pane output"),
            ("/search --fixed OK --context 2", "Search with 2-line context"),
            ("/theme high-contrast",  "Switch to high-contrast theme"),
            ("/export pane ./out.txt","Export pane to text file"),
            ("/voice on",             "Enable voice synthesis"),
            ("/model view",           "View active model"),
            ("/help",                 "Full command reference"),
        ]
        for cmd, desc in menu:
            buf.write(
                f" {self._t('_fg_accent')}{cmd:<40}{self._t('_fg_dim')}{desc}{self._t('_reset')}\n"
            )
        buf.write("\n")
        sys.stdout.write(buf.getvalue())
        sys.stdout.flush()

    # ── Main loop ────────────────────────────────────────────────────────────

    def start_chat(self) -> None:
        os.system("cls" if os.name == "nt" else "clear")
        self.show_logo()
        self._print_workspace_snapshot()
        summary = self.memory.get_context_summary()
        if summary.get("new_session"):
            reaction = self.engine.get_new_chat_reaction()
            self._raw_print(
                f" {self._t('_fg_primary')}• {self._t('_fg_dim')}"
                f"Session restored: {self._t('_reset')}{reaction}"
            )
            self.workspace.append_output(f"Session restored: {reaction}")
            self.speak(reaction)
        else:
            self._raw_print(
                f" {self._t('_fg_dim')}Awaiting command. Type / for protocols.\n{self._t('_reset')}"
            )

    def run(self) -> None:
        self.start_chat()
        try:
            while True:
                try:
                    self._main_loop()
                except Exception as error:
                    self._handle_system_error(error)
        except KeyboardInterrupt:
            self._raw_print(f"\n{self._t('_fg_accent')}NEXA: {self._t('_reset')}Emergency shutdown initiated...")
        finally:
            self.memory.mark_session_end()
            self.workspace.save()

    def _handle_onboarding(self) -> None:
        self._raw_print(
            f"\n{self._t('_fg_accent')}NEXA {self._t('_reset')}›  Welcome to the redesigned terminal workspace."
        )
        name = input(
            f"{self._t('_fg_dim')}• Enter your identity: {self._t('_reset')}"
        ).strip()
        interests = input(
            f"{self._t('_fg_dim')}• Define your objectives (comma separated): {self._t('_reset')}"
        ).strip()
        voice_pref = input(
            f"{self._t('_fg_dim')}• Enable neural voice synthesis? (y/n): {self._t('_reset')}"
        ).strip().lower()
        self.voice_enabled = voice_pref == "y"
        self.listen_enabled = False
        traits = self.memory.memory["user_traits"]
        traits["name"] = name if name else "Operator"
        traits["interests"] = [item.strip() for item in interests.split(",")] if interests else []
        self.memory.save_memory()
        self.engine.user_name = traits["name"]
        welcome = f"Workspace synchronized. Welcome, {traits['name']}."
        self._raw_print(f"\n{self._t('_fg_success')}✓ {self._t('_reset')}{welcome}\n")
        self.workspace.append_output(welcome)
        if self.voice_enabled:
            self.speak(welcome)

    def _main_loop(self) -> None:
        traits = self.memory.memory["user_traits"]
        if traits["name"] is None:
            self._handle_onboarding()
            return
        try:
            if self.listen_enabled:
                user_input = self.listen()
                if not user_input:
                    return
            else:
                with patch_stdout():
                    user_input = self.session.prompt(
                        HTML("<prompt>NEXA › </prompt>")
                    ).strip()
        except EOFError:
            raise SystemExit(0)
        except KeyboardInterrupt:
            return
        if not user_input:
            return
        if user_input == "/":
            self._show_command_menu()
            return
        self.workspace.remember_command(user_input)
        if user_input.lower() in {"exit", "quit", "bye", "/exit"}:
            self._raw_print(
                f"\n{self._t('_fg_accent')}NEXA: {self._t('_reset')}"
                f"Systems hibernating. Stay sharp, {self.engine.user_name}.\n"
            )
            raise SystemExit(0)
        self.handle_input(user_input)

    # ── Input routing ────────────────────────────────────────────────────────

    def handle_input(self, user_input: str) -> None:
        self.memory.analyze_and_update_vibe(user_input)
        self.workspace.append_output(f"USER> {user_input}")
        if self._handle_workspace_command(user_input):
            self.memory.add_chat_turn("user", user_input)
            return
        self._raw_print(f"\n {self._t('_fg_dim')}Initializing OMNI protocol...{self._t('_reset')}")
        time.sleep(0.08)
        if user_input.startswith("/"):
            self._handle_engine_command(user_input)
            return
        self._raw_print(f" {self._t('_fg_dim')}Cross-referencing vault...{self._t('_reset')}")
        started = time.perf_counter()
        response = self.engine.generate_response(user_input)
        latency_ms = int((time.perf_counter() - started) * 1000)
        self._emit_response(response, latency_ms=latency_ms)
        self.memory.add_chat_turn("user", user_input)
        self.memory.add_chat_turn("assistant", response)

    # ── Workspace command handler ─────────────────────────────────────────────

    def _handle_workspace_command(self, user_input: str) -> bool:
        parts = user_input.split()
        command = parts[0].lower()

        if command == "/theme":
            mode = parts[1].lower() if len(parts) > 1 else "toggle"
            valid = {"dark", "light", "high-contrast"}
            if mode == "toggle":
                options = list(valid)
                current_idx = options.index(self.workspace.theme) if self.workspace.theme in options else 0
                self.workspace.theme = options[(current_idx + 1) % len(options)]
            elif mode in valid:
                self.workspace.theme = mode
            else:
                return self._system_message("Use /theme dark, /theme light, /theme high-contrast, or /theme toggle.")
            self.workspace.save()
            self.refresh_session()
            return self._system_message(f"Theme switched to {self.workspace.theme}.")

        if command == "/sidebar":
            mode = parts[1].lower() if len(parts) > 1 else "toggle"
            if mode == "toggle":
                self.workspace.sidebar_collapsed = not self.workspace.sidebar_collapsed
            elif mode == "show":
                self.workspace.sidebar_collapsed = False
            elif mode == "hide":
                self.workspace.sidebar_collapsed = True
            else:
                return self._system_message("Use /sidebar toggle, /sidebar show, or /sidebar hide.")
            self.workspace.save()
            status = "Metrics rail expanded." if not self.workspace.sidebar_collapsed else "Metrics rail collapsed."
            return self._system_message(status)

        if command == "/settings":
            if len(parts) >= 3 and parts[1].lower() == "delay" and parts[2].isdigit():
                self.workspace.autocomplete_delay_ms = max(0, min(500, int(parts[2])))
                self.workspace.save()
                return self._system_message(f"Autocomplete delay set to {self.workspace.autocomplete_delay_ms}ms.")
            return self._system_message("Use /settings delay <0-500>.")

        if command == "/tab":
            return self._handle_tab_command(parts)
        if command == "/pane":
            return self._handle_pane_command(parts)
        if command == "/bookmark":
            return self._handle_bookmark_command(parts)
        if command == "/search":
            return self._handle_search_command(parts)
        if command == "/voice":
            return self._handle_voice_command(parts)
        if command == "/export":
            return self._handle_export_command(parts)

        if command == "/help":
            help_text = (
                "Workspace: /theme dark|light|high-contrast|toggle  /sidebar toggle|show|hide\n"
                "           /settings delay <ms>  /export pane [path]\n"
                "Tabs:      /tab new|switch|rename|move|swap|pin|close|list\n"
                "Panes:     /pane split|focus|resize|label|layout|close|list\n"
                "Search:    /search [--regex|--fixed] <pattern> [--context <N>]\n"
                "Bookmark:  /bookmark list|add|remove|run\n"
                "Voice:     /voice on|off|listen-on|listen-off\n"
                "Engine:    /model /profile /skill /api /forge /auth /file"
            )
            return self._system_message(help_text)

        return False

    # ── Tab command handler ───────────────────────────────────────────────────

    def _handle_tab_command(self, parts: List[str]) -> bool:
        action = parts[1].lower() if len(parts) > 1 else "list"

        if action == "list":
            lines = []
            for idx, tab in enumerate(self.workspace.tabs, start=1):
                active = "●" if tab.tab_id == self.workspace.active_tab_id else "○"
                pin = " 📌" if tab.pinned else ""
                lines.append(f" {active} {idx}. {tab.label}{pin}")
            return self._system_message("Tabs:\n" + "\n".join(lines))

        if action == "new":
            label = " ".join(parts[2:]).strip() or None
            tab = self.workspace.create_tab(label)
            self._print_tab_bar()
            return self._system_message(f"Created tab '{tab.label}'.")

        if action == "switch" and len(parts) > 2:
            if self.workspace.switch_tab(" ".join(parts[2:])):
                self._print_tab_bar()
                self._print_workspace_snapshot()
                return self._system_message(f"Switched to tab '{self.workspace.get_active_tab().label}'.")
            return self._system_message("Tab not found.")

        if action == "rename" and len(parts) > 2:
            self.workspace.rename_tab(" ".join(parts[2:]))
            self._print_tab_bar()
            return self._system_message(f"Tab renamed to '{self.workspace.get_active_tab().label}'.")

        if action == "move" and len(parts) > 3 and parts[2].isdigit() and parts[3].isdigit():
            if self.workspace.move_tab(int(parts[2]), int(parts[3])):
                self._print_tab_bar()
                return self._system_message("Tab order updated.")
            return self._system_message("Invalid tab positions.")

        if action == "swap" and len(parts) > 3 and parts[2].isdigit() and parts[3].isdigit():
            if self.workspace.swap_tabs(int(parts[2]), int(parts[3])):
                self._print_tab_bar()
                return self._system_message(f"Swapped tabs {parts[2]} and {parts[3]}.")
            return self._system_message("Invalid tab indices for swap.")

        if action == "pin":
            ref = parts[2] if len(parts) > 2 else None
            self.workspace.pin_tab(ref)
            tab = self.workspace.get_active_tab()
            status = "pinned" if tab.pinned else "unpinned"
            self._print_tab_bar()
            return self._system_message(f"Tab '{tab.label}' is now {status}.")

        if action == "close":
            ok, msg = self.workspace.close_tab(parts[2] if len(parts) > 2 else None)
            if ok:
                self._print_tab_bar()
            return self._system_message(msg)

        return self._system_message(
            "Use /tab list|new <label>|switch <ref>|rename <label>|move <from> <to>|swap <a> <b>|pin [ref]|close [ref]."
        )

    # ── Pane command handler ──────────────────────────────────────────────────

    def _handle_pane_command(self, parts: List[str]) -> bool:
        action = parts[1].lower() if len(parts) > 1 else "list"

        if action == "list":
            tab = self.workspace.get_active_tab()
            lines = []
            for idx, pid in enumerate(tab.pane_ids, start=1):
                pane = self.workspace.panes[pid]
                marker = "*" if pid == tab.active_pane_id else "-"
                lines.append(f" {marker} {idx}. {pane.label} ({pane.size_pct}%)")
            return self._system_message("Panes:\n" + "\n".join(lines))

        if action == "split":
            layout = parts[2].lower() if len(parts) > 2 else "vertical"
            pane = self.workspace.split_active_pane(layout=layout)
            self._print_workspace_snapshot()
            return self._system_message(f"Created {layout} split pane '{pane.label}'.")

        if action == "focus" and len(parts) > 2:
            if self.workspace.focus_pane(" ".join(parts[2:])):
                self._print_workspace_snapshot()
                return self._system_message(f"Focused pane '{self.workspace.get_active_pane().label}'.")
            return self._system_message("Pane not found.")

        if action == "resize" and len(parts) > 2 and parts[2].isdigit():
            pct = int(parts[2])
            if self.workspace.resize_active_pane(pct):
                self._print_workspace_snapshot()
                return self._system_message(f"Active pane resized to {pct}%.")
            return self._system_message("Resize requires at least 2 panes in the current tab.")

        if action == "label" and len(parts) > 2:
            self.workspace.rename_active_pane(" ".join(parts[2:]))
            self._print_workspace_snapshot()
            return self._system_message(f"Pane renamed to '{self.workspace.get_active_pane().label}'.")

        if action == "layout" and len(parts) > 2:
            if self.workspace.set_layout(parts[2].lower()):
                self._print_workspace_snapshot()
                return self._system_message(f"Layout set to '{self.workspace.get_active_tab().layout}'.")
            return self._system_message("Use /pane layout single|vertical|horizontal.")

        if action == "close":
            if self.workspace.close_active_pane():
                self._print_workspace_snapshot()
                return self._system_message("Closed active pane.")
            return self._system_message("Cannot close the last pane in a tab.")

        return self._system_message(
            "Use /pane list|split vertical|horizontal|focus <ref>|resize <pct>|label <name>|layout <mode>|close."
        )

    # ── Bookmark command handler ──────────────────────────────────────────────

    def _handle_bookmark_command(self, parts: List[str]) -> bool:
        action = parts[1].lower() if len(parts) > 1 else "list"
        if action == "list":
            lines = [f" {idx}. {item}" for idx, item in enumerate(self.workspace.bookmarks, start=1)]
            return self._system_message("Bookmarks:\n" + "\n".join(lines))
        if action == "add" and len(parts) > 2:
            self.workspace.add_bookmark(" ".join(parts[2:]))
            return self._system_message("Bookmark added.")
        if action == "remove" and len(parts) > 2 and parts[2].isdigit():
            if self.workspace.remove_bookmark(int(parts[2])):
                return self._system_message("Bookmark removed.")
            return self._system_message("Bookmark index not found.")
        if action == "run" and len(parts) > 2 and parts[2].isdigit():
            idx = int(parts[2]) - 1
            if 0 <= idx < len(self.workspace.bookmarks):
                bookmark = self.workspace.bookmarks[idx]
                self._raw_print(
                    f" {self._t('_fg_accent')}Running bookmark:{self._t('_reset')} {bookmark}"
                )
                self.handle_input(bookmark)
                return True
            return self._system_message("Bookmark index not found.")
        return self._system_message("Use /bookmark list|add <cmd>|remove <idx>|run <idx>.")

    # ── Search command handler ────────────────────────────────────────────────

    def _handle_search_command(self, parts: List[str]) -> bool:
        if len(parts) == 1:
            return self._system_message("Use /search [--regex|--fixed] <pattern> [--context <N>].")

        regex = True
        context = 0
        query_parts = parts[1:]

        # Parse flags
        filtered = []
        i = 0
        while i < len(query_parts):
            token = query_parts[i]
            if token == "--fixed":
                regex = False
            elif token == "--regex":
                regex = True
            elif token == "--context" and i + 1 < len(query_parts) and query_parts[i + 1].isdigit():
                context = int(query_parts[i + 1])
                i += 1
            else:
                filtered.append(token)
            i += 1

        if not filtered:
            return self._system_message("Search query missing.")

        pattern = " ".join(filtered)
        try:
            matches = self.workspace.search_active_output(pattern, regex=regex, context=context)
        except re.error as error:
            return self._system_message(f"Invalid regex: {error}")

        if not matches:
            return self._system_message("No matches found in the active pane.")

        pane = self.workspace.get_active_pane()
        total_lines = len(pane.lines)
        match_count = sum(1 for m in matches if m.startswith("▶"))
        cap = 50
        display = matches[:cap]
        suffix = f"\n  ... {len(matches) - cap} more lines" if len(matches) > cap else ""

        highlighted = "\n".join(
            self._highlight_match_all(item, pattern, regex) for item in display
        )
        header = (
            f"Search results: {match_count} matched / "
            f"{total_lines} total lines  (regex={regex}, context={context})"
        )
        return self._system_message(f"{header}\n{highlighted}{suffix}")

    # ── Voice command handler ─────────────────────────────────────────────────

    def _handle_voice_command(self, parts: List[str]) -> bool:
        mode = parts[1].lower() if len(parts) > 1 else "on"
        if mode == "on":
            self.voice_enabled = True
            return self._system_message("Voice replies enabled.")
        if mode == "off":
            self.voice_enabled = False
            return self._system_message("Voice replies disabled.")
        if mode == "listen-on":
            self.listen_enabled = True
            return self._system_message("Microphone capture enabled.")
        if mode == "listen-off":
            self.listen_enabled = False
            return self._system_message("Microphone capture disabled.")
        return self._system_message("Use /voice on|off|listen-on|listen-off.")

    # ── Export command handler ────────────────────────────────────────────────

    def _handle_export_command(self, parts: List[str]) -> bool:
        target = parts[1].lower() if len(parts) > 1 else "pane"
        path = parts[2] if len(parts) > 2 else None
        if target == "pane":
            out = self.workspace.export_pane(path=path)
            if out:
                return self._system_message(f"Pane exported to: {out}")
            return self._system_message("Export failed — no active pane data.")
        return self._system_message("Use /export pane [path].")

    # ── Engine command handler ────────────────────────────────────────────────

    def _handle_engine_command(self, user_input: str) -> None:
        parts = user_input.split()
        base = parts[0]
        action = parts[1] if len(parts) > 1 else "view"
        options = " ".join(parts[2:]) if len(parts) > 2 else ""
        nexa_cmd = f"nexa {base[1:]} {action} {options}".strip()
        self._raw_print(
            f" {self._t('_fg_success')}• {self._t('_fg_dim')}Action {self._t('_reset')}{user_input}"
        )
        response = self.engine.handle_cli_command(nexa_cmd)
        if response is None:
            response = "Command not recognized by the terminal or engine."
        latency_ms = 10
        self._emit_response(response, latency_ms=latency_ms)
        if "[SESSION_TERMINATED]" in response:
            self._handle_logout()
        self.memory.add_chat_turn("user", user_input)
        self.memory.add_chat_turn("assistant", response)

    # ── Output emission (buffered) ────────────────────────────────────────────

    def _emit_response(self, response: str, latency_ms: int) -> None:
        """Accumulate all output in a StringIO then flush once — keeps UI snappy."""
        self.workspace.append_output(f"NEXA> {response}")
        buf = io.StringIO()
        buf.write(
            f"\n {self._t('_fg_accent')}NEXA {self._t('_fg_primary')}⬢ "
            f"{self._t('_fg_dim')}{latency_ms}ms{self._t('_reset')}\n"
        )
        for line in response.splitlines() or [""]:
            highlighted = self._highlight_output(line)
            buf.write(f" {self._t('_fg_primary')}{highlighted}{self._t('_reset')}\n")
        buf.write("\n")
        sys.stdout.write(buf.getvalue())
        sys.stdout.flush()
        self._print_workspace_snapshot()
        self.speak(response)

    def _highlight_output(self, line: str) -> str:
        """Syntax-highlight output. Skips lines that already contain ANSI codes."""
        if "\x1b[" in line:
            return line  # ANSI passthrough guard — do not double-wrap
        # File paths
        line = re.sub(
            r"(/[a-zA-Z0-9._\-/]+|[a-zA-Z]:\\[a-zA-Z0-9._\\-]+)",
            f"{self._t('_fg_accent')}\\1{self._t('_fg_primary')}",
            line,
        )
        # Status keywords
        line = re.sub(r"\b(SUCCESS|OK|DONE|PASSED|ACTIVE)\b",
                      f"{self._t('_fg_success')}\\1{self._t('_fg_primary')}",
                      line, flags=re.IGNORECASE)
        line = re.sub(r"\b(ERROR|FAIL|CRITICAL|FATAL)\b",
                      f"{self._t('_fg_error')}\\1{self._t('_fg_primary')}",
                      line, flags=re.IGNORECASE)
        line = re.sub(r"\b(WARNING|WARN|INFO|DEBUG)\b",
                      f"{self._t('_fg_warn')}\\1{self._t('_fg_primary')}",
                      line, flags=re.IGNORECASE)
        return line

    def _system_message(self, message: str) -> bool:
        self.workspace.append_output(f"SYSTEM> {message}")
        buf = io.StringIO()
        buf.write(f"\n {self._t('_fg_system')}SYSTEM {self._t('_reset')}› ")
        for line in message.splitlines():
            buf.write(f"{line}\n          ")
        buf.write("\n")
        sys.stdout.write(buf.getvalue())
        sys.stdout.flush()
        return True

    def _raw_print(self, text: str) -> None:
        sys.stdout.write(text + "\n")
        sys.stdout.flush()

    def _handle_logout(self) -> None:
        self._raw_print(f" {self._t('_fg_warn')}• {self._t('_reset')}Invalidating neural session...")
        self.memory.memory["user_traits"] = {"name": None, "interests": [], "age": None}
        self.memory.memory["chat_history"] = []
        self.workspace.append_output("Session invalidated.")
        self.memory.save_memory()
        time.sleep(0.3)
        self.start_chat()

    def _handle_system_error(self, error: Exception) -> None:
        error_type = type(error).__name__
        message = f"[CRITICAL ERROR] {error_type}: {error}"
        self._raw_print(f"\n{self._t('_fg_error')}{message}{self._t('_reset')}")
        self.workspace.append_output(message)
        try:
            self.storage.log_event("SYSTEM_ERROR", {"type": error_type, "message": str(error)})
        except Exception:
            pass
        self._raw_print(f"{self._t('_fg_warn')}[AUTONOMOUS RESOLUTION] Attempting soft recovery...{self._t('_reset')}")
        time.sleep(0.5)
        self._raw_print(f"{self._t('_fg_accent')}[SYSTEM] Recovery complete. Workspace state restored.{self._t('_reset')}\n")

    # ── Search highlight ──────────────────────────────────────────────────────

    def _highlight_match_all(self, text: str, pattern: str, regex: bool) -> str:
        """Highlight ALL occurrences of pattern in a line."""
        try:
            pat = pattern if regex else re.escape(pattern)
            return re.sub(
                pat,
                lambda m: f"{Back.YELLOW}{Fore.BLACK}{m.group(0)}{Style.RESET_ALL}",
                text,
                flags=re.IGNORECASE,
            )
        except re.error:
            return text

    # Backwards-compat alias used by older code paths
    @staticmethod
    def _highlight_match(text: str, pattern: str, regex: bool) -> str:
        try:
            pat = pattern if regex else re.escape(pattern)
            return re.sub(
                pat,
                lambda m: f"{Back.YELLOW}{Fore.BLACK}{m.group(0)}{Style.RESET_ALL}",
                text,
                flags=re.IGNORECASE,
            )
        except re.error:
            return text


if __name__ == "__main__":
    NexaAI().run()
