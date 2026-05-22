# app/ui/widgets/command_palette.py
"""
Textual Modal Screen for searching and auto-completing slash commands.
"""

from textual.screen import ModalScreen
from textual.widgets import Input, ListView, ListItem, Label
from textual.containers import Vertical
from textual.message import Message
from typing import Dict, List, Tuple

class CommandPalette(ModalScreen[str]):
    """A search overlay for available slash commands."""

    def __init__(self, commands: Dict[str, Tuple[Any, str, str]], **kwargs) -> None:
        super().__init__(**kwargs)
        self.commands = commands
        self.list_view = ListView()
        self.search_input = Input(placeholder="Type command name to search...")

    def compose(self):
        with Vertical(id="palette-container", classes="modal-overlay"):
            yield Label("🔍 SEARCH NEXA SLASH COMMANDS", id="palette-title")
            yield self.search_input
            yield self.list_view
            yield Label("Press [bold]Esc[/bold] to close palette, or [bold]Enter[/bold] to select.", id="palette-help")

    def on_mount(self):
        self.search_input.focus()
        self.populate_list("")

    def populate_list(self, query: str):
        self.list_view.clear()
        q = query.lower()
        
        count = 0
        for cmd, (_, cat, desc) in self.commands.items():
            if q in cmd or q in desc.lower():
                category_label = f"[{cat.upper()}]"
                item_label = f"[bold]{cmd:15}[/bold] [dim]{category_label:12}[/dim] - {desc}"
                self.list_view.append(ListItem(Label(item_label), id=f"item-{cmd[1:]}"))
                count += 1
                if count >= 10:  # Cap at 10 results for viewability
                    break

    def on_input_changed(self, event: Input.Changed) -> None:
        self.populate_list(event.value)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        # If enter is pressed in search box, select the first item in the list
        if len(self.list_view.children) > 0:
            selected_item = self.list_view.children[0]
            cmd_name = "/" + selected_item.id[5:]
            self.dismiss(cmd_name)
        else:
            self.dismiss("")

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.item and event.item.id:
            cmd_name = "/" + event.item.id[5:]
            self.dismiss(cmd_name)
        else:
            self.dismiss("")

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss("")
