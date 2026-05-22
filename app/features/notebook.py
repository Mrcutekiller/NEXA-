# app/features/notebook.py
"""
Local Notebook and Knowledge Store.
Allows saving, searching, tagging, and listing personal user notes.
"""

import json
import os
import uuid
import time
from typing import List, Dict, Any

class NotebookManager:
    def __init__(self, notebook_path: str = "user/notebook.json"):
        self.notebook_path = notebook_path
        self.notes: List[Dict[str, Any]] = []
        self._load_notes()

    def _load_notes(self):
        dir_name = os.path.dirname(self.notebook_path)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)
            
        if os.path.exists(self.notebook_path):
            try:
                with open(self.notebook_path, "r") as f:
                    self.notes = json.load(f)
            except Exception as e:
                print(f"[Notebook Load Error] {e}")

    def save_notebook(self):
        try:
            with open(self.notebook_path, "w") as f:
                json.dump(self.notes, f, indent=4)
        except Exception as e:
            print(f"[Notebook Save Error] {e}")

    def add_note(self, title: str, content: str, tags: List[str] = None) -> Dict[str, Any]:
        tags = tags or []
        note = {
            "id": str(uuid.uuid4())[:8],
            "title": title,
            "content": content,
            "tags": [t.strip().lower() for t in tags],
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.notes.append(note)
        self.save_notebook()
        return note

    def delete_note(self, note_id: str) -> bool:
        initial_len = len(self.notes)
        self.notes = [n for n in self.notes if n["id"] != note_id]
        success = len(self.notes) < initial_len
        if success:
            self.save_notebook()
        return success

    def list_notes(self) -> List[Dict[str, Any]]:
        return self.notes

    def search_notes(self, query: str) -> List[Dict[str, Any]]:
        """
        Searches notes by title, content, or tags.
        """
        q = query.lower()
        results = []
        for note in self.notes:
            if (q in note["title"].lower() or 
                q in note["content"].lower() or 
                any(q in tag for tag in note["tags"])):
                results.append(note)
        return results
