# app/features/code_runner.py
import subprocess
import tempfile
import os
import sys
from typing import Dict, Any

class NexaCodeRunner:
    def __init__(self):
        # We can map languages to interpreter executables
        self.interpreters = {
            "python": [sys.executable, "-c"],
            "javascript": ["node", "-e"],
            "bash": ["bash", "-c"]
        }

    def run_code(self, code: str, language: str = "python", timeout: int = 10) -> Dict[str, Any]:
        lang = language.lower().strip()
        if lang not in self.interpreters:
            # Fallback check
            if "py" in lang:
                lang = "python"
            elif "js" in lang or "node" in lang:
                lang = "javascript"
            elif "sh" in lang or "bash" in lang or "shell" in lang:
                lang = "bash"
            else:
                return {"error": f"Language '{language}' is not supported yet.", "success": False}

        cmd_prefix = self.interpreters[lang]
        
        # Windows compatibility adjustment for bash
        if lang == "bash" and os.name == "nt":
            # On Windows, try executing git bash or wsl if bash isn't directly on PATH, or fallback to powershell
            cmd_prefix = ["powershell", "-Command"]

        try:
            # Run the command with subprocess, limiting execution time
            res = subprocess.run(
                cmd_prefix + [code],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return {
                "stdout": res.stdout,
                "stderr": res.stderr,
                "returncode": res.returncode,
                "success": res.returncode == 0,
                "timed_out": False
            }
        except subprocess.TimeoutExpired:
            return {
                "error": f"Code execution timed out after {timeout} seconds.",
                "success": False,
                "timed_out": True
            }
        except FileNotFoundError:
            return {
                "error": f"Interpreter for '{lang}' was not found on the system path.",
                "success": False,
                "timed_out": False
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
                "timed_out": False
            }
