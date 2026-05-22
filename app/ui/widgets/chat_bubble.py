# app/ui/widgets/chat_bubble.py
"""
Textual Widget representing a single styled chat message bubble with avatar, metadata, and body.
"""

from textual.widget import Widget
from textual.widgets import Label
from textual.containers import Vertical
import time

class ChatBubble(Widget):
    """A message bubble inside the scrollable chat log."""

    def __init__(self, sender: str, text: str, model_color: str = "#00AAFF", **kwargs) -> None:
        super().__init__(**kwargs)
        self.sender = sender.lower()
        self.text = text
        self.model_color = model_color
        self.timestamp = time.strftime("%H:%M:%S")

    def compose(self):
        avatar = "👤 USER" if self.sender == "user" else "🤖 NEXA"
        time_str = f"[{self.timestamp}]"
        
        # Add CSS classes dynamically
        if self.sender == "user":
            self.classes = "chat-bubble-user"
            header = f"[bold]{avatar}[/bold] {time_str}"
        else:
            self.classes = "chat-bubble-bot"
            # Color name based on active model color
            header = f"[bold color({self.model_color})]{avatar}[/bold color] {time_str}"
            
        with Vertical():
            yield Label(header, id="bubble-header")
            yield Label(self.text, id="bubble-body")
