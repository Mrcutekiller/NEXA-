import json
import os
from datetime import datetime

class MemoryManager:
    def __init__(self, storage_path="nexa_memory.json"):
        self.storage_path = storage_path
        self.memory = self._load_memory()

    def _load_memory(self):
        defaults = {
            "user_traits": {
                "name": None,
                "age": None,
                "interests": [],
                "energy_level": "neutral",
                "dominant_mood": "neutral",
                "interaction_count": 0,
                "preferred_topics": [],
                "last_session_end": None
            },
            "chat_history": []
        }
        
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    loaded = json.load(f)
                    # Merge loaded data with defaults to avoid KeyErrors
                    if "user_traits" in loaded:
                        for key, value in defaults["user_traits"].items():
                            if key not in loaded["user_traits"]:
                                loaded["user_traits"][key] = value
                    else:
                        loaded["user_traits"] = defaults["user_traits"]
                    
                    if "chat_history" not in loaded:
                        loaded["chat_history"] = defaults["chat_history"]
                        
                    return loaded
            except:
                pass
        return defaults

    def save_memory(self):
        with open(self.storage_path, 'w') as f:
            json.dump(self.memory, f, indent=4)

    def analyze_and_update_vibe(self, user_input):
        traits = self.memory.get("user_traits", {})
        traits["interaction_count"] = traits.get("interaction_count", 0) + 1
        text = user_input.lower()
        
        # Simple vibe tracking
        if any(word in text for word in ["haha", "lol", "joke", "funny"]):
            traits["dominant_mood"] = "funny"
        elif any(word in text for word in ["work", "code", "serious", "build"]):
            traits["dominant_mood"] = "serious"
        elif any(word in text for word in ["love", "rizz", "date"]):
            traits["dominant_mood"] = "rizz-focused"
            
        # Track topics
        topics = {
            "coding": ["python", "js", "code", "programming", "bug"],
            "trading": ["crypto", "stock", "trade", "bitcoin"],
            "philosophy": ["life", "meaning", "why", "exist"]
        }
        
        preferred = traits.get("preferred_topics", [])
        for topic, keywords in topics.items():
            if any(k in text for k in keywords):
                if topic not in preferred:
                    preferred.append(topic)
        traits["preferred_topics"] = preferred
                    
        self.save_memory()

    def add_chat_turn(self, role, content):
        if "chat_history" not in self.memory:
            self.memory["chat_history"] = []
        self.memory["chat_history"].append({
            "role": role, 
            "content": content,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        # Removed the pop(0) to ensure full history is saved as requested
        self.save_memory()

    def get_context_summary(self):
        traits = self.memory.get("user_traits", {})
        summary = {
            "name": traits.get("name", "Human"),
            "count": traits.get("interaction_count", 0),
            "vibe": traits.get("dominant_mood", "neutral"),
            "topics": traits.get("preferred_topics", []),
            "new_session": self._is_new_session_reaction_needed()
        }
        return summary

    def _is_new_session_reaction_needed(self):
        # If we have history but the session just started
        return len(self.memory["chat_history"]) > 0 and self.memory["user_traits"]["interaction_count"] > 5

    def mark_session_end(self):
        self.memory["user_traits"]["last_session_end"] = os.times().elapsed
        self.save_memory()
