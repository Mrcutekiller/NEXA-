# app/features/personas.py
from typing import Dict, List, Any

class NexaPersonaManager:
    PERSONAS = {
        "code": {
            "name": "Atlas",
            "desc": "Deep, calm, methodical — like a senior engineer",
            "rate": 140,
            "pitch": 0.9,
            "personality": "Technical, measured, never rushes"
        },
        "design": {
            "name": "Luna",
            "desc": "Warm, expressive, creative energy",
            "rate": 175,
            "pitch": 1.1,
            "personality": "Enthusiastic, encouraging, artistic"
        },
        "fix": {
            "name": "Rex",
            "desc": "Confident, detective-like, reassuring",
            "rate": 155,
            "pitch": 0.95,
            "personality": "Analytical, confident, never panics"
        },
        "ultra": {
            "name": "Nova",
            "desc": "Dynamic, shifts tone to match the task",
            "rate": 160,
            "pitch": 1.0,
            "personality": "Versatile, wise, powerful"
        }
    }

    def __init__(self):
        self.active_persona = "Nova"
        self.custom_settings = {}

    def get_persona(self, model_key: str) -> Dict[str, Any]:
        key = model_key.lower().strip()
        # Fallback mapping
        if key not in self.PERSONAS:
            key = "ultra"
        
        cfg = self.PERSONAS[key].copy()
        if self.custom_settings:
            cfg.update(self.custom_settings)
        return cfg

    def set_custom_settings(self, rate: int, pitch: float):
        self.custom_settings = {"rate": rate, "pitch": pitch}

    def reset_persona(self):
        self.custom_settings = {}

    def detect_user_emotion(self, message: str, last_5_messages: List[str]) -> str:
        msg = message.lower()
        
        # Frustration signals
        frustration_signals = [
            "why isn't", "not working", "broken", "stupid", "ugh", "again",
            "still", "nothing works", "i give up", "what the", "seriously", "hate"
        ]
        
        # Urgency signals
        urgency_signals = [
            "urgent", "asap", "quickly", "fast", "deadline", "need now",
            "hurry", "emergency", "critical", "immediately"
        ]
        
        # Confusion signals
        confusion_signals = [
            "i don't understand", "what does", "confused", "lost",
            "what is", "explain", "don't get it", "huh", "what?"
        ]
        
        if any(s in msg for s in frustration_signals):
            return "frustrated"
        if any(s in msg for s in urgency_signals):
            return "urgent"
        if any(s in msg for s in confusion_signals):
            return "confused"
            
        # Check historical context
        hist_text = " ".join(last_5_messages).lower()
        if any(s in hist_text for s in frustration_signals):
            return "frustrated"
            
        return "neutral"

    def adapt_response_to_emotion(self, response: str, emotion: str) -> str:
        if emotion == "frustrated":
            return f"I hear you — let's fix this step by step.\n\n{response}"
        elif emotion == "urgent":
            # Strip extra conversational fluff
            clean_resp = response
            if "\n" in response:
                # Keep first paragraph or direct answer
                parts = response.split("\n\n")
                clean_resp = parts[0] if len(parts) > 0 else response
            return f"Quick answer:\n{clean_resp}\n\n(Ask me to explain if needed)"
        elif emotion == "confused":
            # Add an ELI5 simple explanation block at the end
            lines = response.split("\n")
            summary = lines[0] if lines else response
            return f"{response}\n\nSimple version: Basically, we want to make sure the inputs are checked before they run, like looking both ways before crossing a street."
        return response
