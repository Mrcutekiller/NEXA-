# app/ui/widgets/xp_bar.py
"""
Textual Widget to display user Level, Level Title, and XP Progress.
"""

from textual.widget import Widget
from textual.widgets import Label, ProgressBar
from textual.containers import Vertical, Horizontal

class XPBar(Widget):
    """Displays level progression and experience points."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.level_label = Label("Level 1 - Greenhorn")
        self.xp_progress = ProgressBar(total=100, show_percentage=True)
        self.xp_details_label = Label("0 / 200 XP (0.0%)")

    def compose(self):
        with Vertical(id="xp-bar-container"):
            yield self.level_label
            yield self.xp_progress
            yield self.xp_details_label

    def update_xp(self, level: int, name: str, earned: int, total: int, pct: float):
        """Updates the progress values in the widget."""
        self.level_label.update(f"🏆 Level {level} - [bold]{name.upper()}[/bold]")
        self.xp_progress.progress = int(pct * 100)
        self.xp_details_label.update(f"{earned} / {total} XP ({pct * 100:.1f}%)")
