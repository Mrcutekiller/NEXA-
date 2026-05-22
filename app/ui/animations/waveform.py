# app/ui/animations/waveform.py
"""
Voice audio waveform visualizer.
Provides real-time wave frames using sounddevice or simulation fallbacks.
"""

import math
import random
import threading
import time
from typing import Callable, List

# Block levels for visualization
BAR_CHARS = [" ", "▂", "▃", "▄", "▅", "▆", "▇", "█"]

SOUNDDEVICE_AVAILABLE = False
try:
    import sounddevice as sd
    import numpy as np
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    pass

class WaveformVisualizer:
    def __init__(self, num_bars: int = 8, callback: Callable[[str], None] = None):
        self.num_bars = num_bars
        self.callback = callback
        self.is_running = False
        self.thread = None
        self.stream = None
        self.amplitude_buffer = [0.0] * 10
        self._lock = threading.Lock()

    def _audio_callback(self, indata, frames, time, status):
        """Callback for sounddevice input stream."""
        if status:
            pass
        # Calculate RMS amplitude
        volume_norm = np.linalg.norm(indata) / np.sqrt(indata.size)
        with self._lock:
            self.amplitude_buffer.append(float(volume_norm))
            if len(self.amplitude_buffer) > 10:
                self.amplitude_buffer.pop(0)

    def start(self):
        self.is_running = True
        
        # Try to open sounddevice input stream
        if SOUNDDEVICE_AVAILABLE:
            try:
                self.stream = sd.InputStream(
                    callback=self._audio_callback,
                    channels=1,
                    samplerate=16000,
                    blocksize=1024
                )
                self.stream.start()
            except Exception as e:
                # Failed to open stream (e.g. no audio inputs)
                self.stream = None

        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        self.is_running = False
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass
            self.stream = None
        if self.thread:
            self.thread.join(timeout=1.0)

    def _run(self):
        t = 0.0
        while self.is_running:
            frame = ""
            
            if SOUNDDEVICE_AVAILABLE and self.stream:
                # Use real microphone data
                with self._lock:
                    avg_amp = sum(self.amplitude_buffer) / len(self.amplitude_buffer)
                # Map amplitude to bar index (scale appropriately)
                level = min(int(avg_amp * 40), len(BAR_CHARS) - 1)
                
                # Generate 8 bars around that level with some noise
                for i in range(self.num_bars):
                    variance = random.uniform(-1.5, 1.5)
                    bar_idx = max(0, min(len(BAR_CHARS) - 1, int(level + variance)))
                    frame += BAR_CHARS[bar_idx]
            else:
                # Simulated sine wave + noise fallback
                t += 0.25
                for i in range(self.num_bars):
                    # Sine wave offset by bar index
                    val = math.sin(t + i * 0.7) * math.cos(t * 0.5)
                    # Normalize to 0-1
                    val = (val + 1.0) / 2.0
                    # Add random noise
                    val = val * 0.7 + random.random() * 0.3
                    
                    bar_idx = int(val * (len(BAR_CHARS) - 1))
                    bar_idx = max(0, min(len(BAR_CHARS) - 1, bar_idx))
                    frame += BAR_CHARS[bar_idx]

            if self.callback:
                try:
                    self.callback(frame)
                except Exception:
                    pass

            time.sleep(0.08) # ~12 FPS
