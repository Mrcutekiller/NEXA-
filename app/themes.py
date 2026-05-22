# app/themes.py
"""
WCAG 2.1 AA compliant color themes and styles for the four NEXA v3 models.
"""

from typing import Dict

# Textual stylesheet definitions per model
TEXTUAL_THEMES = {
    "code": {
        "primary": "#00AAFF",
        "primary_dark": "#005588",
        "background": "#0b0f19",
        "surface": "#0f172a",
        "text": "#e2e8f0",
        "accent": "#38bdf8",
        "title": "Electric Blue | Code Specialist",
        "css": """
            Screen {
                background: #0b0f19;
                color: #e2e8f0;
            }
            .sidebar {
                background: #0f172a;
                border-right: tall #00AAFF;
                width: 32;
            }
            .title-bar {
                background: #00AAFF;
                color: #0b0f19;
                text-style: bold;
                height: 3;
            }
            .chat-bubble-user {
                background: #1e293b;
                color: #f8fafc;
                border: round #38bdf8;
                margin: 1 2;
                padding: 1 2;
            }
            .chat-bubble-bot {
                background: #0f172a;
                color: #e2e8f0;
                border: round #00AAFF;
                margin: 1 2;
                padding: 1 2;
            }
            .status-bar {
                background: #005588;
                color: #f8fafc;
            }
        """
    },
    "design": {
        "primary": "#D946EF",
        "primary_dark": "#86198F",
        "background": "#120a16",
        "surface": "#1e1026",
        "text": "#fdf4ff",
        "accent": "#f472b6",
        "title": "Hot Magenta | UI Design Specialist",
        "css": """
            Screen {
                background: #120a16;
                color: #fdf4ff;
            }
            .sidebar {
                background: #1e1026;
                border-right: tall #D946EF;
                width: 32;
            }
            .title-bar {
                background: #D946EF;
                color: #120a16;
                text-style: bold;
                height: 3;
            }
            .chat-bubble-user {
                background: #2e1244;
                color: #fdf4ff;
                border: round #f472b6;
                margin: 1 2;
                padding: 1 2;
            }
            .chat-bubble-bot {
                background: #1e1026;
                color: #fdf4ff;
                border: round #D946EF;
                margin: 1 2;
                padding: 1 2;
            }
            .status-bar {
                background: #86198F;
                color: #fdf4ff;
            }
        """
    },
    "fix": {
        "primary": "#EF4444",
        "primary_dark": "#991B1B",
        "background": "#180808",
        "surface": "#2d0f0f",
        "text": "#fef2f2",
        "accent": "#fca5a5",
        "title": "Crimson Red | Bug Fix Specialist",
        "css": """
            Screen {
                background: #180808;
                color: #fef2f2;
            }
            .sidebar {
                background: #2d0f0f;
                border-right: tall #EF4444;
                width: 32;
            }
            .title-bar {
                background: #EF4444;
                color: #180808;
                text-style: bold;
                height: 3;
            }
            .chat-bubble-user {
                background: #451a1a;
                color: #fef2f2;
                border: round #fca5a5;
                margin: 1 2;
                padding: 1 2;
            }
            .chat-bubble-bot {
                background: #2d0f0f;
                color: #fef2f2;
                border: round #EF4444;
                margin: 1 2;
                padding: 1 2;
            }
            .status-bar {
                background: #991B1B;
                color: #fef2f2;
            }
        """
    },
    "ultra": {
        "primary": "#EAB308",
        "primary_dark": "#854D0E",
        "background": "#121006",
        "surface": "#231f0c",
        "text": "#fefce8",
        "accent": "#fde047",
        "title": "Liquid Gold | Master Model",
        "css": """
            Screen {
                background: #121006;
                color: #fefce8;
            }
            .sidebar {
                background: #231f0c;
                border-right: tall #EAB308;
                width: 32;
            }
            .title-bar {
                background: #EAB308;
                color: #121006;
                text-style: bold;
                height: 3;
            }
            .chat-bubble-user {
                background: #3e3516;
                color: #fefce8;
                border: round #fde047;
                margin: 1 2;
                padding: 1 2;
            }
            .chat-bubble-bot {
                background: #231f0c;
                color: #fefce8;
                border: round #EAB308;
                margin: 1 2;
                padding: 1 2;
            }
            .status-bar {
                background: #854D0E;
                color: #fefce8;
            }
        """
    },
    "god_eye": {
        "primary": "#10B981",
        "primary_dark": "#047857",
        "background": "#064e3b",
        "surface": "#022c22",
        "text": "#ecfdf5",
        "accent": "#34d399",
        "title": "Emerald Green | Routing Coordinator",
        "css": """
            Screen {
                background: #064e3b;
                color: #ecfdf5;
            }
            .sidebar {
                background: #022c22;
                border-right: tall #10B981;
                width: 32;
            }
            .title-bar {
                background: #10B981;
                color: #064e3b;
                text-style: bold;
                height: 3;
            }
            .chat-bubble-user {
                background: #065f46;
                color: #ecfdf5;
                border: round #34d399;
                margin: 1 2;
                padding: 1 2;
            }
            .chat-bubble-bot {
                background: #022c22;
                color: #ecfdf5;
                border: round #10B981;
                margin: 1 2;
                padding: 1 2;
            }
            .status-bar {
                background: #047857;
                color: #ecfdf5;
            }
        """
    },
    "claude": {
        "primary": "#d97706",
        "primary_dark": "#78350f",
        "background": "#1c1917",
        "surface": "#292524",
        "text": "#f5f5f4",
        "accent": "#f59e0b",
        "title": "Warm Amber | Claude Theme",
        "css": """
            Screen {
                background: #1c1917;
                color: #f5f5f4;
            }
            .sidebar {
                background: #292524;
                border-right: tall #d97706;
                width: 32;
            }
            .title-bar {
                background: #d97706;
                color: #1c1917;
                text-style: bold;
                height: 3;
            }
            .chat-bubble-user {
                background: #44403c;
                color: #f5f5f4;
                border: round #f59e0b;
                margin: 1 2;
                padding: 1 2;
            }
            .chat-bubble-bot {
                background: #292524;
                color: #f5f5f4;
                border: round #d97706;
                margin: 1 2;
                padding: 1 2;
            }
            .status-bar {
                background: #78350f;
                color: #f5f5f4;
            }
        """
    }
}

