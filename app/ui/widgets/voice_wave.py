# app/ui/widgets/voice_wave.py
"""
Textual Widget to display the 8-bar real-time voice waveform visualization.
"""

from textual.widget import Widget
from textual.reactive import reactive
from textual.widgets import Label

class VoiceWave(Widget):
    """Renders the real-time audio waveform or muted message."""
    
    waveform_text = reactive("Muted  ")
    is_active = reactive(False)

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.label = Label("")

    def compose(self):
        yield self.label

    def update_waveform(self, text: str):
        if self.is_active:
            self.waveform_text = text
            self.label.update(f"🎤 {self.waveform_text}")
        else:
            self.label.update("🔇 [ Muted ]")

    def set_active(self, active: bool):
        self.is_active = active
        if not active:
            self.label.update("🔇 [ Muted ]")
        else:
            self.label.update("🎤  ▂▃▄▃▂ ")
