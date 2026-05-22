# app/ui/widgets/status_bar.py
"""
Textual Widget representing the bottom status bar strip.
Displays active model, CPU/RAM/Disk metrics, and session information.
"""

from textual.widget import Widget
from textual.widgets import Label
from textual.containers import Horizontal
import psutil
import time

class StatusBar(Widget):
    """Bottom status bar with real-time hardware metrics and model state."""

    def __init__(self, active_model_name: str = "ULTRA", **kwargs) -> None:
        super().__init__(**kwargs)
        self.active_model_name = active_model_name
        self.msg_count = 0
        self.label_info = Label("")

    def compose(self):
        yield self.label_info
        # Setup polling interval for metrics (every 2.0s)
        self.set_interval(2.0, self.update_metrics)
        self.update_metrics()

    def update_model(self, model_name: str):
        self.active_model_name = model_name
        self.update_metrics()

    def increment_messages(self):
        self.msg_count += 1
        self.update_metrics()

    def update_metrics(self) -> None:
        """Polls system metrics and updates status bar text."""
        try:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            disk = psutil.disk_usage("/").percent
        except Exception:
            cpu, ram, disk = 0.0, 0.0, 0.0

        time_str = time.strftime("%H:%M:%S")
        
        status_text = (
            f" 🤖 MODEL: [bold]{self.active_model_name}[/bold] | "
            f"💻 CPU: [bold]{cpu}%[/bold] | "
            f"🧠 RAM: [bold]{ram}%[/bold] | "
            f"💾 DISK: [bold]{disk}%[/bold] | "
            f"💬 SESS: [bold]{self.msg_count} msgs[/bold] | "
            f"🕒 TIME: [bold]{time_str}[/bold]"
        )
        self.label_info.update(status_text)
        self.classes = "status-bar"
