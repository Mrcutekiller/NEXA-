# app/voice/input.py
"""
Voice input capture using SpeechRecognition (and optionally faster-whisper).
Includes VAD, push-to-talk, and dynamic fallback.
"""

import threading
import time
from typing import Optional, Callable

# Dynamic imports with graceful fallbacks
SPEECH_REC_AVAILABLE = False
try:
    import speech_recognition as sr
    SPEECH_REC_AVAILABLE = True
except ImportError:
    pass

FASTER_WHISPER_AVAILABLE = False
try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
except ImportError:
    pass


class NexaVoiceInput:
    def __init__(self, use_whisper: bool = False):
        self.use_whisper = use_whisper and FASTER_WHISPER_AVAILABLE
        self.recognizer = None
        self.microphone = None
        self.whisper_model = None
        self.is_listening = False
        self._init_audio()

    def _init_audio(self):
        if SPEECH_REC_AVAILABLE:
            try:
                self.recognizer = sr.Recognizer()
                # Calibrate recognizer energy threshold for ambient noise
                self.recognizer.energy_threshold = 300
                self.recognizer.dynamic_energy_threshold = True
                self.microphone = sr.Microphone()
            except Exception as e:
                print(f"[Voice Input Init Error] {e}")

        if self.use_whisper:
            try:
                # Load small/base model locally
                self.whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
            except Exception as e:
                print(f"[Whisper Init Error] {e}. Falling back to standard speech recognizer.")
                self.use_whisper = False

    def listen_and_transcribe(self, timeout: int = 5, phrase_time_limit: int = 10) -> str:
        """
        Listens to user input and transcribes it to text.
        """
        if not SPEECH_REC_AVAILABLE or not self.recognizer or not self.microphone:
            return "[Error: Speech recognition dependencies or audio devices not available]"

        self.is_listening = True
        try:
            with self.microphone as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                
            self.is_listening = False

            if self.use_whisper and self.whisper_model:
                # Save temp wav and run faster-whisper
                import tempfile
                import os
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                    f.write(audio.get_wav_data())
                    temp_path = f.name
                
                try:
                    segments, info = self.whisper_model.transcribe(temp_path, beam_size=5)
                    text = "".join(segment.text for segment in segments)
                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                return text.strip()
            else:
                # Use Google Speech Recognition API (built into speech_recognition)
                text = self.recognizer.recognize_google(audio)
                return text.strip()
        except sr.WaitTimeoutError:
            self.is_listening = False
            return ""
        except sr.UnknownValueError:
            self.is_listening = False
            return "[Could not understand audio]"
        except Exception as e:
            self.is_listening = False
            return f"[Transcription error: {str(e)}]"
            
    def listen_in_background(self, callback: Callable[[str], None], stop_event: threading.Event):
        """
        Listens continuously in a background thread and calls callback with transcripts.
        """
        def background_loop():
            while not stop_event.is_set():
                text = self.listen_and_transcribe()
                if text and not text.startswith("["):
                    callback(text)
                time.sleep(0.5)

        thread = threading.Thread(target=background_loop, daemon=True)
        thread.start()
        return thread
