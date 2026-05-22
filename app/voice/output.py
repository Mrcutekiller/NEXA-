# app/voice/output.py
"""
Voice output engine using pyttsx3.
Handles markdown/code stripping, per-model profiles, and asynchronous speaking.
"""

import pyttsx3
import re
import threading
import queue
from typing import Dict, Any

class NexaVoiceOutput:
    def __init__(self):
        self.engine = None
        self.speech_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.speak_thread = None
        self._init_engine()
        self._start_worker()

    def _init_engine(self):
        try:
            self.engine = pyttsx3.init()
            # Set default volume
            self.engine.setProperty("volume", 1.0)
        except Exception as e:
            print(f"[Voice Output Init Error] {e}")
            self.engine = None

    def _start_worker(self):
        def worker():
            while not self.stop_event.is_set():
                try:
                    text, profile = self.speech_queue.get(timeout=0.1)
                except queue.Empty:
                    continue

                if not self.engine:
                    self.speech_queue.task_done()
                    continue

                try:
                    # Apply voice profile configuration
                    rate = profile.get("rate", 150)
                    volume = profile.get("volume", 1.0)
                    
                    self.engine.setProperty("rate", rate)
                    self.engine.setProperty("volume", volume)
                    
                    # In pyttsx3, we can try to select a voice.
                    # Typically, index 0 is male, index 1 is female.
                    # Let's map model pitch/styles to available voices
                    voices = self.engine.getProperty("voices")
                    pitch = profile.get("pitch", "calm_slow")
                    
                    if len(voices) > 1:
                        if pitch == "energetic_expressive" or pitch == "sharp_fast":
                            self.engine.setProperty("voice", voices[1].id) # Often female/high pitch
                        else:
                            self.engine.setProperty("voice", voices[0].id) # Often male/deep voice

                    # Speak
                    self.engine.say(text)
                    self.engine.runAndWait()
                except Exception as e:
                    print(f"[Voice Output Speaking Error] {e}")
                finally:
                    self.speech_queue.task_done()

        self.speak_thread = threading.Thread(target=worker, daemon=True)
        self.speak_thread.start()

    def clean_text_for_speech(self, text: str) -> str:
        """
        Strips markdown formatting, code blocks, URLs, and emojis to make speech sound natural.
        """
        # Remove code blocks entirely
        text = re.sub(r"```[\s\S]*?```", "[code block omitted]", text)
        # Remove inline backticks
        text = re.sub(r"`([^`]+)`", r"\1", text)
        # Remove markdown bold/italics
        text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
        text = re.sub(r"\*([^*]+)\*", r"\1", text)
        # Remove markdown links, keep label
        text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
        # Remove HTML tags
        text = re.sub(r"<[^>]+>", "", text)
        # Remove URLs
        text = re.sub(r"https?://\S+", "", text)
        # Remove emojis (unicode characters outside typical text ranges)
        text = text.encode("ascii", "ignore").decode("ascii")
        # Remove excessive whitespace
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def speak(self, raw_text: str, profile: Dict[str, Any]):
        """
        Strips markdown and queues the text for speaking in the background.
        """
        cleaned_text = self.clean_text_for_speech(raw_text)
        if cleaned_text:
            self.speech_queue.put((cleaned_text, profile))

    def stop(self):
        """
        Clears the speak queue and interrupts the engine.
        """
        # Clear queue
        while not self.speech_queue.empty():
            try:
                self.speech_queue.get_nowait()
                self.speech_queue.task_done()
            except queue.Empty:
                break
        
        # Stop pyttsx3 engine
        if self.engine:
            try:
                self.engine.stop()
            except Exception:
                pass

    def shutdown(self):
        self.stop_event.set()
        self.stop()
        if self.speak_thread:
            self.speak_thread.join(timeout=1.0)
