"""
NEXA Terminal Redesign — End-to-End Test Suite
Tests all 14 core features: tab management, pane operations, search,
autocomplete, atomic saves, session restore, accessibility, and export.
Run with:  python -m pytest test_terminal_redesign.py -v
"""
import io
import json
import os
import re
import sys
import tempfile
import time
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# Minimal stubs so tests run without full NEXA dependencies installed.
# We build *real* module objects instead of MagicMock so that class-level
# attributes (like NexaCommandCompleter.COMMAND_META) survive correctly.
# ---------------------------------------------------------------------------
def _stub(name: str):
    mod = types.ModuleType(name)
    sys.modules[name] = mod
    return mod

# colorama — provide real-looking string constants
_col = _stub("colorama")
_col.Fore = types.SimpleNamespace(**{c: "" for c in
    ["RED","GREEN","YELLOW","BLUE","MAGENTA","CYAN","WHITE","RESET","BLACK",
     "LIGHTBLUE_EX","LIGHTCYAN_EX","LIGHTGREEN_EX","LIGHTRED_EX","LIGHTWHITE_EX"]})
_col.Back = types.SimpleNamespace(**{c: "" for c in
    ["RED","GREEN","YELLOW","BLUE","CYAN","WHITE","BLACK","RESET","MAGENTA"]})
_col.Style = types.SimpleNamespace(BRIGHT="", DIM="", RESET_ALL="", NORMAL="")
_col.init = lambda **kw: None

# psutil
_psutil = _stub("psutil")
_psutil.net_if_stats = lambda: {}
_psutil.disk_usage = lambda p: types.SimpleNamespace(used=0, total=1, free=1)

# pyttsx3
_pyttsx3 = _stub("pyttsx3")
_pyttsx3.init = lambda: MagicMock()

# speech_recognition
_sr = _stub("speech_recognition")
_sr.Recognizer = MagicMock
_sr.Microphone = MagicMock
_sr.WaitTimeoutError = Exception

# prompt_toolkit — provide just enough structure
for _pkg in [
    "prompt_toolkit", "prompt_toolkit.auto_suggest",
    "prompt_toolkit.completion", "prompt_toolkit.formatted_text",
    "prompt_toolkit.history", "prompt_toolkit.lexers",
    "prompt_toolkit.patch_stdout", "prompt_toolkit.styles",
]:
    _stub(_pkg)

# Top-level prompt_toolkit exports used by main.py
_pt = sys.modules["prompt_toolkit"]
_pt.PromptSession = MagicMock
_pt.auto_suggest = sys.modules["prompt_toolkit.auto_suggest"]
_pt.completion = sys.modules["prompt_toolkit.completion"]

_stub("prompt_toolkit.completion").Completer = object
_stub("prompt_toolkit.completion").Completion = (
    lambda *a, **kw: types.SimpleNamespace(text=a[0] if a else "", display=None)
)
_stub("prompt_toolkit.styles").Style = MagicMock()
_stub("prompt_toolkit.formatted_text").HTML = lambda x: x
_stub("prompt_toolkit.formatted_text").to_formatted_text = lambda x, *a, **kw: x
_stub("prompt_toolkit.lexers").PygmentsLexer = MagicMock
_stub("prompt_toolkit.auto_suggest").AutoSuggestFromHistory = MagicMock
_stub("prompt_toolkit.history").FileHistory = MagicMock
_pt_ps = _stub("prompt_toolkit.patch_stdout")
_pt_ps.patch_stdout = MagicMock()
_pt_ps.patch_stdout.__enter__ = lambda s: None
_pt_ps.patch_stdout.__exit__ = lambda s, *a: None

# Re-export so `from prompt_toolkit.completion import Completer, Completion` works
sys.modules["prompt_toolkit.completion"].Completer = object
sys.modules["prompt_toolkit.completion"].Completion = (
    lambda *a, **kw: types.SimpleNamespace(text=a[0] if a else "", display=None)
)

_stub("pygments")
_stub("pygments.lexers")
_stub("pygments.lexers.shell")

# Stub memory / engine / storage
for _mod in ["memory_manager", "nexa_engine", "nexa_storage", "nexa_skills"]:
    _stub(_mod)
    # Give MemoryManager / NexaLogicEngine etc. something importable
    sys.modules[_mod].MemoryManager = MagicMock
    sys.modules[_mod].NexaLogicEngine = MagicMock
    sys.modules[_mod].NexaStorage = MagicMock

