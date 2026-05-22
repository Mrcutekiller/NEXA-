# app/ui/animations/model_switch.py
"""
Model Switch Animation.
Handles the 7-step transition sequence (dim → badge-out → border-colour-shift → badge-in → placeholder-fade → sweep-line → brighten)
for smooth transitions in both classic CLI and Textual UI.
"""

import time
from typing import Generator, List

def get_model_switch_logs(from_model: str, to_model: str, to_color_ansi: str) -> List[str]:
    """
    Returns the log lines representing the 7-step switch sequence.
    """
    return [
        f"\033[2m[SYSTEM] Switching neural path: {from_model.upper()} -> {to_color_ansi}{to_model.upper()}\033[0m",
        f"\033[2m[Step 1/7] Dimming UI viewport and locking input...\033[0m",
        f"\033[2m[Step 2/7] Unmounting {from_model.upper()} specialized response weights...\033[0m",
        f"[Step 3/7] Shifting theme colors to {to_color_ansi}{to_model.upper()}\033[0m color tokens...",
        f"[Step 4/7] Hot-loading {to_color_ansi}{to_model.upper()}\033[0m prompt layers and instruction set...",
        f"[Step 5/7] Repopulating smart autocomplete suggestions buffer...",
        f"[Step 6/7] Sweeping scan-line: alignment check \033[32m[PASS]\033[0m...",
        f"\033[1m[Step 7/7] Restoring full UI brightness. {to_color_ansi}{to_model.upper()}\033[0m is locked in! \033[0m"
    ]

def get_sweep_line_frame(width: int, step: int, char: str = "=") -> str:
    """
    Generates a horizontal scanline frame of a given width for visual transition.
    """
    if step < 0:
        step = 0
    pos = step % width
    left = " " * pos
    line = f"\033[38;5;51m{char * 5}\033[0m"
    right = " " * max(0, width - pos - 5)
    return f"[{left}{line}{right}]"

def play_terminal_model_switch(from_model: str, to_model: str, to_color_ansi: str, delay: float = 0.05):
    """
    Synchronously plays the model switch transition to standard output.
    """
    logs = get_model_switch_logs(from_model, to_model, to_color_ansi)
    for log in logs:
        print(log)
        time.sleep(delay)
        
    # Play a quick horizontal sweep sweep
    for i in range(20):
        frame = get_sweep_line_frame(50, i)
        print(f"\r{frame}", end="", flush=True)
        time.sleep(0.015)
    print("\r" + " " * 54 + "\r", end="", flush=True)
