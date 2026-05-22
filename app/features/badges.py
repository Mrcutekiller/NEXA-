# app/features/badges.py
import os
import json
from datetime import datetime
from typing import Dict, List, Any

class BadgeManager:
    BADGES_CONFIG = {
        "coding_first_line": {"icon": "🐣", "name": "First Line", "desc": "Generated first code with Nexa Code", "xp": 100},
        "coding_bug_hunter": {"icon": "🐛", "name": "Bug Hunter", "desc": "Fixed 10 bugs", "xp": 150},
        "coding_bug_slayer": {"icon": "🔫", "name": "Bug Slayer", "desc": "Fixed 100 bugs", "xp": 250},
        "coding_bug_destroyer": {"icon": "☠", "name": "Bug Destroyer", "desc": "Fixed 500 bugs", "xp": 500},
        "coding_speed_coder": {"icon": "⚡", "name": "Speed Coder", "desc": "Generated 5 code snippets quickly", "xp": 200},
        "coding_architect": {"icon": "🏗", "name": "Architect", "desc": "Used /project to generate a full project", "xp": 300},
        "coding_test_master": {"icon": "🧪", "name": "Test Master", "desc": "Generated 50 unit tests", "xp": 250},
        "coding_polyglot": {"icon": "🔄", "name": "Polyglot", "desc": "Generated code in 5+ different languages", "xp": 300},
        
        "design_first_pixel": {"icon": "🎨", "name": "First Pixel", "desc": "Generated first UI design", "xp": 100},
        "design_color_master": {"icon": "🌈", "name": "Color Master", "desc": "Generated 20 color palettes", "xp": 150},
        "design_mobile_first": {"icon": "📱", "name": "Mobile First", "desc": "Made 10 responsive layouts", "xp": 200},
        "design_dark_lord": {"icon": "🌙", "name": "Dark Lord", "desc": "Added dark mode to 20 components", "xp": 200},
        "design_animator": {"icon": "✨", "name": "Animator", "desc": "Added animations to 15 components", "xp": 200},
        "design_system_builder": {"icon": "🏛", "name": "System Builder", "desc": "Generated a full design system", "xp": 300},
        
        "debug_first_fix": {"icon": "🔍", "name": "First Fix", "desc": "Fixed first bug", "xp": 100},
        "debug_detective": {"icon": "🕵", "name": "Detective", "desc": "Correctly identified root cause 25 times", "xp": 200},
        "debug_confidence_100": {"icon": "💯", "name": "Confidence 100", "desc": "Got 10 fixes with 95%+ confidence", "xp": 250},
        "debug_security_guard": {"icon": "🛡", "name": "Security Guard", "desc": "Found 5 security vulnerabilities", "xp": 300},
        "debug_optimizer": {"icon": "🚀", "name": "Optimizer", "desc": "Fixed 10 performance issues", "xp": 200},
        "debug_http_hero": {"icon": "🌐", "name": "HTTP Hero", "desc": "Solved 20 API/HTTP errors", "xp": 200},
        
        "streak_on_fire": {"icon": "🔥", "name": "On Fire", "desc": "7 day streak", "xp": 150},
        "streak_burning": {"icon": "♨", "name": "Burning", "desc": "30 day streak", "xp": 300},
        "streak_volcanic": {"icon": "🌋", "name": "Volcanic", "desc": "100 day streak", "xp": 500},
        "streak_solar": {"icon": "☀", "name": "Solar", "desc": "365 day streak", "xp": 1000},
        
        "special_ultra_master": {"icon": "🌌", "name": "Ultra Master", "desc": "Used all 4 models in one session", "xp": 200},
        "special_perfectionist": {"icon": "🎯", "name": "Perfectionist", "desc": "Got 50 /feedback good responses", "xp": 250},
        "special_scholar": {"icon": "📚", "name": "Scholar", "desc": "Taught Nexa 100 facts", "xp": 300},
        "special_duelist": {"icon": "🤝", "name": "Duelist", "desc": "Won 10 duels", "xp": 200},
        "special_champion": {"icon": "🏆", "name": "Champion", "desc": "Won 50 duels", "xp": 500},
        "special_all_rounder": {"icon": "⭐", "name": "All-Rounder", "desc": "Used every slash command at least once", "xp": 300},
        "special_tree_climber": {"icon": "🔓", "name": "Tree Climber", "desc": "Unlocked 5 skill tree nodes", "xp": 200},
        "special_nexa_legend": {"icon": "👑", "name": "Nexa Legend", "desc": "Reached Level 8 + earned 20 badges", "xp": 1000}
    }

    def __init__(self, storage_path: str = "user/badges.json"):
        self.storage_path = storage_path
        os.makedirs(os.path.dirname(storage_path), exist_ok=True)
        self.earned = self._load_data()

    def _load_data(self) -> Dict[str, str]:
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}  # badge_key -> date_earned

    def _save_data(self):
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(self.earned, f, indent=2)

    def check_badges(self, stats: Dict[str, Any], skill_tree_unlocked: List[str]) -> List[Dict[str, Any]]:
        new_badges = []
        
        # Mapping requirements
        reqs = {
            "coding_first_line": stats.get("code_runs", 0) >= 1 or stats.get("code_files_generated", 0) >= 1,
            "coding_bug_hunter": stats.get("bugs_fixed", 0) >= 10,
            "coding_bug_slayer": stats.get("bugs_fixed", 0) >= 100,
            "coding_bug_destroyer": stats.get("bugs_fixed", 0) >= 500,
            "coding_speed_coder": stats.get("speed_codes", 0) >= 5,
            "coding_architect": stats.get("projects_created", 0) >= 1,
            "coding_test_master": stats.get("tests_generated", 0) >= 50,
            "coding_polyglot": stats.get("languages_used", 0) >= 5,
            
            "design_first_pixel": stats.get("designs_created", 0) >= 1,
            "design_color_master": stats.get("palettes_created", 0) >= 20,
            "design_mobile_first": stats.get("layouts_created", 0) >= 10,
            "design_dark_lord": stats.get("dark_modes_created", 0) >= 20,
            "design_animator": stats.get("animations_created", 0) >= 15,
            "design_system_builder": stats.get("systems_created", 0) >= 1,
            
            "debug_first_fix": stats.get("bugs_fixed", 0) >= 1,
            "debug_detective": stats.get("root_causes_found", 0) >= 25,
            "debug_confidence_100": stats.get("high_confidence_fixes", 0) >= 10,
            "debug_security_guard": stats.get("security_bugs_fixed", 0) >= 5,
            "debug_optimizer": stats.get("perf_bugs_fixed", 0) >= 10,
            "debug_http_hero": stats.get("http_bugs_fixed", 0) >= 20,
            
            "streak_on_fire": stats.get("streak", 0) >= 7,
            "streak_burning": stats.get("streak", 0) >= 30,
            "streak_volcanic": stats.get("streak", 0) >= 100,
            "streak_solar": stats.get("streak", 0) >= 365,
            
            "special_ultra_master": stats.get("used_all_models", False),
            "special_perfectionist": stats.get("good_feedback_count", 0) >= 50,
            "special_scholar": stats.get("facts_taught", 0) >= 100,
            "special_duelist": stats.get("duels_won", 0) >= 10,
            "special_champion": stats.get("duels_won", 0) >= 50,
            "special_all_rounder": stats.get("unique_commands_used", 0) >= 30,
            "special_tree_climber": len(skill_tree_unlocked) >= 5,
            "special_nexa_legend": stats.get("level", 1) >= 8 and len(self.earned) >= 20
        }

        for key, met in reqs.items():
            if met and key not in self.earned:
                date_str = datetime.now().strftime("%Y-%m-%d")
                self.earned[key] = date_str
                cfg = self.BADGES_CONFIG[key]
                new_badges.append({
                    "key": key,
                    "name": cfg["name"],
                    "icon": cfg["icon"],
                    "desc": cfg["desc"],
                    "xp": cfg["xp"],
                    "date": date_str
                })

        if new_badges:
            self._save_data()
            
        return new_badges

    def get_badges_display(self, show_type: str = "all") -> str:
        lines = []
        if show_type == "recent":
            lines.append("🏆 RECENT BADGES EARNED")
            sorted_earned = sorted(self.earned.items(), key=lambda x: x[1], reverse=True)[:5]
            for key, date in sorted_earned:
                cfg = self.BADGES_CONFIG[key]
                lines.append(f"  {cfg['icon']} [bold]{cfg['name']}[/bold] - {cfg['desc']} (Earned: {date})")
        elif show_type == "locked":
            lines.append("🔒 LOCKED BADGES (HOW TO UNLOCK)")
            for key, cfg in self.BADGES_CONFIG.items():
                if key not in self.earned:
                    lines.append(f"  {cfg['icon']} [dim]{cfg['name']}[/dim] - {cfg['desc']} ({cfg['xp']} XP)")
        else:
            lines.append("🏆 ALL EARNED BADGES")
            for key, date in self.earned.items():
                cfg = self.BADGES_CONFIG[key]
                lines.append(f"  {cfg['icon']} [bold]{cfg['name']}[/bold] - {cfg['desc']} (Earned: {date})")
            if not self.earned:
                lines.append("  No badges earned yet. Complete challenges and code to unlock!")
                
        return "\n".join(lines)
