# app/ui/chat_ui.py
"""
NEXA v3 Main Textual App Interface.
Ties together UI widgets, animations, voice systems, and backend logic.
"""

from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal, VerticalScroll, Container
from textual.widgets import Label, Input, Button, Static, ProgressBar
from textual.reactive import reactive
from textual.screen import ModalScreen

import sys
import os
import threading
import time
from typing import Dict, Any, List

# Import custom widgets
from app.ui.widgets.model_switcher import ModelSwitcher
from app.ui.widgets.voice_wave import VoiceWave
from app.ui.widgets.xp_bar import XPBar
from app.ui.widgets.chat_bubble import ChatBubble
from app.ui.widgets.status_bar import StatusBar
from app.ui.widgets.command_palette import CommandPalette
from app.ui.widgets.knowledge_bar import KnowledgeBar
from app.ui.widgets.preview_pane import PreviewPane
from app.ui.widgets.minimap import Minimap

# Import animations and themes
from app.ui.themes import NEXA_CSS
from app.ui.animations.cube_3d import Cube3DAnimator
from app.ui.animations.model_switch import get_model_switch_logs
from app.ui.animations.waveform import WaveformVisualizer
from app.ui.animations.particles import LevelUpAnimation

# Import features and commands
from app.themes import TEXTUAL_THEMES
from app.model_manager import NexaModelManager
from app.features.xp import XPManager
from app.features.challenges import ChallengeManager
from app.features.notebook import NotebookManager
from app.commands import CommandRouter
from nexa_storage import NexaStorage
from memory_manager import MemoryManager

# Import engine
from nexa_engine import NexaLogicEngine


