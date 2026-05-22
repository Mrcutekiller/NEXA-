# app/ui/widgets/knowledge_bar.py
from textual.widgets import Static
from textual.reactive import reactive
from typing import Dict, Any

class KnowledgeBar(Static):
    """Sidebar widget tracking facts count, top topics, and learning updates."""
    
    facts_count: reactive[int] = reactive(0)
    top_topic: reactive[str] = reactive("none")
    animation_text: reactive[str] = reactive("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.styles.margin = (1, 0)
        self.styles.padding = (0, 1)

    def render(self) -> str:
        anim = f"  [bold color(#10b981)]{self.animation_text}[/bold color]" if self.animation_text else ""
        return f"""
📚 KNOWLEDGE BASE
────────────────
Facts:      [bold]{self.facts_count}[/bold]{anim}
Top Topic:  [bold color(#38bdf8)]{self.top_topic}[/bold color]
        """.strip()

    def trigger_increment(self):
        self.animation_text = "↑ +1 learned! ✓"
        # Reset flash after 3 seconds
        self.set_timer(3.0, self._reset_animation)

    def _reset_animation(self):
        self.animation_text = ""
