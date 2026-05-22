# app/features/audit.py
import os
from datetime import datetime
from typing import List

class NexaAuditLog:
    def __init__(self, log_path: str = "user/audit.log"):
        self.log_path = log_path
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

    def log_action(self, action: str, details: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [ACTION: {action}] {details}\n"
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(log_line)

    def get_logs(self, filter_today: bool = False) -> List[str]:
        if not os.path.exists(self.log_path):
            return []
        
        today_str = datetime.now().strftime("%Y-%m-%d")
        logs = []
        with open(self.log_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if filter_today and not line.startswith(f"[{today_str}"):
                    continue
                logs.append(line.strip())
        return logs

    def clear_logs(self):
        if os.path.exists(self.log_path):
            os.remove(self.log_path)
        self.log_action("AUDIT_CLEAR", "Audit logs cleared by user.")

    def get_privacy_report(self) -> str:
        report = """
🔒 NEXA SYSTEM PRIVACY REPORT
==============================
NEXA operates 100% offline. No data is sent to external clouds or servers.

DATA STORAGE LOCATIONS:
- Learned Facts:        user/knowledge.json
- Notes/Notebooks:      user/notebook.json
- Weekly Insights:      user/stats.json
- Achievements:         user/badges.json
- Skill Tree:           user/skill_tree.json
- Mistake Logs:         user/mistakes.json
- Encrypted Secrets:    user/vault.enc (AES-256 encrypted)
- Action Audit History: user/audit.log

Your data belongs completely to you. You can export or clear any of these
subsystems at any time using the appropriate slash commands.
"""
        return report.strip()
