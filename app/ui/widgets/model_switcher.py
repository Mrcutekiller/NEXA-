# app/ui/widgets/model_switcher.py
"""
Custom Textual Widget for switching between the 4 models.
"""

from textual.widget import Widget
from textual.widgets import Button
from textual.containers import Horizontal
from textual.message import Message

class ModelSwitcher(Widget):
    """A horizontal row of buttons to select the active specialist model."""
    
    class ModelChanged(Message):
        """Emitted when the user selects a new model."""
        def __init__(self, model_key: str) -> None:
            self.model_key = model_key
            super().__init__()

    def __init__(self, active_key: str = "ultra", **kwargs) -> None:
        super().__init__(**kwargs)
        self.active_key = active_key
        self.buttons = {}

    def compose(self):
        with Horizontal(id="switcher-container"):
            self.buttons["code"] = Button("💻 CODE", id="switch-code", variant="primary")
            self.buttons["design"] = Button("🎨 DESIGN", id="switch-design", variant="primary")
            self.buttons["fix"] = Button("🔧 FIX", id="switch-fix", variant="primary")
            self.buttons["ultra"] = Button("👑 ULTRA", id="switch-ultra", variant="success")
            
            for button in self.buttons.values():
                yield button
                
        self.call_after_refresh(self.update_styles)

    def set_active(self, model_key: str):
        if model_key in self.buttons:
            self.active_key = model_key
            self.update_styles()

    def update_styles(self):
        """Highlights the active model button with custom border/background styles."""
        for key, btn in self.buttons.items():
            if key == self.active_key:
                btn.styles.opacity = 1.0
                btn.styles.text_style = "bold underline"
                # Add dynamic border coloring in CSS or styles
                btn.styles.border = ("double", self.get_color_token(key))
            else:
                btn.styles.opacity = 0.6
                btn.styles.text_style = "normal"
                btn.styles.border = ("none", "transparent")

    def get_color_token(self, key: str) -> str:
        tokens = {
            "code": "#00AAFF",
            "design": "#D946EF",
            "fix": "#EF4444",
            "ultra": "#EAB308"
        }
        return tokens.get(key, "#ffffff")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "switch-code":
            key = "code"
        elif button_id == "switch-design":
            key = "design"
        elif button_id == "switch-fix":
            key = "fix"
        else:
            key = "ultra"
            
        self.active_key = key
        self.update_styles()
        self.post_message(self.ModelChanged(key))
