# app/features/challenges.py
"""
Daily Challenge System.
Provides per-model interactive challenges, hints, and checks user solutions.
"""

import random
from typing import Dict, Any, List, Optional

CHALLENGES = {
    "code": [
        {
            "id": "code_1",
            "desc": "Write a recursive Fibonacci function with memoization in Python.",
            "hints": ["Use a dictionary to store cached values.", "Base cases are n <= 1."],
            "keywords": ["def ", "memo", "fib", "return"],
            "xp": 100
        },
        {
            "id": "code_2",
            "desc": "Write a Python decorator that measures and prints execution time of a function.",
            "hints": ["Import the time module.", "Use *args and **kwargs in the wrapper."],
            "keywords": ["import time", "wrapper", "decorator", "func", "return"],
            "xp": 100
        }
    ],
    "design": [
        {
            "id": "design_1",
            "desc": "Design a 3-column responsive layout using CSS Grid.",
            "hints": ["Use 'display: grid;'.", "Use 'grid-template-columns: repeat(3, 1fr);' or media queries."],
            "keywords": ["display: grid", "grid-template-columns", "repeat", "fr"],
            "xp": 100
        },
        {
            "id": "design_2",
            "desc": "Generate a WCAG 2.1 AA compliant color scheme with a primary blue (#0055ff). What is the minimum contrast background?",
            "hints": ["WCAG AA contrast requires at least 4.5:1 ratio.", "A very light gray or pure white background will work."],
            "keywords": ["contrast", "#ffffff", "white", "ratio"],
            "xp": 100
        }
    ],
    "fix": [
        {
            "id": "fix_1",
            "desc": "Explain and fix the bug in: d = {}; print(d['key']) when key is absent.",
            "hints": ["Use d.get('key', default) instead of bracket lookup.", "Or wrap it in try-except KeyError."],
            "keywords": ["get(", "try", "keyerror", "except"],
            "xp": 100
        },
        {
            "id": "fix_2",
            "desc": "Fix a potential division by zero error in a function: def avg(lst): return sum(lst) / len(lst)",
            "hints": ["Check if the list is empty first.", "Check if len(lst) == 0 before division."],
            "keywords": ["if not", "len(", "== 0", "empty"],
            "xp": 100
        }
    ],
    "ultra": [
        {
            "id": "ultra_1",
            "desc": "Draft a multi-layer optimization plan for a slow SQLite database query in a chat app.",
            "hints": ["Use indexes on frequently queried fields like user_id.", "Optimize queries with LIMIT and avoid SELECT *."],
            "keywords": ["index", "query", "select", "explain query plan", "limit"],
            "xp": 150
        }
    ]
}

class ChallengeManager:
    def __init__(self, stats_manager=None):
        self.stats_manager = stats_manager

    def get_challenge(self, model_key: str) -> Dict[str, Any]:
        """
        Retrieves the daily challenge for a specific model key.
        """
        model_challenges = CHALLENGES.get(model_key, CHALLENGES["ultra"])
        # We can select based on day of month, or just randomize
        import datetime
        day = datetime.datetime.now().day
        idx = day % len(model_challenges)
        challenge = model_challenges[idx]
        
        # Check if already completed in stats
        completed = False
        if self.stats_manager:
            completed_list = self.stats_manager.stats.get("completed_challenges", [])
            completed = challenge["id"] in completed_list
            
        return {
            "id": challenge["id"],
            "description": challenge["desc"],
            "hints": challenge["hints"],
            "xp": challenge["xp"],
            "completed": completed,
            "keywords": challenge["keywords"]
        }

    def verify_solution(self, model_key: str, answer_text: str) -> Tuple[bool, str]:
        """
        Verifies the user's solution. Returns (success, feedback_message).
        """
        challenge = self.get_challenge(model_key)
        if challenge["completed"]:
            return False, "This challenge has already been completed today!"

        # Simple verification check based on keywords
        missing_kw = [kw for kw in challenge["keywords"] if kw not in answer_text.lower()]
        
        if not missing_kw:
            # Mark as completed
            if self.stats_manager:
                if "completed_challenges" not in self.stats_manager.stats:
                    self.stats_manager.stats["completed_challenges"] = []
                self.stats_manager.stats["completed_challenges"].append(challenge["id"])
                self.stats_manager.stats["challenges_completed_count"] += 1
                self.stats_manager.add_xp("challenge_completed")
                # Add extra challenge xp
                self.stats_manager.stats["total_xp"] += challenge["xp"]
                self.stats_manager.save_stats()
            return True, f"Challenge completed! +{challenge['xp']} XP awarded."
        else:
            return False, f"Check your code/explanation. Make sure you address all criteria. (Hint: missing components)."
