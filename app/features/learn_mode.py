# app/features/learn_mode.py
import os
import json
from datetime import datetime
from typing import Dict, Any, List

class NexaLearnMode:
    def __init__(self, profile_path: str = "user/profile.json"):
        self.profile_path = profile_path
        os.makedirs(os.path.dirname(profile_path), exist_ok=True)
        self.profile_data = self._load_profile()

    def _load_profile(self) -> Dict[str, Any]:
        if os.path.exists(self.profile_path):
            try:
                with open(self.profile_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "name": "Human",
            "level": 1,
            "total_xp": 0,
            "streak": 0,
            "learned_about_user": {
                "language_preference": None,
                "skill_level": None,
                "common_mistakes": [],
                "favorite_topics": [],
                "response_length_preference": "detailed",
                "working_hours": [],
                "communication_style": "casual"
            }
        }

    def _save_profile(self):
        with open(self.profile_path, "w", encoding="utf-8") as f:
            json.dump(self.profile_data, f, indent=2, ensure_ascii=False)

    def analyze_session(self, messages: List[Dict[str, str]]):
        """
        Analyzes the last few messages in the conversation to learn about the user.
        Format of messages: [{"role": "user", "content": "..."}, {"role": "bot", "content": "..."}]
        """
        learned = self.profile_data.setdefault("learned_about_user", {
            "language_preference": None,
            "skill_level": None,
            "common_mistakes": [],
            "favorite_topics": [],
            "response_length_preference": "detailed",
            "working_hours": [],
            "communication_style": "casual"
        })

        # Track user message strings
        user_msgs = [m["content"] for m in messages if m.get("role") == "user"]
        full_text = " ".join(user_msgs).lower()

        # 1. Language preference detection
        for lang in ["python", "javascript", "typescript", "c++", "rust", "java", "html", "css", "go", "bash"]:
            if f"in {lang}" in full_text or f"using {lang}" in full_text or f"write {lang}" in full_text:
                learned["language_preference"] = lang.capitalize()

        # 2. Skill level estimation
        if any(w in full_text for w in ["how to run", "what is", "syntax error", "install"]):
            learned["skill_level"] = "beginner"
        elif any(w in full_text for w in ["optimize", "architect", "benchmark", "decorator", "generic", "multithread"]):
            learned["skill_level"] = "advanced"
        elif learned["skill_level"] is None:
            learned["skill_level"] = "intermediate"

        # 3. Response length preference
        if any(w in full_text for w in ["summarize", "brief", "short", "quick", "tl;dr", "just code"]):
            learned["response_length_preference"] = "short"
        elif any(w in full_text for w in ["explain in detail", "detailed", "step by step", "elaborate"]):
            learned["response_length_preference"] = "detailed"

        # 4. Favorite topics detection
        topics = learned.setdefault("favorite_topics", [])
        if "api" in full_text or "rest" in full_text or "fastapi" in full_text:
            if "Web APIs" not in topics: topics.append("Web APIs")
        if "data" in full_text or "pandas" in full_text or "plot" in full_text:
            if "Data Science" not in topics: topics.append("Data Science")
        if "css" in full_text or "layout" in full_text or "flexbox" in full_text:
            if "UI Design" not in topics: topics.append("UI Design")
        if "test" in full_text or "pytest" in full_text:
            if "Testing" not in topics: topics.append("Testing")

        # 5. Communication style
        if any(w in full_text for w in ["please", "sir", "thank you", "sincerely"]):
            learned["communication_style"] = "formal"
        elif any(w in full_text for w in ["bro", "hey", "yo", "lol", "lmao", "wtf"]):
            learned["communication_style"] = "casual"

        # 6. Working hours
        hour = datetime.now().hour
        working_hours = learned.setdefault("working_hours", [])
        time_slot = f"{hour:02d}:00"
        if time_slot not in working_hours:
            working_hours.append(time_slot)

        self._save_profile()

    def get_user_insight(self) -> str:
        learned = self.profile_data.get("learned_about_user", {})
        pref_lang = learned.get("language_preference") or "no preference"
        skill = learned.get("skill_level") or "unknown"
        fav_topics = ", ".join(learned.get("favorite_topics", [])) or "None"
        
        return (
            f"User Profile Insights:\n"
            f"- Preferred Language: {pref_lang}\n"
            f"- Skill Level: {skill}\n"
            f"- Favorite Topics: {fav_topics}\n"
            f"- Communication Style: {learned.get('communication_style', 'casual')}"
        )
