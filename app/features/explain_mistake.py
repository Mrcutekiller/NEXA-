# app/features/explain_mistake.py
import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

class NexaMistakeLog:
    def __init__(self, storage_path: str = "user/mistakes.json"):
        self.storage_path = storage_path
        os.makedirs(os.path.dirname(storage_path), exist_ok=True)
        self.mistakes = self._load_mistakes()

    def _load_mistakes(self) -> List[Dict[str, Any]]:
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def _save_mistakes(self):
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(self.mistakes, f, indent=2, ensure_ascii=False)

    def log_mistake(self, title: str, description: str, lesson: str, code_before: str, code_after: str, topic: str = "general") -> Dict[str, Any]:
        mistake_id = f"mistake_{len(self.mistakes) + 1:03d}"
        mistake = {
            "id": mistake_id,
            "title": title,
            "description": description,
            "lesson": lesson,
            "code_before": code_before,
            "code_after": code_after,
            "topic": topic,
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        self.mistakes.append(mistake)
        self._save_mistakes()
        return mistake

    def get_mistakes(self, topic: Optional[str] = None) -> List[Dict[str, Any]]:
        if topic:
            return [m for m in self.mistakes if m["topic"].lower() == topic.lower()]
        return self.mistakes

    def clear_mistakes(self):
        self.mistakes = []
        self._save_mistakes()

    def format_bug_fix(self, what_wrong: str, why_hit: str, fix: str, lesson: str, bad_pattern: str, good_pattern: str) -> str:
        """
        Formats the standard output response when Nexa Fix corrects a bug.
        """
        return f"""
WHAT WENT WRONG
───────────────
{what_wrong}

WHY YOU HIT THIS BUG
────────────────────
{why_hit}

THE FIX
───────
{fix}

THE LESSON
──────────
{lesson}

PATTERN TO AVOID
────────────────
BAD PATTERN:
{bad_pattern}

GOOD PATTERN:
{good_pattern}

Save this lesson? Type: /note Mistake: {what_wrong[:20]} | {lesson} | mistake
"""
