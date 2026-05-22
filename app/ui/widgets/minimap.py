# app/ui/widgets/minimap.py
from textual.widgets import Static
from textual.reactive import reactive
from typing import List, Dict, Any

class Minimap(Static):
    """Minimap panel rendering a high-contrast structural representation of chat history."""
    
    messages: reactive[List[Dict[str, Any]]] = reactive([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.styles.width = 12
        self.styles.dock = "right"
        self.styles.background = "#0f172a"
        self.styles.border_left = ("thin", "#334155")
        self.styles.padding = (1, 1)

    def render(self) -> str:
        if len(self.messages) < 6:
            return ""  # Only show when conversation gets populated

        lines = ["[bold]MAP[/bold]", "───"]
        for idx, msg in enumerate(self.messages):
            sender = msg.get("sender", "User")
            text = msg.get("text", "")
            
            if sender == "User":
                # User message - Blue dot
                lines.append(f"[color(#38bdf8)]●[/color] [dim]U{idx}[/dim]")
            elif "```" in text:
                # Code block - Yellow block
                lines.append(f"[color(#eab308)]▣[/color] [dim]C{idx}[/dim]")
            elif "note" in text.lower():
                # Saved note - Green star
                lines.append(f"[color(#10b981)]★[/color] [dim]N{idx}[/dim]")
            else:
                # Bot message - Purple dot
                lines.append(f"[color(#a855f7)]●[/color] [dim]A{idx}[/dim]")

        # Current location indicator
        lines.append("───")
        lines.append(" ▶ [bold]LATEST[/bold]")
        return "\n".join(lines)

    def update_messages(self, messages_list: List[Dict[str, Any]]):
        self.messages = messages_list
