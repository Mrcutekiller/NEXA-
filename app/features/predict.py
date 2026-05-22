# app/features/predict.py
from typing import List, Dict, Any

class NexaPredict:
    def __init__(self, history_manager=None):
        self.history_manager = history_manager
        self.common_questions = {
            "code": [
                "how do i write a python function to read a file?",
                "how do i parse json in javascript?",
                "how do i implement binary search in c++?",
                "how do i write a unit test in python?",
                "how do i run a bash script from command line?"
            ],
            "design": [
                "how do i build a responsive grid layout?",
                "how do i create a dark mode css palette?",
                "how do i add hover scale animations in vanilla css?",
                "how do i design a clean landing page layout?",
                "how do i write svg code for a home icon?"
            ],
            "fix": [
                "how do i fix a typeerror: 'noneval' is not callable?",
                "how do i fix a null pointer error in python?",
                "how do i fix a broken css flexbox layout?",
                "how do i fix a 404 error in my fastapi?",
                "how do i fix a permissions denied terminal error?"
            ],
            "ultra": [
                "how do i design an api server system architecture?",
                "how do i build a local rag document search?",
                "how do i implement a plugin framework in python?",
                "how do i create a multiplayer local network room?",
                "how do i encrypt a database with aes-256?"
            ]
        }

    def get_predictions(self, partial_input: str, context: Dict[str, Any]) -> List[str]:
        if not partial_input or len(partial_input.strip()) < 3:
            return []
            
        partial_lower = partial_input.lower()
        predictions = []
        
        # 1. Search past questions (from history if available)
        past_questions = []
        if self.history_manager and hasattr(self.history_manager, "get_all_questions"):
            try:
                past_questions = self.history_manager.get_all_questions()
            except Exception:
                pass
        
        for q in past_questions:
            if q.lower().startswith(partial_lower) and q not in predictions:
                predictions.append(q)

        # 2. Search common questions related to current model mode
        model = context.get("current_model", "ultra").lower()
        common = self.common_questions.get(model, self.common_questions["ultra"])
        for q in common:
            if q.lower().startswith(partial_lower) and q not in predictions:
                predictions.append(q)

        # 3. Search common questions from other modes as fallback
        for mode, qs in self.common_questions.items():
            if mode != model:
                for q in qs:
                    if q.lower().startswith(partial_lower) and q not in predictions:
                        predictions.append(q)

        return predictions[:3]  # Max 3 predictions
