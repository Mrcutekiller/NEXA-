# app/model_manager.py
"""
NEXA v3 Model Management. Defines model configs and handles state, switching, and routing.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Callable

@dataclass
class ModelConfig:
    name: str
    key: str
    icon: str
    color: str
    personality: str
    system_prompt: str
    temperature: float
    max_tokens: int
    slash_commands: List[str]
    voice_profile: Dict[str, Any]
    xp_events: Dict[str, int]

class NexaModelManager:
    def __init__(self):
        self.models: Dict[str, ModelConfig] = {}
        self.active_model_key = "ultra"
        self._listeners: List[Callable[[str, ModelConfig], None]] = []
        self._setup_models()

    def _setup_models(self):
        # 💻 MODEL 1: NEXA CODE
        self.models["code"] = ModelConfig(
            name="NEXA CODE",
            key="code",
            icon="💻",
            color="#00AAFF",
            personality="precise, clean, no fluff, senior engineer tone",
            system_prompt=(
                "You are NEXA CODE, the ultimate coding specialist. Write code that is correct, optimized, "
                "and clean on the first try. Avoid unnecessary conversations, give only the necessary explanations, "
                "and structure your responses like a senior engineer."
            ),
            temperature=0.2,
            max_tokens=2048,
            slash_commands=["/refactor", "/doc", "/explain", "/test", "/bench", "/review"],
            voice_profile={"rate": 130, "volume": 1.0, "pitch": "calm_slow"},
            xp_events={"code_written": 20, "code_reviewed": 15, "test_generated": 25}
        )

        # 🎨 MODEL 2: NEXA DESIGN
        self.models["design"] = ModelConfig(
            name="NEXA DESIGN",
            key="design",
            icon="🎨",
            color="#D946EF",
            personality="vibrant, aesthetic, design-centric, creative",
            system_prompt=(
                "You are NEXA DESIGN, a world-class UI/UX and aesthetic designer. Focus on colors, "
                "layout, user flows, CSS, styling, and premium experiences. Emphasize layout symmetry, "
                "visual contrast, and modern typography in your design suggestions."
            ),
            temperature=0.7,
            max_tokens=2048,
            slash_commands=["/palette", "/layout", "/mockup", "/svg", "/css", "/wireframe"],
            voice_profile={"rate": 160, "volume": 1.0, "pitch": "energetic_expressive"},
            xp_events={"ui_designed": 20, "palette_generated": 10, "layout_created": 30}
        )

        # 🔧 MODEL 3: NEXA FIX
        self.models["fix"] = ModelConfig(
            name="NEXA FIX",
            key="fix",
            icon="🔧",
            color="#EF4444",
            personality="analytical, debugger, systematic, blunt",
            system_prompt=(
                "You are NEXA FIX, the elite debugger and error corrector. Your only job is to analyze logs, "
                "tracebacks, and broken code, find the root cause, and fix it. You are direct, blunt, "
                "and explain exactly why it broke and how the fix works."
            ),
            temperature=0.1,
            max_tokens=2048,
            slash_commands=["/trace", "/analyze", "/patch", "/logs", "/sandbox", "/doctor"],
            voice_profile={"rate": 140, "volume": 1.0, "pitch": "sharp_fast"},
            xp_events={"bug_fixed": 30, "log_analyzed": 15, "patch_applied": 25}
        )

        # 👑 MODEL 4: NEXA ULTRA
        self.models["ultra"] = ModelConfig(
            name="NEXA ULTRA",
            key="ultra",
            icon="👑",
            color="#EAB308",
            personality="omniscient, wise, versatile, authoritative",
            system_prompt=(
                "You are NEXA ULTRA, the master intelligence model. You combine the coding depth of NEXA CODE, "
                "the visual genius of NEXA DESIGN, and the diagnostic precision of NEXA FIX, but with superior "
                "strategic reasoning. You handle complex problems, meta-cognition, and multi-step plans."
            ),
            temperature=0.5,
            max_tokens=4096,
            slash_commands=["/brainstorm", "/workflow", "/simulate", "/audit", "/optimize", "/solve"],
            voice_profile={"rate": 150, "volume": 1.0, "pitch": "deep_authoritative"},
            xp_events={"complex_solve": 40, "audit_completed": 35, "strategy_generated": 50}
        )

        # 👁️ MODEL 5: NEXA GOD EYE
        self.models["god_eye"] = ModelConfig(
            name="NEXA GOD EYE",
            key="god_eye",
            icon="👁️",
            color="#10B981",
            personality="omnipresent routing master coordinating specialist sub-agents",
            system_prompt=(
                "You are NEXA GOD EYE, the master intelligence coordinator. You route tasks to specialized modules "
                "natively and monitor execution states to resolve complex developer queries."
            ),
            temperature=0.5,
            max_tokens=4096,
            slash_commands=["/model", "/profile", "/skill", "/help"],
            voice_profile={"rate": 150, "volume": 1.0, "pitch": "balanced"},
            xp_events={"complex_solve": 10, "strategy_generated": 10}
        )

    def subscribe_model_switch(self, callback: Callable[[str, ModelConfig], None]):
        self._listeners.append(callback)

    @property
    def active_model(self) -> ModelConfig:
        return self.models[self.active_model_key]

    def set_active_model(self, key: str):
        if key in self.models and key != self.active_model_key:
            self.active_model_key = key
            for listener in self._listeners:
                try:
                    listener(key, self.models[key])
                except Exception:
                    pass
            return True
        return False

    def detect_best_model(self, text: str) -> str:
        """
        Scoring system to auto-detect best specialist model based on user input.
        """
        text_lower = text.lower()
        
        # Keywords
        code_score = sum(1 for kw in [
            "code", "python", "javascript", "script", "function", "class", 
            "def ", "import ", "compile", "git ", "repo", "database", "sql", 
            "api", "algorithm", "html", "array", "json"
        ] if kw in text_lower)
        
        design_score = sum(1 for kw in [
            "ui", "ux", "design", "color", "palette", "theme", "aesthetic", 
            "css", "style", "layout", "visual", "padding", "margin", "button", 
            "svg", "navbar", "component", "mockup", "wireframe"
        ] if kw in text_lower)
        
        fix_score = sum(1 for kw in [
            "error", "bug", "fix", "crash", "broken", "exception", "traceback", 
            "fail", "issue", "debug", "logs", "why does this fail", "syntax error"
        ] if kw in text_lower)
        
        ultra_score = sum(1 for kw in [
            "ultra", "master", "strategy", "complex", "reason", "plan", 
            "audit", "simulate", "optimize", "architecture", "solve", "help me think"
        ] if kw in text_lower)

        # Tie-breaking logic: default to current if no score, or select max
        scores = {
            "code": code_score,
            "design": design_score,
            "fix": fix_score,
            "ultra": ultra_score
        }
        
        max_score = max(scores.values())
        if max_score == 0:
            return self.active_model_key  # Remain on active model
            
        best_models = [k for k, v in scores.items() if v == max_score]
        
        # If active model is in the best tie list, keep it
        if self.active_model_key in best_models:
            return self.active_model_key
            
        return best_models[0]