# ANSI codes for classic terminal output fallback
ANSI_THEMES = {
    "code": {
        "primary": "\033[38;2;0;170;255m",     # #00AAFF
        "accent": "\033[38;2;56;189;248m",    # #38bdf8
        "bg_highlight": "\033[48;2;15;23;42m",
        "reset": "\033[0m"
    },
    "design": {
        "primary": "\033[38;2;217;70;239m",    # #D946EF
        "accent": "\033[38;2;244;114;182m",   # #f472b6
        "bg_highlight": "\033[48;2;30;16;38m",
        "reset": "\033[0m"
    },
    "fix": {
        "primary": "\033[38;2;239;68;68m",     # #EF4444
        "accent": "\033[38;2;252;165;165m",   # #fca5a5
        "bg_highlight": "\033[48;2;45;15;15m",
        "reset": "\033[0m"
    },
    "ultra": {
        "primary": "\033[38;2;234;179;8m",     # #EAB308
        "accent": "\033[38;2;253;224;71m",    # #fde047
        "bg_highlight": "\033[48;2;35;31;12m",
        "reset": "\033[0m"
    },
    "god_eye": {
        "primary": "\033[38;2;16;185;129m",    # #10B981
        "accent": "\033[38;2;52;211;153m",     # #34d399
        "bg_highlight": "\033[48;2;6;78;59m",
        "reset": "\033[0m"
    },
    "claude": {
        "primary": "\033[38;2;217;119;6m",     # #d97706
        "accent": "\033[38;2;245;158;11m",     # #f59e0b
        "bg_highlight": "\033[48;2;41;37;36m",
        "reset": "\033[0m"
    }
}
