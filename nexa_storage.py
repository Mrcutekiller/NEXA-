import json
import os
import sqlite3
import logging
from datetime import datetime
from colorama import Fore, Style

# Setup Logging
logging.basicConfig(
    filename='nexa_system.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class NexaStorage:
    def __init__(self, db_path="nexa_vault.db"):
        self.db_path = db_path
        self._init_db()
        self.config = self._load_config_from_db()

    def _init_db(self):
        """Initializes SQLite database with required tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Config table
        cursor.execute('''CREATE TABLE IF NOT EXISTS config (
                            key TEXT PRIMARY KEY,
                            value TEXT
                          )''')
        
        # Skills table
        cursor.execute('''CREATE TABLE IF NOT EXISTS skills (
                            name TEXT PRIMARY KEY,
                            source TEXT,
                            installed_at TEXT,
                            status TEXT
                          )''')
        
        # Logs table
        cursor.execute('''CREATE TABLE IF NOT EXISTS system_logs (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            timestamp TEXT,
                            action TEXT,
                            details TEXT
                          )''')
        
        conn.commit()
        conn.close()

    def _load_config_from_db(self):
        """Loads configuration from SQLite, or initializes with defaults."""
        defaults = {
            "api_providers": {
                "LOCAL": {"type": "internal", "active": True},
                "OPENAI": {"type": "external", "active": False, "key": None, "model": "gpt-4"},
                "ANTHROPIC": {"type": "external", "active": False, "key": None, "model": "claude-3-sonnet"},
                "GEMINI": {"type": "external", "active": False, "key": None, "model": "gemini-pro"}
            },
            "active_provider": "LOCAL",
            "settings": {
                "temperature": 0.7,
                "max_tokens": 2048,
                "active_model": "GOD_EYE"
            }
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM config WHERE key = 'main_config'")
        row = cursor.fetchone()
        
        if row:
            config = json.loads(row[0])
            # Merge with defaults
            for k, v in defaults.items():
                if k not in config:
                    config[k] = v
        else:
            config = defaults
            cursor.execute("INSERT INTO config (key, value) VALUES (?, ?)", 
                           ('main_config', json.dumps(config)))
            conn.commit()
        
        # Load skills into config for easy access
        cursor.execute("SELECT * FROM skills")
        rows = cursor.fetchall()
        config["installed_skills"] = {row[0]: {"source": row[1], "installed_at": row[2], "status": row[3]} for row in rows}
        
        conn.close()
        return config

    def save(self):
        """Saves current config and skills back to SQLite."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Save main config
            config_to_save = self.config.copy()
            skills_data = config_to_save.pop("installed_skills", {})
            cursor.execute("UPDATE config SET value = ? WHERE key = 'main_config'", 
                           (json.dumps(config_to_save),))
            
            # Save skills
            for name, info in skills_data.items():
                cursor.execute("INSERT OR REPLACE INTO skills (name, source, installed_at, status) VALUES (?, ?, ?, ?)",
                               (name, info.get("source"), info.get("installed_at"), info.get("status")))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logging.error(f"Failed to save to SQLite: {e}")

    def log_event(self, action, details):
        """Logs event to both file and SQLite."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = f"Action: {action} | Details: {details}"
        logging.info(msg)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO system_logs (timestamp, action, details) VALUES (?, ?, ?)",
                           (timestamp, action, str(details)))
            conn.commit()
            conn.close()
        except Exception as e:
            logging.error(f"Failed to log to SQLite: {e}")
        
        print(f"{Fore.YELLOW}[SYSTEM LOG] {Style.RESET_ALL}{action}: {details}")
