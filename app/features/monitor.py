# app/features/monitor.py
import re
from typing import List, Optional

class NexaMonitor:
    ERROR_PATTERNS = [
        r'Traceback \(most recent call last\)',    # Python traceback start
        r'SyntaxError:',                           # Python syntax
        r'TypeError:',                             # Python type
        r'NameError:',                             # Python name
        r'ModuleNotFoundError:',                   # Python missing module
        r'Error: Cannot find module',              # Node.js missing module
        r'ENOENT: no such file',                   # File not found
        r'Permission denied',                      # Permissions
        r'command not found',                      # Shell errors
        r'fatal error:',                           # C/C++ compiler error
        r'error\[E\d+\]',                          # Rust compiler error
        r'error TS\d+',                            # TypeScript error
        r'HTTP \d{3}',                             # HTTP status error
    ]

    def __init__(self):
        self.is_active = False
        self.error_log: List[str] = []
        self.last_captured_error: Optional[str] = None

    def start_monitoring(self):
        self.is_active = True

    def stop_monitoring(self):
        self.is_active = False

    def feed_line(self, line: str) -> Optional[str]:
        """
        Feeds a line of console output to the monitor.
        If an error pattern is matched and the monitor is active, returns a prompt notification.
        """
        if not self.is_active:
            return None

        for pattern in self.ERROR_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                self.last_captured_error = line.strip()
                self.error_log.append(self.last_captured_error)
                
                # Format warning block
                warning = (
                    f"\n┌─ nexa monitor ──────────────────────────────┐\n"
                    f"│ ⚠  Error detected: {self.last_captured_error[:40]}...   │\n"
                    f"│  /monitor fix  to auto-fix  |  /why  to explain     │\n"
                    f"└──────────────────────────────────────────────┘"
                )
                return warning
        return None

    def get_status(self) -> str:
        status = "ACTIVE" if self.is_active else "INACTIVE"
        return f"NEXA Monitor is currently {status}. Errors caught: {len(self.error_log)}."

    def clear_log(self):
        self.error_log = []
        self.last_captured_error = None
