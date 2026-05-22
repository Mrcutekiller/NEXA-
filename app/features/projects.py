# app/features/projects.py
import os
import json
import zipfile
from datetime import datetime
from typing import Dict, List, Any, Optional

class ProjectManager:
    def __init__(self, base_dir: str = "projects"):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)
        self.current_project: Optional[str] = None
        self.metadata: Dict[str, Any] = {}

    def create_project(self, name: str, description: str = "") -> str:
        proj_dir = os.path.join(self.base_dir, name)
        if os.path.exists(proj_dir):
            return f"Project '{name}' already exists."

        os.makedirs(proj_dir, exist_ok=True)
        os.makedirs(os.path.join(proj_dir, "files"), exist_ok=True)

        meta = {
            "name": name,
            "created": datetime.now().strftime("%Y-%m-%d"),
            "last_opened": datetime.now().strftime("%Y-%m-%d"),
            "description": description or f"Workspace for {name}",
            "model_preference": "ultra",
            "files_generated": [],
            "todos": [],
            "stats": {
                "total_sessions": 1,
                "code_files_generated": 0,
                "bugs_fixed": 0,
                "designs_created": 0
            }
        }
        self._save_project_metadata(name, meta)
        
        # Create default empty files
        self._write_json(os.path.join(proj_dir, "chat_history.json"), [])
        self._write_json(os.path.join(proj_dir, "notes.json"), [])
        
        return f"Project '{name}' created successfully!"

    def open_project(self, name: str) -> str:
        proj_dir = os.path.join(self.base_dir, name)
        if not os.path.exists(proj_dir):
            return f"Project '{name}' does not exist."

        self.current_project = name
        meta = self._load_project_metadata(name)
        meta["last_opened"] = datetime.now().strftime("%Y-%m-%d")
        meta["stats"]["total_sessions"] = meta["stats"].get("total_sessions", 0) + 1
        self._save_project_metadata(name, meta)
        self.metadata = meta
        return f"Opened project '{name}'."

    def close_project(self) -> str:
        if not self.current_project:
            return "No active project to close."
        name = self.current_project
        self.current_project = None
        self.metadata = {}
        return f"Closed project '{name}'."

    def list_projects(self) -> List[Dict[str, Any]]:
        projects = []
        if not os.path.exists(self.base_dir):
            return []
        for name in os.listdir(self.base_dir):
            meta_path = os.path.join(self.base_dir, name, "project.json")
            if os.path.exists(meta_path):
                try:
                    with open(meta_path, "r", encoding="utf-8") as f:
                        projects.append(json.load(f))
                except Exception:
                    pass
        return projects

    def delete_project(self, name: str) -> str:
        proj_dir = os.path.join(self.base_dir, name)
        if not os.path.exists(proj_dir):
            return f"Project '{name}' does not exist."
            
        import shutil
        shutil.rmtree(proj_dir)
        if self.current_project == name:
            self.current_project = None
            self.metadata = {}
        return f"Project '{name}' has been deleted."

    def add_todo(self, task: str) -> str:
        if not self.current_project:
            return "No active project. Open a project first."
        
        todo_id = f"todo_{len(self.metadata['todos']) + 1:02d}"
        todo = {
            "id": todo_id,
            "task": task,
            "completed": False,
            "date_added": datetime.now().strftime("%Y-%m-%d")
        }
        self.metadata["todos"].append(todo)
        self._save_project_metadata(self.current_project, self.metadata)
        return f"Added todo: [{todo_id}] {task}"

    def list_todos(self) -> str:
        if not self.current_project:
            return "No active project."
        todos = self.metadata.get("todos", [])
        if not todos:
            return "No todos for this project."
        
        lines = [f"📋 TODOS FOR PROJECT: {self.current_project.upper()}"]
        for t in todos:
            chk = "✓" if t["completed"] else " "
            lines.append(f"  [{chk}] [{t['id']}] {t['task']}")
        return "\n".join(lines)

    def mark_todo_done(self, todo_id: str) -> str:
        if not self.current_project:
            return "No active project."
        for t in self.metadata["todos"]:
            if t["id"] == todo_id:
                t["completed"] = True
                self._save_project_metadata(self.current_project, self.metadata)
                return f"Marked [{todo_id}] as completed!"
        return f"Todo '{todo_id}' not found."

    def clear_completed_todos(self) -> str:
        if not self.current_project:
            return "No active project."
        initial_count = len(self.metadata["todos"])
        self.metadata["todos"] = [t for t in self.metadata["todos"] if not t["completed"]]
        self._save_project_metadata(self.current_project, self.metadata)
        cleared = initial_count - len(self.metadata["todos"])
        return f"Cleared {cleared} completed todos."

    def get_summary(self) -> str:
        if not self.current_project:
            return "No active project."
        meta = self.metadata
        stats = meta.get("stats", {})
        return f"""
📁 PROJECT SUMMARY: {meta['name'].upper()}
Description:   {meta['description']}
Created:       {meta['created']}
Sessions:      {stats.get('total_sessions', 1)}
Files Made:    {stats.get('code_files_generated', 0)}
Bugs Fixed:    {stats.get('bugs_fixed', 0)}
Designs:       {stats.get('designs_created', 0)}
Todos:         {len([t for t in meta['todos'] if t['completed'] == True])}/{len(meta['todos'])} complete
"""

    def export_project_zip(self) -> str:
        if not self.current_project:
            return "No active project."
        proj_dir = os.path.join(self.base_dir, self.current_project)
        zip_path = os.path.join(self.base_dir, f"{self.current_project}.zip")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(proj_dir):
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, self.base_dir)
                    zipf.write(full_path, rel_path)
        return zip_path

    def _write_json(self, filepath: str, data: Any):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _load_project_metadata(self, name: str) -> Dict[str, Any]:
        meta_path = os.path.join(self.base_dir, name, "project.json")
        with open(meta_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_project_metadata(self, name: str, meta: Dict[str, Any]):
        meta_path = os.path.join(self.base_dir, name, "project.json")
        self._write_json(meta_path, meta)
