# app/ui/themes.py
"""
Textual CSS Stylesheet definitions for NEXA v3.
Provides responsive layouts, sidebar positioning, chat bubble alignment, and color profiles.
"""

NEXA_CSS = """
Screen {
    background: #1c1917;
    color: #f5f5f4;
    layout: grid;
    grid-size: 2 3;
    grid-columns: 32 1fr;
    grid-rows: 3 1fr 3;
}

.title-bar {
    column-span: 2;
    background: #292524;
    color: #f5f5f4;
    border-bottom: hsolid #d97706;
    height: 3;
    content-align: center middle;
    text-style: bold;
}

.sidebar {
    background: #292524;
    border-right: vsolid #44403c;
    padding: 1 2;
}

#chat-area {
    background: #1c1917;
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
    background: #44403c;
    color: #f5f5f4;
    border-left: solid #f59e0b 3;
    margin: 1 2;
    padding: 1 2;
    align: right;
    width: 85%;
}

.chat-bubble-bot {
    background: #292524;
    color: #f5f5f4;
    border-left: solid #d97706 3;
    margin: 1 2;
    padding: 1 2;
    align: left;
    width: 85%;
}

#bubble-header {
    text-style: bold;
    color: #f59e0b;
    margin-bottom: 1;
}

#bubble-body {
    color: #f5f5f4;
}

#input-container {
    column-span: 2;
    layout: horizontal;
    background: #292524;
    border-top: hsolid #44403c;
    height: 3;
    padding: 0 1;
}

#input-container Input {
    width: 75%;
    border: none;
    background: #44403c;
}

#input-container Button {
    width: 10%;
    margin-left: 1;
    min-width: 8;
}

.status-bar {
    column-span: 2;
    height: 1;
    background: #292524;
    color: #a8a29e;
    content-align: left middle;
    padding-left: 2;
}

#xp-bar-container {
    padding: 1 0;
    border-bottom: hsolid #44403c;
}

#xp-bar-container ProgressBar {
    width: 100%;
    height: 1;
    color: #d97706;
}

.suggest-bar {
    layout: horizontal;
    height: 3;
    background: #1c1917;
    padding: 0 2;
    align-vertical: center;
}

.suggest-button {
    margin-right: 2;
    background: #292524;
    color: #d6d3d1;
    border: none;
    height: 1;
}

.suggest-button:hover {
    background: #44403c;
    color: #f5f5f4;
}

#palette-container {
    background: #292524;
    border: double #d97706;
    padding: 1 2;
    width: 60;
    height: 25;
    align: center middle;
}

#palette-title {
    text-style: bold;
    color: #d97706;
    margin-bottom: 1;
    content-align: center middle;
}

#palette-help {
    margin-top: 1;
    color: #a8a29e;
    content-align: center middle;
}
"""
