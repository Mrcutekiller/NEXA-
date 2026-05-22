# app/features/narrate.py
import re
import threading
import time
from typing import Dict, List, Any, Optional, Callable

class NexaNarrate:
    def __init__(self):
        self.engine = None
        self.is_speaking = False
        self.speed = 150
        self.stop_event = threading.Event()
        self.thread: Optional[threading.Thread] = None

    def _init_engine(self):
        if not self.engine:
            try:
                import pyttsx3
                self.engine = pyttsx3.init()
                self.engine.setProperty('rate', self.speed)
            except Exception:
                self.engine = None

    def stop(self):
        self.stop_event.set()
        self.is_speaking = False
        if self.engine:
            try:
                self.engine.stop()
            except Exception:
                pass

    def set_speed(self, speed_val: float):
        # speed_val is e.g. 0.5 to 2.0. Base rate is 150.
        self.speed = int(150 * speed_val)
        if self.engine:
            try:
                self.engine.setProperty('rate', self.speed)
            except Exception:
                pass

    def extract_key_points(self, text: str) -> List[str]:
        # Extract sentences that look like key points
        sentences = re.split(r'(?<=[.!?])\s+', text)
        points = []
        for s in sentences:
            s_clean = s.strip()
            if any(w in s_clean.lower() for w in ["must", "should", "architect", "key", "important", "feature", "first", "never", "always", "transformer", "nexa"]):
                if len(s_clean) > 20 and len(s_clean) < 120 and s_clean not in points:
                    points.append(s_clean)
        if not points:
            # Fallback: take first two sentences
            points = [s.strip() for s in sentences[:2] if len(s.strip()) > 10]
        return points[:5]

    def narrate_text(self, text: str, callback: Callable[[str, List[str], float], None]):
        """
        Starts narration in a separate thread.
        callback parameters: current_sentence, key_points_so_far, progress_fraction
        """
        self.stop()
        self.stop_event.clear()
        self._init_engine()
        self.is_speaking = True
        
        self.thread = threading.Thread(target=self._run_narration, args=(text, callback), daemon=True)
        self.thread.start()

    def _run_narration(self, text: str, callback: Callable[[str, List[str], float], None]):
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
        key_points = self.extract_key_points(text)
        points_discovered = []
        
        total_sents = len(sentences)
        for idx, sent in enumerate(sentences):
            if self.stop_event.is_set():
                break

            # Check if this sentence contains any key points
            for pt in key_points:
                if pt in sent and pt not in points_discovered:
                    points_discovered.append(pt)

            progress = (idx + 1) / total_sents
            callback(sent, points_discovered, progress)

            if self.engine:
                try:
                    self.engine.say(sent)
                    self.engine.runAndWait()
                except Exception:
                    # Fallback timer based on words length
                    words_count = len(sent.split())
                    time.sleep(words_count * 0.4)
            else:
                # Timer fallback simulation
                words_count = len(sent.split())
                time.sleep(words_count * 0.4)
                
        self.is_speaking = False
        callback("[Finished Narration]", points_discovered, 1.0)
stream = None
