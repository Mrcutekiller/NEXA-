# app/ui/themes.py
"""
Textual CSS Stylesheet definitions for NEXA v3.
Provides responsive layouts, sidebar positioning, chat bubble alignment, and color profiles.
"""

NEXA_CSS = """
Screen {
    background: #0b0f19;
    color: #e2e8f0;
    layout: grid;
    grid-size: 2 3;
    grid-columns: 32 1fr;
    grid-rows: 3 1fr 3;
}

.title-bar {
    grid-column: 1 / 3;
    background: #0f172a;
    color: #e2e8f0;
    border-bottom: hsolid #00AAFF;
    height: 3;
    content-align: center middle;
    text-style: bold;
}

.sidebar {
    grid-row: 2 / 3;
    background: #0f172a;
    border-right: vsolid #1e293b;
    padding: 1 2;
}

#chat-area {
    grid-row: 2 / 3;
    grid-column: 2 / 3;
    background: #090d16;
    layout: horizontal;
    padding: 0;
}

#chat-scroll {
    width: 1fr;
    height: 100%;
    overflow-y: scroll;
    padding: 1 2;
}

.chat-bubble-user {
    background: #1e293b;
    color: #f8fafc;
    border-left: solid #38bdf8 3;
    margin: 1 2;
    padding: 1 2;
    align: right;
    width: 85%;
}

.chat-bubble-bot {
    background: #0f172a;
    color: #e2e8f0;
    border-left: solid #00AAFF 3;
    margin: 1 2;
    padding: 1 2;
    align: left;
    width: 85%;
}

#bubble-header {
    text-style: bold;
    color: #6ee7f9;
    margin-bottom: 1;
}

#bubble-body {
    color: #e2e8f0;
}

#input-container {
    grid-column: 1 / 3;
    grid-row: 3 / 4;
    layout: horizontal;
    background: #0f172a;
    border-top: hsolid #1e293b;
    height: 3;
    padding: 0 1;
}

#input-container Input {
    width: 75%;
    border: none;
    background: #1e293b;
}

#input-container Button {
    width: 10%;
    margin-left: 1;
    min-width: 8;
}

.status-bar {
    grid-column: 1 / 3;
    height: 1;
    background: #0f172a;
    color: #94a3b8;
    content-align: left middle;
    padding-left: 2;
}

#xp-bar-container {
    padding: 1 0;
    border-bottom: hsolid #1e293b;
}

#xp-bar-container ProgressBar {
    width: 100%;
    height: 1;
    color: #EAB308;
}

.suggest-bar {
    layout: horizontal;
    height: 3;
    background: #090d16;
    padding: 0 2;
    align-vertical: center;
}

.suggest-button {
    margin-right: 2;
    background: #1e293b;
    color: #cbd5e1;
    border: none;
    height: 1;
}

.suggest-button:hover {
    background: #334155;
    color: #f8fafc;
}

#palette-container {
    background: #0f172a;
    border: double #00AAFF;
    padding: 1 2;
    width: 60;
    height: 25;
    align: center middle;
}

#palette-title {
    text-style: bold;
    color: #00AAFF;
    margin-bottom: 1;
    content-align: center middle;
}

#palette-help {
    margin-top: 1;
    color: #94a3b8;
    content-align: center middle;
}
"""
