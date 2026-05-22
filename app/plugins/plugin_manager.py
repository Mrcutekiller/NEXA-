# app/plugins/plugin_manager.py
import os
import json
import importlib.util
from typing import Dict, List, Any, Optional

class PluginManager:
    def __init__(self, plugins_dir: str = "plugins", config_path: str = "user/plugins.json"):
        self.plugins_dir = plugins_dir
        self.config_path = config_path
        os.makedirs(plugins_dir, exist_ok=True)
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        self.active_plugins: Dict[str, Any] = {}
        self.enabled_list = self._load_config()
        self._setup_built_in_placeholders()
        self.load_plugins()

    def _load_config(self) -> List[str]:
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return ["calculator", "timer", "word-count", "json-format"]  # default active

    def _save_config(self):
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.enabled_list, f, indent=2)

    def _setup_built_in_placeholders(self):
        # Create folder structure for default plugins if missing
        for p in ["calculator", "timer", "word-count", "json-format"]:
            p_dir = os.path.join(self.plugins_dir, p)
            os.makedirs(p_dir, exist_ok=True)
            meta_path = os.path.join(p_dir, "plugin.json")
            if not os.path.exists(meta_path):
                meta = {
                    "name": p,
                    "version": "1.0",
                    "description": f"Built-in utility helper for {p}.",
                    "author": "system",
                    "commands": [f"/{p}"],
                    "triggers": [p],
                    "entry": "main.py"
                }
                with open(meta_path, "w", encoding="utf-8") as f:
                    json.dump(meta, f, indent=2)

            main_path = os.path.join(p_dir, "main.py")
            if not os.path.exists(main_path):
                # Write a basic script template
                code = f"""# Nexa Plugin: {p}
class NexaPlugin:
    def on_command(self, command: str, args: str) -> str:
        return f"[Plugin {p}] Executed command: " + command + " with args: " + args
    
    def on_trigger(self, message: str, context: dict) -> str:
        return None
"""
                with open(main_path, "w", encoding="utf-8") as f:
                    f.write(code)

    def load_plugins(self):
        self.active_plugins.clear()
        if not os.path.exists(self.plugins_dir):
            return

        for name in os.listdir(self.plugins_dir):
            p_dir = os.path.join(self.plugins_dir, name)
            if not os.path.isdir(p_dir):
                continue
            
            meta_path = os.path.join(p_dir, "plugin.json")
            if os.path.exists(meta_path):
                try:
                    with open(meta_path, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                    
                    if name in self.enabled_list:
                        # Load entry module
                        entry_file = meta.get("entry", "main.py")
                        module_path = os.path.join(p_dir, entry_file)
                        if os.path.exists(module_path):
                            spec = importlib.util.spec_from_file_location(f"plugin_{name}", module_path)
                            if spec and spec.loader:
                                module = importlib.util.module_from_spec(spec)
                                spec.loader.exec_module(module)
                                if hasattr(module, "NexaPlugin"):
                                    self.active_plugins[name] = {
                                        "meta": meta,
                                        "instance": module.NexaPlugin()
                                    }
                except Exception as e:
                    print(f"Error loading plugin '{name}': {e}")

    def list_installed_plugins(self) -> List[Dict[str, Any]]:
        plugins = []
        for name in os.listdir(self.plugins_dir):
            p_dir = os.path.join(self.plugins_dir, name)
            if os.path.isdir(p_dir):
                meta_path = os.path.join(p_dir, "plugin.json")
                if os.path.exists(meta_path):
                    try:
                        with open(meta_path, "r", encoding="utf-8") as f:
                            meta = json.load(f)
                        meta["enabled"] = name in self.enabled_list
                        plugins.append(meta)
                    except Exception:
                        pass
        return plugins

    def enable_plugin(self, name: str) -> str:
        p_dir = os.path.join(self.plugins_dir, name)
        if not os.path.exists(p_dir):
            return f"Plugin '{name}' is not installed."
        if name not in self.enabled_list:
            self.enabled_list.append(name)
            self._save_config()
            self.load_plugins()
            return f"Plugin '{name}' enabled successfully."
        return f"Plugin '{name}' is already enabled."

    def disable_plugin(self, name: str) -> str:
        if name in self.enabled_list:
            self.enabled_list.remove(name)
            self._save_config()
            self.load_plugins()
            return f"Plugin '{name}' disabled."
        return f"Plugin '{name}' is not currently active."

    def install_plugin(self, name: str) -> str:
        p_dir = os.path.join(self.plugins_dir, name)
        if os.path.exists(p_dir):
            return f"Plugin '{name}' already exists."
        
        os.makedirs(p_dir, exist_ok=True)
        meta = {
            "name": name,
            "version": "1.0",
            "description": f"Community plugin {name}",
            "author": "community",
            "commands": [f"/{name}"],
            "triggers": [name],
            "entry": "main.py"
        }
        with open(os.path.join(p_dir, "plugin.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)
            
        with open(os.path.join(p_dir, "main.py"), "w", encoding="utf-8") as f:
            f.write(f"""# Custom Nexa Plugin: {name}
class NexaPlugin:
    def on_command(self, command: str, args: str) -> str:
        return f"Hello from community plugin '{name}'! Args: {{args}}"
    def on_trigger(self, message: str, context: dict) -> str:
        return None
""")
        self.enabled_list.append(name)
        self._save_config()
        self.load_plugins()
        return f"Plugin '{name}' generated and installed successfully."

    def remove_plugin(self, name: str) -> str:
        p_dir = os.path.join(self.plugins_dir, name)
        if not os.path.exists(p_dir):
            return f"Plugin '{name}' does not exist."
            
        import shutil
        shutil.rmtree(p_dir)
        if name in self.enabled_list:
            self.enabled_list.remove(name)
            self._save_config()
        self.load_plugins()
        return f"Plugin '{name}' has been uninstalled."

    def route_command(self, cmd: str, args: str) -> Optional[str]:
        for name, data in self.active_plugins.items():
            meta = data["meta"]
            if cmd in meta.get("commands", []):
                try:
                    return data["instance"].on_command(cmd, args)
                except Exception as e:
                    return f"Error executing plugin '{name}': {e}"
        return None

    def check_triggers(self, text: str, context: Dict[str, Any]) -> Optional[str]:
        text_lower = text.lower()
        for name, data in self.active_plugins.items():
            meta = data["meta"]
            for trig in meta.get("triggers", []):
                if trig in text_lower:
                    try:
                        res = data["instance"].on_trigger(text, context)
                        if res:
                            return res
                    except Exception:
                        pass
        return None
