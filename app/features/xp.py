# app/features/xp.py
"""
Gamification & Engagement Layer.
Tracks XP awards, calculates levels (8 tiers), and manages login/usage streaks.
"""

import json
import os
import time
from typing import Dict, Any, Tuple

# 8 Levels / Tiers
LEVELS = [
    (1, "Greenhorn", 0),
    (2, "Logic Initiate", 200),
    (3, "Syntax Adept", 500),
    (4, "Algorithm Architect", 1000),
    (5, "Neural Commander", 2000),
    (6, "Quantum Scholar", 3500),
    (7, "Omni Sage", 5500),
    (8, "Nexa God Mode", 8000)
]

XP_EVENTS = {
    "message_sent": 10,
    "model_switched": 5,
    "command_run": 15,
    "challenge_completed": 100,
    "notebook_note_saved": 20,
    "voice_activated": 15,
    "code_written": 20,
    "ui_designed": 20,
    "bug_fixed": 30,
    "complex_solve": 40
}

class XPManager:
    def __init__(self, stats_path: str = "user/stats.json"):
        self.stats_path = stats_path
        self.stats = {
            "total_xp": 0,
            "level": 1,
            "level_name": LEVELS[0][1],
            "streak": 0,
            "last_active_date": "",
            "message_count": 0,
            "commands_run": 0,
            "challenges_completed_count": 0,
            "topic_breakdown": {
                "coding": 0,
                "design": 0,
                "debugging": 0,
                "general": 0
            }
        }
        self._load_stats()

    def _load_stats(self):
        dir_name = os.path.dirname(self.stats_path)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)
            
        if os.path.exists(self.stats_path):
            try:
                with open(self.stats_path, "r") as f:
                    loaded = json.load(f)
                    # Merge keys to ensure compatibility
                    for k, v in loaded.items():
                        if k in self.stats:
                            if isinstance(v, dict) and isinstance(self.stats[k], dict):
                                self.stats[k].update(v)
                            else:
                                self.stats[k] = v
            except Exception as e:
                print(f"[XP Load Error] {e}")

    def save_stats(self):
        try:
            with open(self.stats_path, "w") as f:
                json.dump(self.stats, f, indent=4)
        except Exception as e:
            print(f"[XP Save Error] {e}")

    def add_xp(self, event_key: str) -> Tuple[int, bool]:
        """
        Adds XP for a specific event. Returns (xp_added, leveled_up).
        """
        xp_amount = XP_EVENTS.get(event_key, 10)
        self.stats["total_xp"] += xp_amount
        
        # Check level up
        old_level = self.stats["level"]
        new_level = old_level
        new_name = self.stats["level_name"]
        
        # Determine current level based on total XP
        for lv, name, min_xp in LEVELS:
            if self.stats["total_xp"] >= min_xp:
                new_level = lv
                new_name = name
                
        leveled_up = new_level > old_level
        if leveled_up:
            self.stats["level"] = new_level
            self.stats["level_name"] = new_name
            
        self.save_stats()
        return xp_amount, leveled_up

    def increment_message(self):
        self.stats["message_count"] += 1
        self.save_stats()

    def update_streak(self):
        """
        Checks and increments the user's daily streak.
        """
        today = time.strftime("%Y-%m-%d")
        last_active = self.stats.get("last_active_date", "")
        
        if not last_active:
            self.stats["streak"] = 1
        elif last_active == today:
            pass  # Already updated today
        else:
            # Check if yesterday
            try:
                last_time = time.strptime(last_active, "%Y-%m-%d")
                today_time = time.strptime(today, "%Y-%m-%d")
                diff_days = (time.mktime(today_time) - time.mktime(last_time)) / 86400
                if diff_days <= 1.1:  # Within 24-26 hours
                    self.stats["streak"] += 1
                else:
                    self.stats["streak"] = 1  # Reset streak
            except Exception:
                self.stats["streak"] = 1
                
        self.stats["last_active_date"] = today
        self.save_stats()

    def get_progress_to_next(self) -> Tuple[int, int, float]:
        """
        Returns (current_xp_in_level, next_level_xp_requirement, percent_complete).
        """
        current_xp = self.stats["total_xp"]
        current_lvl = self.stats["level"]
        
        if current_lvl >= len(LEVELS):
            # Max level
            max_lvl_xp = LEVELS[-1][2]
            return current_xp - max_lvl_xp, 99999, 1.0
            
        current_lvl_min = LEVELS[current_lvl - 1][2]
        next_lvl_min = LEVELS[current_lvl][2]
        
        total_needed_in_range = next_lvl_min - current_lvl_min
        earned_in_range = current_xp - current_lvl_min
        
        percent = earned_in_range / total_needed_in_range if total_needed_in_range > 0 else 0.0
        percent = max(0.0, min(1.0, percent))
        
        return earned_in_range, total_needed_in_range, percent
        
    def record_topic(self, topic: str):
        if topic in self.stats["topic_breakdown"]:
            self.stats["topic_breakdown"][topic] += 1
            self.save_stats()