class CubeWidget(Static):
    """Sidebar widget rendering the 3D rotating cube."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.animator = Cube3DAnimator(width=28, height=9)
        self.color_ansi = "\033[38;5;220m" # Default gold

    def on_mount(self):
        self.set_interval(0.1, self.update_cube)

    def update_cube(self):
        frame = self.animator.next_frame(color_ansi=self.color_ansi, char="█")
        self.update(frame)

    def set_color(self, ansi_color: str):
        self.color_ansi = ansi_color


class NexaApp(App):
    """Main Textual Application for NEXA v3."""
    
    CSS = NEXA_CSS
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Backend managers
        self.storage = NexaStorage()
        self.memory = MemoryManager()
        self.model_manager = NexaModelManager()
        
        # Sync active model from storage config
        active_model_from_config = self.storage.config.get("settings", {}).get("active_model") or self.storage.config.get("active_model")
        if active_model_from_config:
            self.model_manager.active_model_key = active_model_from_config.lower()
            
        self.xp_manager = XPManager()
        self.challenge_manager = ChallengeManager(self.xp_manager)
        self.notebook_manager = NotebookManager()
        
        # Engine
        self.engine = NexaLogicEngine(
            user_summary=self.memory.get_context_summary(),
            storage=self.storage,
            memory_manager=self.memory
        )
        self.engine.active_model = self.model_manager.active_model_key.upper()
        
        # Command Router
        self.router = CommandRouter(
            model_manager=self.model_manager,
            xp_manager=self.xp_manager,
            challenge_manager=self.challenge_manager,
            notebook_manager=self.notebook_manager,
            storage=self.storage,
            memory_manager=self.memory
        )
        
        # Voice (optional load to prevent blocking)
        self.voice_input = None
        self.voice_output = None
        self.voice_active = False
        self.voice_visualizer = None
        
        # UI State
        self.active_color = "#EAB308" # default gold

        # Autocomplete Predictor & Chat History list
        from app.features.predict import NexaPredict
        self.predictor = NexaPredict()
        self.chat_history_list = []

        # Sync backend engines
        self.engine.kb = self.router.kb
        self.engine.rag = self.router.rag
        self.engine.monitor = self.router.monitor

    def compose(self) -> ComposeResult:
        # Title bar
        with Horizontal(classes="title-bar"):
            yield Label("👑 NEXA INTELLIGENCE HUB v3.0.0", id="app-title")
            
        # Sidebar
        with Vertical(classes="sidebar"):
            yield Label("⚡ ENGAGEMENT METRICS", id="sidebar-section-title")
            self.xp_bar = XPBar()
            yield self.xp_bar
            
            # Streak and Challenge Indicators
            self.streak_label = Label("🔥 Streak: 0 Days")
            self.challenge_label = Label("🎯 Challenge: [UNSOLVED]")
            yield self.streak_label
            yield self.challenge_label
            
            # Bouncing Voice Indicator
            self.voice_wave = VoiceWave()
            yield self.voice_wave

            # Knowledge Base and Live Preview widgets
            self.knowledge_bar = KnowledgeBar()
            self.preview_pane = PreviewPane()
            yield self.knowledge_bar
            yield self.preview_pane
            
            # 3D Cube
            yield Label("\n🧊 NEURAL RESONANCE 3D", id="cube-title")
            self.cube = CubeWidget()
            yield self.cube
            
        # Chat area
        with Horizontal(id="chat-area"):
            with VerticalScroll(id="chat-scroll"):
                self.chat_container = Container(id="chat-container")
                yield self.chat_container
            self.minimap = Minimap()
            yield self.minimap
            
        # Suggestion panel
        with Horizontal(classes="suggest-bar"):
            self.suggest_btn_1 = Button("Explain Folder", classes="suggest-button", id="sug-1")
            self.suggest_btn_2 = Button("Run Challenge", classes="suggest-button", id="sug-2")
            self.suggest_btn_3 = Button("Show Statistics", classes="suggest-button", id="sug-3")
            yield self.suggest_btn_1
            yield self.suggest_btn_2
            yield self.suggest_btn_3

        # Input container
        with Horizontal(id="input-container"):
            self.mic_btn = Button("🎤 Mic", id="mic-toggle", variant="primary")
            self.chat_input = Input(placeholder="Type a message or / for commands...")
            self.send_btn = Button("Send", id="btn-send", variant="success")
            yield self.mic_btn
            yield self.chat_input
            yield self.send_btn
            
        # Status bar
        self.status_bar = StatusBar(active_model_name="ULTRA")
        yield self.status_bar

    def on_mount(self):
        # 1. Update Streak
        self.xp_manager.update_streak()
        
        # 2. Sync UI state
        self.refresh_stats_ui()
        self.sync_model_ui()
        
        # 3. Setup voice system safely in a separate thread
        threading.Thread(target=self._init_voice_system, daemon=True).start()
        
        # 4. Subscribe to model manager changes
        self.model_manager.subscribe_model_switch(self.on_model_switched_event)

        # 5. Welcome message
        name = self.memory.memory.get("user_traits", {}).get("name") or "Human"
        self.append_bot_message(f"Welcome back, {name}! I am NEXA, your personality-driven AI assistant. Feel free to type in natural language or use [bold]/help[/bold] to see slash commands.")

    def _init_voice_system(self):
        try:
            from app.voice.input import NexaVoiceInput
            from app.voice.output import NexaVoiceOutput
            self.voice_input = NexaVoiceInput(use_whisper=False)
            self.voice_output = NexaVoiceOutput()
        except Exception as e:
            pass

    def refresh_stats_ui(self):
        """Pulls latest stats and updates labels."""
        stats = self.xp_manager.stats
        earned, total, pct = self.xp_manager.get_progress_to_next()
        self.xp_bar.update_xp(stats["level"], stats["level_name"], earned, total, pct)
        self.streak_label.update(f"🔥 Daily Streak: [bold]{stats['streak']}[/bold] Days")
        
        # Update challenge status
        active_key = self.model_manager.active_model_key
        challenge = self.challenge_manager.get_challenge(active_key)
        ch_status = "[bold color(#10b981)]SOLVED[/bold color]" if challenge["completed"] else "[bold color(#ef4444)]ACTIVE[/bold color]"
        self.challenge_label.update(f"🎯 Challenge: {ch_status}")

        # Update knowledge stats
        if hasattr(self, "knowledge_bar"):
            kb_stats = self.router.kb.get_stats()
            self.knowledge_bar.facts_count = kb_stats.get("total_facts", 0)
            if kb_stats.get("topics"):
                self.knowledge_bar.top_topic = kb_stats["topics"][0]
            else:
                self.knowledge_bar.top_topic = "none"

        # Check live preview server status on port 7750
        if hasattr(self, "preview_pane"):
            import socket
            is_online = False
            try:
                with socket.create_connection(("127.0.0.1", 7750), timeout=0.1):
                    is_online = True
            except Exception:
                pass
            self.preview_pane.set_status(is_online)

    def sync_model_ui(self):
        """Synchronizes color scheme and theme parameters to the active model."""
        active_key = self.model_manager.active_model_key
        cfg = TEXTUAL_THEMES[active_key]
        self.active_color = cfg["primary"]
        
        # Set border color for sidebar
        self.query_one(".sidebar").styles.border_right = ("tall", self.active_color)
        self.query_one(".title-bar").styles.border_bottom = ("hsolid", self.active_color)
        
        # Set 3D cube color
        # Map keys to ANSI codes
        ansi_colors = {
            "code": "\033[38;5;33m",     # Cyan-Blue
            "design": "\033[38;5;201m",   # Pink-Magenta
            "fix": "\033[38;5;196m",      # Crimson Red
            "ultra": "\033[38;5;220m",    # Gold
            "god_eye": "\033[38;5;120m",  # Emerald Green
            "claude": "\033[38;5;214m"    # Amber/Orange
        }
        self.cube.set_color(ansi_colors.get(active_key, "\033[38;5;220m"))
        
        # Update labels and placeholders
        self.status_bar.update_model(active_key.upper())
        self.chat_input.placeholder = f"Talk to {active_key.upper()} (e.g. type /help or questions)..."
        
        # Refresh buttons
        self.suggest_btn_1.label = f"Code Template" if active_key == "code" else f"Aesthetic Palette" if active_key == "design" else f"Debug Checklist" if active_key == "fix" else "Explain Folder"
        self.suggest_btn_2.label = f"Daily Challenge"
        self.suggest_btn_3.label = f"Generate Insights"

    def on_model_switched_event(self, key: str, cfg: Any):
        self.engine.active_model = key.upper()
        self.sync_model_ui()
        self.refresh_stats_ui()

    def append_user_message(self, text: str):
        self.chat_container.mount(ChatBubble(sender="User", text=text, model_color=self.active_color))
        self.chat_history_list.append({"sender": "User", "text": text})
        self.minimap.update_messages(list(self.chat_history_list))
        self.call_after_refresh(self.scroll_chat_to_bottom)

    def append_bot_message(self, text: str):
        active_key = self.model_manager.active_model_key
        self.chat_container.mount(ChatBubble(sender="Nexa", text=text, model_color=self.active_color))
        self.chat_history_list.append({"sender": "Nexa", "text": text})
        self.minimap.update_messages(list(self.chat_history_list))
        self.status_bar.increment_messages()
        self.call_after_refresh(self.scroll_chat_to_bottom)
        
        # Voice output speaking
        if self.voice_active and self.voice_output:
            active_model = self.model_manager.active_model
            self.voice_output.speak(text, active_model.voice_profile)

    def scroll_chat_to_bottom(self):
        chat_scroll = self.query_one("#chat-scroll")
        chat_scroll.scroll_to(y=chat_scroll.virtual_size.height)

    def on_input_changed(self, event: Input.Changed) -> None:
        if getattr(self, "_cycling_predictions", False):
            return
            
        val = event.value
        
        # If user types "/", pop up command palette modal
        if val == "/":
            self.chat_input.value = ""
            self.action_show_palette()
            return

        if not val or len(val.strip()) < 3:
            self.predictions_list = []
            self.sync_model_ui()
            return

        # Fetch predictions
        context = {"current_model": self.model_manager.active_model_key}
        preds = self.predictor.get_predictions(val, context)
        self.predictions_list = preds
        self.current_prediction_index = 0
        
        if preds:
            self.suggest_btn_1.label = preds[0]
            self.suggest_btn_2.label = preds[1] if len(preds) >= 2 else ""
            self.suggest_btn_3.label = preds[2] if len(preds) >= 3 else ""
        else:
            self.sync_model_ui()

    def on_key(self, event) -> None:
        key = event.key
        if getattr(self, "predictions_list", []):
            if key == "tab":
                event.prevent_default()
                event.stop()
                pred = self.predictions_list[self.current_prediction_index]
                self._cycling_predictions = True
                self.chat_input.value = pred
                self._cycling_predictions = False
                self.predictions_list = []
                self.sync_model_ui()
            elif key == "down":
                event.prevent_default()
                event.stop()
                self.current_prediction_index = (self.current_prediction_index + 1) % len(self.predictions_list)
                pred = self.predictions_list[self.current_prediction_index]
                self._cycling_predictions = True
                self.chat_input.value = pred
                self._cycling_predictions = False
            elif key == "escape":
                event.prevent_default()
                event.stop()
                self.predictions_list = []
                self.sync_model_ui()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        user_text = event.value.strip()
        if not user_text:
            return
            
        self.chat_input.value = ""
        self.process_input(user_text)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        
        if btn_id == "btn-send":
            user_text = self.chat_input.value.strip()
            if user_text:
                self.chat_input.value = ""
                self.process_input(user_text)
                
        elif btn_id == "mic-toggle":
            self.toggle_voice()
            
        elif btn_id.startswith("sug-"):
            # Check if predictions are active
            if getattr(self, "predictions_list", []):
                idx = int(btn_id.split("-")[1]) - 1
                if idx < len(self.predictions_list):
                    pred = self.predictions_list[idx]
                    self._cycling_predictions = True
                    self.chat_input.value = pred
                    self._cycling_predictions = False
                    self.predictions_list = []
                    self.sync_model_ui()
                    self.chat_input.focus()
                    return
            
            # Execute suggestion actions
            active_key = self.model_manager.active_model_key
            if btn_id == "sug-1":
                if active_key == "code":
                    self.chat_input.value = "/refactor "
                    self.chat_input.focus()
                elif active_key == "design":
                    self.chat_input.value = "/palette "
                    self.chat_input.focus()
                elif active_key == "fix":
                    self.chat_input.value = "/trace "
                    self.chat_input.focus()
                else:
                    self.process_input("Explain files in the current directory")
            elif btn_id == "sug-2":
                self.process_input("/challenges")
            elif btn_id == "sug-3":
                self.process_input("/insights")

    def toggle_voice(self):
        self.voice_active = not self.voice_active
        self.voice_wave.set_active(self.voice_active)
        
        if self.voice_active:
            self.mic_btn.label = "🎤 Live"
            self.mic_btn.variant = "success"
            
            # Start waveform animation updater
            self.voice_visualizer = WaveformVisualizer(callback=self.voice_wave.update_waveform)
            self.voice_visualizer.start()
            
            # Listen in background safely if voice input available
            if self.voice_input:
                self.stop_voice_listen = threading.Event()
                self.voice_input.listen_in_background(self.on_voice_transcribed, self.stop_voice_listen)
        else:
            self.mic_btn.label = "🎤 Mic"
            self.mic_btn.variant = "primary"
            
            if self.voice_visualizer:
                self.voice_visualizer.stop()
                self.voice_visualizer = None
                
            if hasattr(self, "stop_voice_listen"):
                self.stop_voice_listen.set()
                
            if self.voice_output:
                self.voice_output.stop()

    def on_voice_transcribed(self, text: str):
        """Callback from background speech-to-text listener."""
        self.call_from_thread(self.append_user_message, text)
        self.call_from_thread(self.process_input, text, print_user_msg=False)

    def action_show_palette(self):
        """Displays the searchable command palette."""
        def set_command(cmd: str):
            if cmd:
                self.chat_input.value = cmd
                self.chat_input.focus()
                
        self.push_screen(CommandPalette(self.router.commands), set_command)

    def process_input(self, text: str, print_user_msg: bool = True):
        if print_user_msg:
            self.append_user_message(text)
            
        # 1. Parse command if it is a slash command
        if text.startswith("/"):
            res = self.router.route(text)
            self.append_bot_message(res.text)
            
            # Trigger knowledge bar increment animation if we learned facts
            if (text.startswith("/learn") or text.startswith("/knowledge import")) and res.success:
                if hasattr(self, "knowledge_bar"):
                    self.knowledge_bar.trigger_increment()
            
            # Handle special animation triggers
            if res.animation == "model_switch":
                # Print switch transition animation logs
                active_key = self.model_manager.active_model_key
                logs = get_model_switch_logs("general", active_key, "\033[38;5;220m")
                for log in logs:
                    self.append_bot_message(log)
            elif res.animation == "level_up":
                self.play_level_up_burst()
                
            # Process XP event
            if res.xp_event:
                self.award_xp(res.xp_event)
            return

        # 2. Check for auto-switching
        detected_model = self.model_manager.detect_best_model(text)
        current_model = self.model_manager.active_model_key
        
        if detected_model != current_model:
            self.model_manager.set_active_model(detected_model)
            self.append_bot_message(f"[SYSTEM] Auto-switched model to {detected_model.upper()} based on input context.")
            
        # 3. Award general XP for chatting
        self.xp_manager.increment_message()
        self.award_xp("message_sent")
        
        # Categorize topic in stats
        if detected_model == "code":
            self.xp_manager.record_topic("coding")
        elif detected_model == "design":
            self.xp_manager.record_topic("design")
        elif detected_model == "fix":
            self.xp_manager.record_topic("debugging")
        else:
            self.xp_manager.record_topic("general")

        # 4. Generate AI response using logic engine
        active_model_cfg = self.model_manager.active_model
        self.engine.active_model = active_model_cfg.key.upper()
        self.engine.user_name = self.memory.memory.get("user_traits", {}).get("name") or "Human"
        
        # Create a placeholder bot bubble and mount it immediately so user sees action fast
        bot_bubble = ChatBubble(sender="Nexa", text="⚡ Thinking...", model_color=self.active_color)
        self.chat_container.mount(bot_bubble)
        self.call_after_refresh(self.scroll_chat_to_bottom)
        
        def bg_generate():
            def status_cb(status_msg: str):
                self.call_from_thread(bot_bubble.update_text, f"⚡ {status_msg}")
                self.call_from_thread(self.scroll_chat_to_bottom)
            
            try:
                response = self.engine.generate_response(text, status_callback=status_cb)
                formatted_response = f"{active_model_cfg.icon} {response}"
                self.call_from_thread(bot_bubble.update_text, formatted_response)
                
                # Record in history
                self.chat_history_list.append({"sender": "Nexa", "text": formatted_response})
                self.call_from_thread(self.minimap.update_messages, list(self.chat_history_list))
                self.call_from_thread(self.status_bar.increment_messages)
                self.call_from_thread(self.refresh_stats_ui)
                self.call_from_thread(self.scroll_chat_to_bottom)
                
                # voice output speaking
                if self.voice_active and self.voice_output:
                    self.voice_output.speak(response, active_model_cfg.voice_profile)
            except Exception as e:
                self.call_from_thread(bot_bubble.update_text, f"[Error generating response: {e}]")
                
        threading.Thread(target=bg_generate, daemon=True).start()

    def award_xp(self, event_key: str):
        xp_gained, leveled_up = self.xp_manager.add_xp(event_key)
        self.refresh_stats_ui()
        
        if leveled_up:
            self.play_level_up_burst()

    def play_level_up_burst(self):
        stats = self.xp_manager.stats
        # Add notification bubble
        lvl_up_banner = (
            f"⚡⚡ [bold color(#eab308)]LEVEL UP![/bold color] ⚡⚡\n"
            f"You reached Level {stats['level']}: {stats['level_name'].upper()}!"
        )
        self.append_bot_message(lvl_up_banner)
        
        # If in classic mode, play terminal animations
        # In Textual UI, we can trigger a short visual flash or display
        pass

    def on_unmount(self):
        if self.voice_visualizer:
            self.voice_visualizer.stop()
        if self.voice_output:
            self.voice_output.shutdown()
        if hasattr(self, "stop_voice_listen"):
            self.stop_voice_listen.set()
