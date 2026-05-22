# app/ui/animations/boot.py
"""
Boot sequence animations for NEXA v3.
Contains ASCII logo reveals, pulse effects, log lines, and tagline transitions.
"""

import time
import sys

NEXA_ASCII_LOGO = [
    "███╗   ██╗███████╗██╗  ██╗ █████╗ ",
    "████╗  ██║██╔════╝╚██╗██╔╝██╔══██╗",
    "██╔██╗ ██║█████╗   ╚███╔╝ ███████║",
    "██║╚██╗██║██╔══╝   ██╔██╗ ██╔══██║",
    "██║ ╚████║███████╗██╔╝ ██╗██║  ██║",
    "╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝"
]

BOOT_LOG_LINES = [
    "Initializing NEXA Core Engine v3.0.0-PRO...",
    "Loading neural weights for Specialist Models...",
    "Starting 4-Core Brain Manager (Code, Design, Fix, Ultra)...",
    "Configuring WCAG 2.1 AA compliant color palettes...",
    "Activating high-fidelity 3D rendering pipeline...",
    "Mounting local SQLite knowledge vault and memory buffers...",
    "Checking audio voice devices and faster-whisper VAD parameters...",
    "System status: 100% ONLINE. Zero data-loss protection: ACTIVE."
]

def get_boot_logs():
    """Returns boot logs with simulated delays."""
    for line in BOOT_LOG_LINES:
        yield f"\033[38;5;250m[\033[32mOK\033[38;5;250m] {line}"

def get_logo_reveal_frames():
    """Generates logo reveal frames line-by-line."""
    current = []
    for line in NEXA_ASCII_LOGO:
        current.append(line)
        yield "\n".join(current)

def get_logo_pulse_frames(color_code="\033[38;5;51m", cycles=3, steps=5):
    """
    Creates pulsing brightness animation frames for the logo.
    Uses ANSI 256-color palette to fade in and out.
    """
    # 256-color grays/cyans for pulse levels
    pulse_colors = [
        "\033[38;5;23m",  # Dark Teal
        "\033[38;5;30m",  # Medium Teal
        "\033[38;5;37m",  # Bright Teal
        "\033[38;5;51m",  # Electric Cyan (max)
        "\033[38;5;37m",
        "\033[38;5;30m",
        "\033[38;5;23m"
    ]
    
    frames = []
    for _ in range(cycles):
        for color in pulse_colors:
            frame = "\n".join([f"{color}{line}\033[0m" for line in NEXA_ASCII_LOGO])
            frames.append(frame)
    return frames

def play_terminal_boot():
    """
    Plays the entire boot animation directly to stdout for classic mode.
    """
    sys.stdout.write("\033[H\033[2J")  # Clear screen
    sys.stdout.flush()
    
    # 1. Print log lines with delay
    for line in BOOT_LOG_LINES:
        print(f"\033[38;5;250m[\033[32mOK\033[38;5;250m] {line}")
        time.sleep(0.08)
    
    print("\n")
    time.sleep(0.2)
    
    # 2. Line by line logo reveal
    for frame in get_logo_reveal_frames():
        sys.stdout.write("\033[H") # Reset cursor
        # Skip down past boot logs
        sys.stdout.write("\n" * (len(BOOT_LOG_LINES) + 2))
        print("\033[38;5;51m" + frame + "\033[0m")
        time.sleep(0.04)
        
    time.sleep(0.1)
    
    # 3. Pulse animation
    pulse_frames = get_logo_pulse_frames()
    for frame in pulse_frames:
        sys.stdout.write("\033[H")
        sys.stdout.write("\n" * (len(BOOT_LOG_LINES) + 2))
        sys.stdout.write(frame + "\n")
        sys.stdout.flush()
        time.sleep(0.05)
        
    # 4. Slide tagline
    tagline = "--- NEXA v3: Write it once. Write it right. ---"
    for i in range(1, len(tagline) + 1):
        sys.stdout.write("\033[H")
        sys.stdout.write("\n" * (len(BOOT_LOG_LINES) + len(NEXA_ASCII_LOGO) + 4))
        sys.stdout.write(" " * ((60 - i)//2) + tagline[:i] + "\033[0m\n")
        sys.stdout.flush()
        time.sleep(0.01)
        
    time.sleep(0.5)
