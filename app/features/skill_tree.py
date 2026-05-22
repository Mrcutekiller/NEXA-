# app/features/skill_tree.py
import os
import json
from typing import Dict, List, Any, Tuple

class SkillTreeManager:
    def __init__(self, storage_path: str = "user/skill_tree.json"):
        self.storage_path = storage_path
        os.makedirs(os.path.dirname(storage_path), exist_ok=True)
        self.unlocked_nodes = self._load_data()

    def _load_data(self) -> List[str]:
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return ["power_lvl1"]  # default unlocked

    def _save_data(self):
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(self.unlocked_nodes, f, indent=2)

    def check_unlocks(self, level: int, model_usages: Dict[str, int], streak: int) -> List[str]:
        new_unlocks = []
        
        # Branch 1: Power Unlocks (levels)
        power_nodes = [
            ("power_lvl1", 1, "Basic chat & arithmetic"),
            ("power_lvl2", 2, "/notebook note saving"),
            ("power_lvl3", 3, "/explain pro"),
            ("power_lvl4", 4, "/project workspace manager"),
            ("power_lvl5", 5, "/brainstorm dynamic ideas"),
            ("power_lvl6", 6, "/ultra turbo long outputs"),
            ("power_lvl7", 7, "/duel multiplayer mode"),
            ("power_lvl8", 8, "/nexa god mode unlock")
        ]
        for node_id, req_lvl, name in power_nodes:
            if level >= req_lvl and node_id not in self.unlocked_nodes:
                self.unlocked_nodes.append(node_id)
                new_unlocks.append(name)

        # Branch 2: Specialist Unlocks (50x model usage)
        specialist_nodes = [
            ("spec_code", "code", "/snippet library"),
            ("spec_design", "design", "/brand kit colors"),
            ("spec_fix", "fix", "/bug history log"),
            ("spec_ultra", "ultra", "/deep think mode")
        ]
        for node_id, model_key, name in specialist_nodes:
            usage = model_usages.get(model_key, 0)
            if usage >= 50 and node_id not in self.unlocked_nodes:
                self.unlocked_nodes.append(node_id)
                new_unlocks.append(name)

        # Branch 3: Streak Unlocks (days)
        streak_nodes = [
            ("streak_7", 7, "Custom terminal themes"),
            ("streak_30", 30, "Voice persona custom names"),
            ("streak_100", 100, "/nexa legacy exporter")
        ]
        for node_id, req_streak, name in streak_nodes:
            if streak >= req_streak and node_id not in self.unlocked_nodes:
                self.unlocked_nodes.append(node_id)
                new_unlocks.append(name)

        if new_unlocks:
            self._save_data()
            
        return new_unlocks

    def is_unlocked(self, skill_name: str) -> bool:
        skill_map = {
            "notebook": "power_lvl2",
            "explain_pro": "power_lvl3",
            "project": "power_lvl4",
            "brainstorm": "power_lvl5",
            "ultra_turbo": "power_lvl6",
            "duel": "power_lvl7",
            "nexa_god": "power_lvl8",
            "snippets": "spec_code",
            "brand_kit": "spec_design",
            "bug_history": "spec_fix",
            "deep_think": "spec_ultra",
            "custom_themes": "streak_7",
            "voice_persona": "streak_30",
            "nexa_legacy": "streak_100"
        }
        node = skill_map.get(skill_name)
        if not node:
            return True  # basic commands are always unlocked
        return node in self.unlocked_nodes

    def get_skill_tree_text(self, level: int, model_usages: Dict[str, int], streak: int) -> str:
        self.check_unlocks(level, model_usages, streak)
        
        def status(node_id: str) -> str:
            return "★ UNLOCKED" if node_id in self.unlocked_nodes else "🔒 LOCKED"

        res = f"""
                    [NEXA SKILL TREE PROGRESSION]

BRANCH 1: POWER UNLOCKS (XP Levels)
─────────────────────────────────────────────────────────────────
Lv 1  {status("power_lvl1")}  - Basic Chat & Arithmetic
Lv 2  {status("power_lvl2")}  - /notebook (Save/Search Notes)
Lv 3  {status("power_lvl3")}  - /explain pro (Expert depth explanations)
Lv 4  {status("power_lvl4")}  - /project (Multi-workspace project system)
Lv 5  {status("power_lvl5")}  - /brainstorm (Generate 10 dynamic ideas)
Lv 6  {status("power_lvl6")}  - /ultra turbo (2x context length response)
Lv 7  {status("power_lvl7")}  - /duel (Challenge other users p2p)
Lv 8  {status("power_lvl8")}  - /nexa god (Max level context control)

BRANCH 2: SPECIALIST UNLOCKS (Usage Thresholds)
─────────────────────────────────────────────────────────────────
Code   {model_usages.get('code', 0)}/50  {status("spec_code")}  - /snippet library
Design {model_usages.get('design', 0)}/50  {status("spec_design")}  - /brand kit colors
Fix    {model_usages.get('fix', 0)}/50  {status("spec_fix")}  - /bug history log
Ultra  {model_usages.get('ultra', 0)}/50  {status("spec_ultra")}  - /deep think mode

BRANCH 3: STREAK UNLOCKS (Daily Activity Streaks)
─────────────────────────────────────────────────────────────────
Streak 7d   {streak}/7   {status("streak_7")}  - Custom terminal theme creator
Streak 30d  {streak}/30  {status("streak_30")}  - Voice voice personas name edit
Streak 100d {streak}/100 {status("streak_100")}  - /nexa legacy journey exporter
"""
        return res.strip()