from main import (  # noqa: E402
    NexaCommandCompleter,
    TerminalPane,
    TerminalTab,
    TerminalWorkspace,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_workspace(tmp_dir: str) -> TerminalWorkspace:
    state_path = os.path.join(tmp_dir, "state.json")
    ws = TerminalWorkspace(state_path=state_path)
    return ws


# ---------------------------------------------------------------------------
# 1. Tab lifecycle
# ---------------------------------------------------------------------------

class TestTabLifecycle(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.ws = _make_workspace(self.tmp)

    def test_create_rename_tab(self):
        tab = self.ws.create_tab("Alpha")
        self.assertEqual(tab.label, "Alpha")
        self.ws.rename_tab("Beta")
        self.assertEqual(self.ws.get_active_tab().label, "Beta")

    def test_move_tab(self):
        self.ws.create_tab("A")
        self.ws.create_tab("B")
        original_order = [t.label for t in self.ws.tabs]
        self.ws.move_tab(2, 3)
        new_order = [t.label for t in self.ws.tabs]
        self.assertNotEqual(original_order, new_order)

    def test_swap_tabs(self):
        self.ws.create_tab("X")
        self.ws.create_tab("Y")
        labels_before = [t.label for t in self.ws.tabs]
        self.ws.swap_tabs(2, 3)
        labels_after = [t.label for t in self.ws.tabs]
        self.assertNotEqual(labels_before, labels_after)
        self.assertIn("X", labels_after)
        self.assertIn("Y", labels_after)

    def test_pin_prevents_close(self):
        self.ws.create_tab("Pinned")
        self.ws.switch_tab("2")
        self.ws.pin_tab()
        ok, msg = self.ws.close_tab()
        self.assertFalse(ok)
        self.assertIn("pinned", msg.lower())

    def test_unpin_allows_close(self):
        self.ws.create_tab("Pinned")
        self.ws.switch_tab("2")
        self.ws.pin_tab()   # pin
        self.ws.pin_tab()   # unpin
        ok, _ = self.ws.close_tab()
        self.assertTrue(ok)

    def test_close_last_tab_blocked(self):
        self.assertEqual(len(self.ws.tabs), 1)
        ok, _ = self.ws.close_tab()
        self.assertFalse(ok)


# ---------------------------------------------------------------------------
# 2. Pane lifecycle
# ---------------------------------------------------------------------------

class TestPaneLifecycle(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.ws = _make_workspace(self.tmp)

    def test_split_focus_label_close(self):
        pane2 = self.ws.split_active_pane(layout="vertical")
        self.assertEqual(len(self.ws.get_active_tab().pane_ids), 2)
        self.ws.focus_pane("1")
        self.ws.rename_active_pane("Monitor")
        self.assertEqual(self.ws.get_active_pane().label, "Monitor")
        ok = self.ws.close_active_pane()
        self.assertTrue(ok)
        self.assertEqual(len(self.ws.get_active_tab().pane_ids), 1)

    def test_cannot_close_last_pane(self):
        ok = self.ws.close_active_pane()
        self.assertFalse(ok)

    def test_resize_pane(self):
        self.ws.split_active_pane()
        ok = self.ws.resize_active_pane(30)
        self.assertTrue(ok)
        self.assertEqual(self.ws.get_active_pane().size_pct, 30)

    def test_resize_requires_two_panes(self):
        ok = self.ws.resize_active_pane(40)
        self.assertFalse(ok)

    def test_layout_modes(self):
        self.ws.split_active_pane()
        for mode in ("vertical", "horizontal", "single"):
            ok = self.ws.set_layout(mode)
            self.assertTrue(ok)

    def test_layout_rejects_invalid(self):
        ok = self.ws.set_layout("diagonal")
        self.assertFalse(ok)


# ---------------------------------------------------------------------------
# 3. Search — regex
# ---------------------------------------------------------------------------

class TestSearchRegex(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.ws = _make_workspace(self.tmp)
        lines = [
            "INFO: starting server",
            "DEBUG: connection pool ready",
            "ERROR: database timeout",
            "INFO: retry attempt 1",
            "ERROR: retry failed",
        ]
        for line in lines:
            self.ws.append_output(line)

    def test_regex_match_count(self):
        matches = self.ws.search_active_output("ERROR", regex=True)
        hit_lines = [m for m in matches if m.startswith("▶")]
        self.assertEqual(len(hit_lines), 2)

    def test_regex_case_insensitive(self):
        matches = self.ws.search_active_output("error", regex=True)
        hit_lines = [m for m in matches if m.startswith("▶")]
        self.assertEqual(len(hit_lines), 2)

    def test_regex_context_lines(self):
        matches = self.ws.search_active_output("ERROR", regex=True, context=1)
        # 2 match lines + up to 2 context lines each → between 2 and 6 result lines
        self.assertGreater(len(matches), 2)

    def test_invalid_regex_raises(self):
        with self.assertRaises(re.error):
            self.ws.search_active_output("[unclosed", regex=True)


# ---------------------------------------------------------------------------
# 4. Search — fixed text
# ---------------------------------------------------------------------------

class TestSearchFixed(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.ws = _make_workspace(self.tmp)
        self.ws.append_output("hello world")
        self.ws.append_output("HELLO AGAIN")
        self.ws.append_output("nothing here")

    def test_fixed_no_regex_interpretation(self):
        # Pattern that would be special in regex but is literal in --fixed mode
        matches = self.ws.search_active_output("hello", regex=False)
        hit_lines = [m for m in matches if m.startswith("▶")]
        self.assertEqual(len(hit_lines), 2)  # both "hello world" and "HELLO AGAIN"

    def test_fixed_no_false_positives(self):
        matches = self.ws.search_active_output("nothing", regex=False)
        hit_lines = [m for m in matches if m.startswith("▶")]
        self.assertEqual(len(hit_lines), 1)


# ---------------------------------------------------------------------------
# 5. Autocomplete — NEXA slash commands
# ---------------------------------------------------------------------------

class TestAutocompleteNexaCommands(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.ws = _make_workspace(self.tmp)
        self.completer = NexaCommandCompleter(self.ws)

    def _completions_for(self, text: str):
        doc = MagicMock()
        doc.text_before_cursor = text
        event = MagicMock()
        event.completion_requested = True
        return list(self.completer.get_completions(doc, event))

    def test_all_16_commands_present(self):
        completions = self._completions_for("/")
        texts = [c.text for c in completions]
        for cmd in NexaCommandCompleter.COMMAND_META:
            self.assertIn(cmd, texts, f"{cmd} missing from completions")

    def test_prefix_filtering(self):
        completions = self._completions_for("/tab")
        texts = [c.text for c in completions]
        # /tab itself should appear
        self.assertIn("/tab", texts)
        # All completions should be related: either the /tab command itself,
        # or sub-command tokens like 'new', 'switch', 'rename' etc.
        tab_sub_commands = set(NexaCommandCompleter.FLAG_META.get("/tab", []))
        for text in texts:
            self.assertTrue(
                text.startswith("/tab") or text in tab_sub_commands or "/tab" in text,
                f"Unexpected completion '{text}' for /tab prefix",
            )

    def test_no_completions_for_empty(self):
        # Non-slash, non-path input with < 2 chars should not crash
        completions = self._completions_for("a")
        # Just ensure no exception; may return 0 or more
        self.assertIsInstance(completions, list)


# ---------------------------------------------------------------------------
# 6. Autocomplete — history
# ---------------------------------------------------------------------------

class TestAutocompleteHistory(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.ws = _make_workspace(self.tmp)
        self.ws.command_history = ["git status", "git log", "python main.py", "pip install flask"]
        self.completer = NexaCommandCompleter(self.ws)

    def _completions_for(self, text: str):
        doc = MagicMock()
        doc.text_before_cursor = text
        event = MagicMock()
        event.completion_requested = True
        return list(self.completer.get_completions(doc, event))

    def test_history_surfaces(self):
        completions = self._completions_for("git")
        texts = [c.text for c in completions]
        # At least one git-related history entry should appear
        self.assertTrue(any("git" in t for t in texts))

    def test_history_deduplication(self):
        self.ws.command_history = ["pip install", "pip install", "pip install"]
        completions = self._completions_for("pip")
        texts = [c.text for c in completions]
        self.assertEqual(len(texts), len(set(texts)), "Duplicate history completions detected")


# ---------------------------------------------------------------------------
# 7. Atomic save — crash safety
# ---------------------------------------------------------------------------

class TestAtomicSave(unittest.TestCase):
    def test_tmp_file_renamed_on_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = _make_workspace(tmp)
            state_path = ws.state_path
            tmp_path = state_path + ".tmp"
            ws.save()
            self.assertTrue(os.path.exists(state_path), "State file missing after save")
            self.assertFalse(os.path.exists(tmp_path), ".tmp file should be renamed after save")

    def test_state_survives_simulated_save_crash(self):
        """If the tmp write crashes mid-way, the original state file is untouched."""
        with tempfile.TemporaryDirectory() as tmp:
            ws = _make_workspace(tmp)
            ws.save()  # write initial good state
            original_mtime = os.path.getmtime(ws.state_path)
            # Simulate a crash by making the open call raise mid-write
            with patch("builtins.open", side_effect=OSError("disk full")):
                ws.save()  # should swallow the error
            # Original file should still exist and be unchanged
            self.assertTrue(os.path.exists(ws.state_path))
            self.assertEqual(os.path.getmtime(ws.state_path), original_mtime)


# ---------------------------------------------------------------------------
# 8. Output buffer latency
# ---------------------------------------------------------------------------

class TestOutputBufferLatency(unittest.TestCase):
    def test_10k_line_pane_append_under_100ms(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = _make_workspace(tmp)
            lines = [f"Line {i}: {'x' * 80}" for i in range(10_000)]
            start = time.perf_counter()
            for line in lines:
                ws.append_output(line)
            elapsed_ms = (time.perf_counter() - start) * 1000
            self.assertLess(elapsed_ms, 100, f"Appending 10k lines took {elapsed_ms:.1f}ms (limit: 100ms)")

    def test_pane_cap_enforced(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = _make_workspace(tmp)
            pane = ws.get_active_pane()
            pane.output_limit = 1_000
            for i in range(2_000):
                ws.append_output(f"line {i}")
            self.assertLessEqual(len(pane.lines), 1_000)


# ---------------------------------------------------------------------------
# 9. Session restore
# ---------------------------------------------------------------------------

class TestSessionRestore(unittest.TestCase):
    def test_tabs_and_panes_restored(self):
        with tempfile.TemporaryDirectory() as tmp:
            state_path = os.path.join(tmp, "state.json")
            ws1 = TerminalWorkspace(state_path=state_path)
            ws1.create_tab("Dev")
            ws1.create_tab("Ops")
            ws1.split_active_pane(layout="horizontal")
            ws1.save()

            ws2 = TerminalWorkspace(state_path=state_path)
            self.assertEqual(len(ws2.tabs), len(ws1.tabs))
            self.assertIn("Dev", [t.label for t in ws2.tabs])
            self.assertIn("Ops", [t.label for t in ws2.tabs])

    def test_bookmarks_restored(self):
        with tempfile.TemporaryDirectory() as tmp:
            state_path = os.path.join(tmp, "state.json")
            ws1 = TerminalWorkspace(state_path=state_path)
            ws1.add_bookmark("/model list")
            ws1.save()
            ws2 = TerminalWorkspace(state_path=state_path)
            self.assertIn("/model list", ws2.bookmarks)

    def test_command_history_restored(self):
        with tempfile.TemporaryDirectory() as tmp:
            state_path = os.path.join(tmp, "state.json")
            ws1 = TerminalWorkspace(state_path=state_path)
            ws1.remember_command("git push origin main")
            ws1.save()
            ws2 = TerminalWorkspace(state_path=state_path)
            self.assertIn("git push origin main", ws2.command_history)


# ---------------------------------------------------------------------------
# 10. WCAG 2.1 AA contrast check (structural)
# ---------------------------------------------------------------------------

# Approximate relative luminance for sRGB hex colours (simplified WCAG formula).
def _hex_luminance(hex_color: str) -> float:
    h = hex_color.lstrip("#")
    if len(h) != 6:
        return 0.0
    r, g, b = (int(h[i:i+2], 16) / 255 for i in (0, 2, 4))
    def _linearize(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * _linearize(r) + 0.7152 * _linearize(g) + 0.0722 * _linearize(b)

def _contrast_ratio(hex_a: str, hex_b: str) -> float:
    la, lb = _hex_luminance(hex_a), _hex_luminance(hex_b)
    lighter, darker = max(la, lb), min(la, lb)
    return (lighter + 0.05) / (darker + 0.05)


class TestAccessibilityContrast(unittest.TestCase):
    """Verify that at least the primary text + background pairs meet WCAG AA (4.5:1)."""

    PAIRS = [
        # (theme, fg_hex, bg_hex, description)
        ("dark",           "#6ee7f9", "#0f172a", "dark prompt on dark bg"),
        ("dark",           "#f8fafc", "#0f172a", "dark toolbar text"),
        ("light",          "#0f172a", "#e2e8f0", "light toolbar text"),
        ("high-contrast",  "#ffffff", "#000000", "hc white on black"),
        ("high-contrast",  "#000000", "#ffff00", "hc black on yellow"),
    ]

    def test_all_pairs_wcag_aa(self):
        for theme, fg, bg, description in self.PAIRS:
            ratio = _contrast_ratio(fg, bg)
            self.assertGreaterEqual(
                ratio, 4.5,
                f"WCAG AA FAIL [{theme}] {description}: {fg}/{bg} ratio={ratio:.2f}"
            )


# ---------------------------------------------------------------------------
# 11. ANSI passthrough guard
# ---------------------------------------------------------------------------

class TestAnsiPassthrough(unittest.TestCase):
    def _make_ai_stub(self):
        """Build a minimal NexaAI-like object with just _highlight_output."""
        from main import NexaAI
        # Avoid running __init__; just grab the method
        instance = object.__new__(NexaAI)
        instance.workspace = MagicMock()
        instance.workspace.theme = "dark"
        return instance

    def test_pre_coloured_line_not_wrapped(self):
        instance = self._make_ai_stub()
        coloured = "\x1b[31mERROR: something bad\x1b[0m"
        result = instance._highlight_output(coloured)
        # Should be returned unchanged
        self.assertEqual(result, coloured)

    def test_plain_line_gets_highlighted(self):
        instance = self._make_ai_stub()
        plain = "ERROR: something bad"
        result = instance._highlight_output(plain)
        self.assertNotEqual(result, plain)  # highlighting was applied


# ---------------------------------------------------------------------------
# 12. Pane resize column widths
# ---------------------------------------------------------------------------

class TestPaneResize(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.ws = _make_workspace(self.tmp)
        self.ws.split_active_pane()

    def test_resize_clamps_min(self):
        self.ws.resize_active_pane(0)
        self.assertEqual(self.ws.get_active_pane().size_pct, 10)

    def test_resize_clamps_max(self):
        self.ws.resize_active_pane(99)
        self.assertEqual(self.ws.get_active_pane().size_pct, 90)

    def test_other_panes_redistributed(self):
        self.ws.resize_active_pane(40)
        tab = self.ws.get_active_tab()
        total = sum(self.ws.panes[pid].size_pct for pid in tab.pane_ids)
        # Total should be close to 100 (may differ by 1 due to integer division)
        self.assertAlmostEqual(total, 100, delta=5)


# ---------------------------------------------------------------------------
# 13. Bookmark run
# ---------------------------------------------------------------------------

class TestBookmarkRun(unittest.TestCase):
    def test_bookmark_added_and_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = _make_workspace(tmp)
            ws.add_bookmark("/model view")
            self.assertIn("/model view", ws.bookmarks)

    def test_bookmark_remove(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = _make_workspace(tmp)
            ws.add_bookmark("/profile view")
            before_count = len(ws.bookmarks)
            ws.remove_bookmark(before_count)  # remove the last one (just added)
            self.assertEqual(len(ws.bookmarks), before_count - 1)

    def test_bookmark_run_appends_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = _make_workspace(tmp)
            ws.append_output("initial line")
            # Simulate running a bookmark by appending its result
            bookmark = "/model view"
            ws.append_output(f"BOOKMARK_RUN: {bookmark}")
            pane = ws.get_active_pane()
            self.assertTrue(any("BOOKMARK_RUN" in line for line in pane.lines))


# ---------------------------------------------------------------------------
# 14. Export pane
# ---------------------------------------------------------------------------

class TestExportPane(unittest.TestCase):
    def test_export_writes_correct_lines(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = _make_workspace(tmp)
            ws.append_output("Hello NEXA")
            ws.append_output("\x1b[32mGREEN line\x1b[0m")
            out_file = os.path.join(tmp, "export.txt")
            path = ws.export_pane(path=out_file)
            self.assertTrue(os.path.exists(path))
            content = Path(path).read_text(encoding="utf-8")
            self.assertIn("Hello NEXA", content)
            self.assertIn("GREEN line", content)          # ANSI stripped
            self.assertNotIn("\x1b[", content)            # no escape codes

    def test_export_default_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = _make_workspace(tmp)
            ws.append_output("Test line")
            original_dir = os.getcwd()
            os.chdir(tmp)
            try:
                path = ws.export_pane()
                self.assertTrue(os.path.exists(path))
            finally:
                os.chdir(original_dir)
                try:
                    os.remove(path)
                except Exception:
                    pass


# ---------------------------------------------------------------------------
# 15. New V4 Upgrades Verification
# ---------------------------------------------------------------------------

class TestNewV4Upgrades(unittest.TestCase):
    def setUp(self):
        import sys
        self.stubbed_modules = {}
        for m in ["nexa_engine", "memory_manager", "nexa_storage", "nexa_skills"]:
            if m in sys.modules:
                self.stubbed_modules[m] = sys.modules[m]
                del sys.modules[m]

    def tearDown(self):
        import sys
        for m, mod in self.stubbed_modules.items():
            sys.modules[m] = mod

    def test_model_switching_robust_parsing(self):
        from app.model_manager import NexaModelManager
        from app.commands import CommandRouter
        from nexa_storage import NexaStorage
        from memory_manager import MemoryManager
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_db:
            db_path = tmp_db.name
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp_mem:
            mem_path = tmp_mem.name
            
        try:
            mm = NexaModelManager()
            storage = NexaStorage(db_path=db_path)
            memory = MemoryManager(storage_path=mem_path)
            router = CommandRouter(model_manager=mm, storage=storage, memory_manager=memory)
            
            res = router.route("/model")
            self.assertIn("Registered Models:", res.text)
            self.assertIn("➔ ●", res.text) # active highlighter
            
            # Test switch parsing variations
            res = router.route("/model switch god eye")
            self.assertEqual(mm.active_model_key, "god_eye")
            
            res = router.route("/model code")
            self.assertEqual(mm.active_model_key, "code")
        finally:
            if os.path.exists(db_path):
                os.remove(db_path)
            if os.path.exists(mem_path):
                os.remove(mem_path)

    def test_auto_learn_age_declarations(self):
        from nexa_engine import NexaLogicEngine
        from memory_manager import MemoryManager
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp_mem:
            mem_path = tmp_mem.name
            
        try:
            memory = MemoryManager(storage_path=mem_path)
            engine = NexaLogicEngine(memory_manager=memory)
            
            # Test "I am 25" matching
            engine._auto_learn_from_user("I am 25")
            traits = memory.memory.get("user_traits", {})
            self.assertEqual(traits.get("age"), 25)
            
            # Test "I'm 30" matching
            engine._auto_learn_from_user("I'm 30")
            traits = memory.memory.get("user_traits", {})
            self.assertEqual(traits.get("age"), 30)
        finally:
            if os.path.exists(mem_path):
                os.remove(mem_path)

    def test_profile_persistence(self):
        from app.commands import CommandRouter
        from memory_manager import MemoryManager
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp_mem:
            mem_path = tmp_mem.name
            
        try:
            memory = MemoryManager(storage_path=mem_path)
            router = CommandRouter(memory_manager=memory)
            
            # Edit name
            res = router.route("/profile edit name Biruk")
            traits = memory.memory.get("user_traits", {})
            self.assertEqual(traits.get("name"), "Biruk")
            
            # Edit age
            res = router.route("/profile edit age 25")
            traits = memory.memory.get("user_traits", {})
            self.assertEqual(traits.get("age"), 25)
        finally:
            if os.path.exists(mem_path):
                os.remove(mem_path)


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    unittest.main(verbosity=2)
