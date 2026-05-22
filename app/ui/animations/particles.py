# app/ui/animations/particles.py
"""
Level Up and XP Award Particle Animations.
Calculates physics-based particle dispersion vectors and returns colored ANSI frames.
"""

import math
import random
import time
from typing import List

GOLD_COLOR = "\033[38;5;220m"
WHITE_COLOR = "\033[97m"
GREEN_COLOR = "\033[32m"
RESET_COLOR = "\033[0m"

ASCII_LEVEL_UP = [
    "  _      _______      ________ _      _    _ _____  ",
    " | |    |  ____\\ \\    / /  ____| |    | |  | |  __ \\ ",
    " | |    | |__   \\ \\  / /| |__  | |    | |  | | |__) |",
    " | |    |  __|   \\ \\/ / |  __| | |    | |  | |  ___/ ",
    " | |____| |____   \\  /  | |____| |____| |__| | |     ",
    " |______|______|   \\/   |______|______ \\____/|_|     "
]

class Particle:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        # Random angle and speed
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1.0, 4.0)
        self.dx = math.cos(angle) * speed * 2.0  # Stretch X to compensate for terminal font aspect ratio
        self.dy = math.sin(angle) * speed
        # Gravity
        self.gravity = 0.15
        # Colors: gold, yellow, light yellow, white
        self.color = random.choice([
            "\033[38;5;220m",  # Gold
            "\033[38;5;226m",  # Yellow
            "\033[38;5;228m",  # Light Yellow
            "\033[97m"         # White
        ])
        self.char = random.choice(["*", "+", ".", "o"])

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.dy += self.gravity  # Apply gravity downwards

class LevelUpAnimation:
    def __init__(self, width: int = 60, height: int = 20):
        self.width = width
        self.height = height
        self.particles: List[Particle] = []
        
    def reset(self, num_particles: int = 40):
        self.particles = [Particle(self.width / 2.0, self.height / 3.0) for _ in range(num_particles)]

    def get_frame(self, level_num: int, level_name: str, xp_gained: int = 0) -> str:
        """
        Calculates one frame of particle physics and draws the UI.
        """
        # Create empty canvas
        canvas = [[" " for _ in range(self.width)] for _ in range(self.height)]
        
        # Update and draw particles
        for p in self.particles:
            p.update()
            ix, iy = int(p.x), int(p.y)
            if 0 <= ix < self.width and 0 <= iy < self.height:
                canvas[iy][ix] = f"{p.color}{p.char}{RESET_COLOR}"
                
        # Remove particles that fell off-screen
        self.particles = [p for p in self.particles if 0 <= p.x < self.width and p.y < self.height]
        
        # Convert canvas to list of lines
        lines = []
        for r_idx, row in enumerate(canvas):
            # Render text on top of particles
            line_str = ""
            for cell in row:
                line_str += cell if len(cell) > 1 else cell  # Cell might contain ANSI codes
            lines.append(line_str)
            
        # Overlay Level Up Banner in the middle/top
        banner_start = 2
        for idx, line in enumerate(ASCII_LEVEL_UP):
            if banner_start + idx < self.height:
                # Merge ASCII banner centered
                offset = max(0, (self.width - len(line)) // 2)
                # Overwrite line
                original_line = lines[banner_start + idx]
                # Keep particles on the sides
                left = original_line[:offset]
                right = original_line[offset + len(line):]
                lines[banner_start + idx] = left + f"{GOLD_COLOR}{line}{RESET_COLOR}" + right
                
        # Overlay Level Name and XP info
        info_y = banner_start + len(ASCII_LEVEL_UP) + 1
        if info_y < self.height:
            info_str = f" REACHED LEVEL {level_num}: {level_name.upper()} "
            offset = max(0, (self.width - len(info_str)) // 2)
            original_line = lines[info_y]
            lines[info_y] = original_line[:offset] + f"{GREEN_COLOR}{info_str}{RESET_COLOR}" + original_line[offset + len(info_str):]
            
        if xp_gained > 0 and info_y + 1 < self.height:
            xp_str = f" +{xp_gained} XP BONUS! "
            offset = max(0, (self.width - len(xp_str)) // 2)
            original_line = lines[info_y + 1]
            lines[info_y + 1] = original_line[:offset] + f"{GOLD_COLOR}{xp_str}{RESET_COLOR}" + original_line[offset + len(xp_str):]
            
        return "\n".join(lines)

def play_terminal_level_up(level_num: int, level_name: str, xp_gained: int = 100):
    """
    Synchronously plays the level up animation directly in the terminal (classic mode).
    """
    animator = LevelUpAnimation()
    animator.reset()
    
    for _ in range(25): # 25 frames
        frame = animator.get_frame(level_num, level_name, xp_gained)
        print("\033[H" + frame, end="", flush=True)
        time.sleep(0.06)
    print("\n" * 2)
