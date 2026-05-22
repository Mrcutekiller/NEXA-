# app/ui/widgets/preview_pane.py
from textual.widgets import Static
from textual.reactive import reactive

class PreviewPane(Static):
    """Widget to show the status of the local live preview server (port 7750)."""
    
    server_status: reactive[str] = reactive("OFFLINE")
    preview_url: reactive[str] = reactive("http://localhost:7750/preview")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.styles.margin = (1, 0)
        self.styles.padding = (0, 1)

    def render(self) -> str:
        color = "#ef4444" if self.server_status == "OFFLINE" else "#10b981"
        return f"""
🌐 LIVE CODE PREVIEW
──────────────────
Status:   [bold color({color})]{self.server_status}[/bold color]
Server:   [underline]{self.preview_url}[/underline]
        """.strip()

    def set_status(self, is_online: bool):
        self.server_status = "ONLINE" if is_online else "OFFLINE"
