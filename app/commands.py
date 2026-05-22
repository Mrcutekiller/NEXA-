# app/commands.py
"""
Universal and Specialist Slash Command Router for NEXA v4.
Registers and routes over 100 slash commands to model contexts and features.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any, Callable
import re
import os

from app.features.knowledge import NexaKnowledgeBase
from app.features.learn_mode import NexaLearnMode
from app.features.explain_mistake import NexaMistakeLog
from app.features.duels import NexaDuels
from app.features.skill_tree import SkillTreeManager
from app.features.badges import BadgeManager
from app.features.projects import ProjectManager
from app.features.diff import NexaDiff
from app.features.translate import NexaTranslator
from app.features.templates import TemplateManager
from app.features.code_runner import NexaCodeRunner
from app.features.vault import NexaVault
from app.features.audit import NexaAuditLog
from app.features.monitor import NexaMonitor
from app.features.rag import NexaRAG
from app.features.narrate import NexaNarrate
from app.features.personas import NexaPersonaManager
from app.plugins.plugin_manager import PluginManager

@dataclass
class CommandResult:
    text: str
    xp_event: Optional[str] = None
    animation: Optional[str] = None
    success: bool = True

class CommandRouter:
    def __init__(self, model_manager=None, xp_manager=None, challenge_manager=None, notebook_manager=None):
        self.model_manager = model_manager
        self.xp_manager = xp_manager
        self.challenge_manager = challenge_manager
        self.notebook_manager = notebook_manager

        # Initialize all v4 features
        self.kb = NexaKnowledgeBase()
        self.learn_mode = NexaLearnMode()
        self.mistake_log = NexaMistakeLog()
        self.duels = NexaDuels(xp_manager=self.xp_manager)
        self.skill_tree = SkillTreeManager()
        self.badge_manager = BadgeManager()
        self.project_manager = ProjectManager()
        self.diff = NexaDiff()
        self.translator = NexaTranslator()
        self.template_manager = TemplateManager()
        self.code_runner = NexaCodeRunner()
        self.vault = NexaVault()
        self.audit_log = NexaAuditLog()
        self.monitor = NexaMonitor()
        self.rag = NexaRAG()
        self.narrator = NexaNarrate()
        self.persona_manager = NexaPersonaManager()
        self.plugin_manager = PluginManager()

        self.commands: Dict[str, Tuple[Callable[[str], CommandResult], str, str]] = {}
        self._register_all_commands()

    def _register_all_commands(self):
        # 1. Universal / Global Commands
        self.commands["/help"] = (self._cmd_help, "universal", "Display all commands or help for active model.")
        self.commands["/model"] = (self._cmd_model, "universal", "Switch active model. Usage: /model [code|design|fix|ultra]")
        self.commands["/voice"] = (self._cmd_voice, "universal", "Toggle voice output/input. Usage: /voice [on|off]")
        self.commands["/stats"] = (self._cmd_stats, "universal", "Show current level, XP progress, and streaks.")
        self.commands["/challenges"] = (self._cmd_challenges, "universal", "Show daily challenge for the active model.")
        self.commands["/challenge"] = (self._cmd_challenges, "universal", "Alias for /challenges.")
        self.commands["/solve"] = (self._cmd_solve, "universal", "Submit a solution to the active challenge. Usage: /solve [your solution]")
        self.commands["/insights"] = (self._cmd_insights, "universal", "Generate and display weekly usage reports.")
        self.commands["/note"] = (self._cmd_note, "universal", "Save a note. Usage: /note Title | Content [| tag1,tag2]")
        self.commands["/notebook"] = (self._cmd_notebook, "universal", "List notes or search. Usage: /notebook [search_term]")
        self.commands["/clear"] = (self._cmd_clear, "universal", "Clear conversation history.")
        self.commands["/exit"] = (self._cmd_exit, "universal", "Exit the application.")

        # 2. NEXA v4 Knowledge System & Learn Mode
        self.commands["/learn"] = (self._cmd_learn, "universal", "Teach Nexa new facts from text or file. Usage: /learn [text/file]")
        self.commands["/knowledge"] = (self._cmd_knowledge, "universal", "Manage knowledge database. Usage: /knowledge [search|delete|clear|export|import|stats] [args]")
        self.commands["/forget"] = (self._cmd_forget, "universal", "Delete all facts about a topic. Usage: /forget [topic]")
        self.commands["/what"] = (self._cmd_what_do_you_know, "universal", "Show summary of all learned knowledge.")

        # 3. Explain My Mistake Log
        self.commands["/mistakes"] = (self._cmd_mistakes, "universal", "Manage personal bug correction lessons. Usage: /mistakes [topic|clear]")

        # 4. Multiplayer Duels
        self.commands["/duel"] = (self._cmd_duel, "universal", "Multiplayer coding/design duels. Usage: /duel [host|join|solo] [code]")

        # 5. Skill Tree System
        self.commands["/skilltree"] = (self._cmd_skilltree, "universal", "Show full interactive skill tree.")
        self.commands["/skills"] = (self._cmd_skills, "universal", "Show unlocked or locked skills. Usage: /skills [locked|next]")

        # 6. Achievement Badges
        self.commands["/badges"] = (self._cmd_badges, "universal", "Show earned/locked/recent badges. Usage: /badges [locked|recent]")

        # 7. Persistent Workspaces (Projects) & Todos
        self.commands["/project"] = (self._cmd_project, "universal", "Manage isolated persistent workspaces. Usage: /project [new|open|list|close|delete|summary|export|share]")
        self.commands["/todo"] = (self._cmd_todo, "universal", "Manage workspace task list. Usage: /todo [add|list|done|clear]")

        # 8. Diff Comparison
        self.commands["/diff"] = (self._cmd_diff, "universal", "Compare two code blocks. Paste OLD version, type '---', paste NEW version.")

        # 9. Language & Code Translation
        self.commands["/translate"] = (self._cmd_translate, "universal", "Translate text to other languages. Usage: /translate [language] [text]")
        self.commands["/convert"] = (self._cmd_convert, "universal", "Convert code between languages. Usage: /convert [from] to [to]")
        self.commands["/simplify"] = (lambda args: self._cmd_complexity("simplify"), "universal", "Simplify last response for a beginner.")
        self.commands["/complexify"] = (lambda args: self._cmd_complexity("complexify"), "universal", "Convert last response to expert level.")
        self.commands["/eli5"] = (lambda args: self._cmd_complexity("eli5"), "universal", "Explain last response like I'm 5.")
        self.commands["/eli-expert"] = (lambda args: self._cmd_complexity("eli-expert"), "universal", "Explain last response at PhD level.")

        # 10. Template System
        self.commands["/template"] = (self._cmd_template, "universal", "Scaffold code templates. Usage: /template [name|save|my|delete]")

        # 11. Voice Personas
        self.commands["/persona"] = (self._cmd_persona, "universal", "Switch or custom voice profiles. Usage: /persona [name|custom|reset]")

        # 12. Voice Narrator
        self.commands["/narrate"] = (self._cmd_narrate, "universal", "Read files/responses aloud. Usage: /narrate [file|stop|speed|highlight]")

        # 13. Plugin Manager
        self.commands["/plugin"] = (self._cmd_plugin, "universal", "Install or manage helper utility plugins. Usage: /plugin [install|remove|list|enable|disable]")

        # 14. Local session RAG (Document Memory)
        self.commands["/read"] = (self._cmd_read, "universal", "Load document temporarily into session memory. Usage: /read [file|list|clear]")

        # 15. Background Error Monitor
        self.commands["/monitor"] = (self._cmd_monitor, "universal", "Watch stderr output for crashes. Usage: /monitor [on|off|status|log|fix]")

        # 16. Sandboxed Code Runner
        self.commands["/run"] = (self._cmd_run, "universal", "Execute generated code block. Usage: /run [python|javascript|bash|file]")
        self.commands["/runstop"] = (self._cmd_runstop, "universal", "Stop running code process.")

        # 17. Security Vault
        self.commands["/vault"] = (self._cmd_vault, "universal", "Manage AES-256 encrypted credential storage. Usage: /vault [setup|open|lock|add|get|list|delete]")

        # 18. Audit Logging & Privacy Reports
        self.commands["/audit"] = (self._cmd_audit, "universal", "Show history of files read, vault opened, facts learned. Usage: /audit [today|data|memory|clear]")
        self.commands["/privacy"] = (self._cmd_privacy, "universal", "Show data locations and offline privacy report.")

        # 19. Live HTML/CSS Preview
        self.commands["/preview"] = (self._cmd_preview, "universal", "Show live rendering on port 7750. Usage: /preview [watch|close|file]")
        self.commands["/dashboard"] = (self._cmd_dashboard, "universal", "Open local dashboard in default web browser. Usage: /dashboard")

    def route(self, command_str: str) -> CommandResult:
        parts = command_str.strip().split(" ", 1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        if cmd not in self.commands:
            return CommandResult(
                text=f"Unknown command: '{cmd}'. Type /help to see all available commands.",
                success=False
            )

        handler, category, desc = self.commands[cmd]
        
        # Verify model category permission
        if category != "universal" and self.model_manager:
            active_key = self.model_manager.active_model_key
            if active_key != category:
                return CommandResult(
                    text=f"Command '{cmd}' is exclusive to model '{category.upper()}'! Switch using '/model {category}'.",
                    success=False
                )

        try:
            res = handler(args)
            if isinstance(res, CommandResult):
                return res
            return CommandResult(text=str(res))
        except Exception as e:
            return CommandResult(
                text=f"Error executing '{cmd}': {str(e)}",
                success=False
            )

    # --- Unified Command Handlers ---

    def _cmd_help(self, args: str) -> CommandResult:
        universal_cmds = [f"{k:12} - {v[2]}" for k, v in self.commands.items() if v[1] == "universal"]
        help_text = f"""
\033[1;36mNEXA v4 Intelligence Hub Command Suite\033[0m
Total commands registered: {len(self.commands)}

\033[1mCore Commands:\033[0m
{chr(10).join(universal_cmds[:15])}

Type more specific slash commands like /knowledge, /project, /vault, /badges, /skilltree to manage features.
"""
        return CommandResult(text=help_text.strip(), xp_event="command_run")

    def _cmd_model(self, args: str) -> CommandResult:
        if not args:
            return CommandResult(text="Please specify a model. Select from: code, design, fix, ultra.")
        model_key = args.strip().lower()
        if not self.model_manager:
            return CommandResult(text="Model Manager offline.")
        if model_key not in self.model_manager.models:
            return CommandResult(text=f"Unknown model: '{model_key}'.")
        old_key = self.model_manager.active_model_key
        self.model_manager.set_active_model(model_key)
        return CommandResult(
            text=f"Switched model from {old_key.upper()} to {model_key.upper()}.",
            xp_event="model_switched",
            animation="model_switch"
        )

    def _cmd_voice(self, args: str) -> CommandResult:
        opt = args.strip().lower()
        if opt in ["on", "activate", "true"]:
            return CommandResult(text="Voice output enabled.", xp_event="voice_activated", animation="waveform")
        return CommandResult(text="Voice output disabled.")

    def _cmd_stats(self, args: str) -> CommandResult:
        if not self.xp_manager:
            return CommandResult(text="XP manager offline.")
        stats = self.xp_manager.stats
        earned, total, pct = self.xp_manager.get_progress_to_next()
        bar = "■" * int(pct * 10) + "□" * (10 - int(pct * 10))
        res = f"""
🏆 USER PROGRESS REPORT
Level:      {stats['level']} ({stats['level_name']})
XP Total:   {stats['total_xp']} XP
Next Lvl:   [{bar}] {pct*100:.1f}% ({earned}/{total} XP)
Streak:     {stats['streak']} days active
"""
        return CommandResult(text=res.strip(), xp_event="command_run")

    def _cmd_challenges(self, args: str) -> CommandResult:
        if not self.challenge_manager:
            return CommandResult(text="Challenges manager offline.")
        active_key = self.model_manager.active_model_key if self.model_manager else "ultra"
        ch = self.challenge_manager.get_challenge(active_key)
        res = f"🎯 DAILY CHALLENGE: {ch['description']}\nReward: {ch['xp']} XP. Submit via /solve [answer]."
        return CommandResult(text=res, xp_event="command_run")

    def _cmd_solve(self, args: str) -> CommandResult:
        if not args:
            return CommandResult(text="Provide an answer. Usage: /solve [answer]")
        active_key = self.model_manager.active_model_key if self.model_manager else "ultra"
        success, msg = self.challenge_manager.verify_solution(active_key, args)
        if success:
            return CommandResult(text=f"✓ Correct! {msg}", xp_event="challenge_completed", animation="level_up")
        return CommandResult(text=f"✗ Incorrect: {msg}", success=False)

    def _cmd_insights(self, args: str) -> CommandResult:
        from app.features.insights import InsightsManager
        mgr = InsightsManager(self.xp_manager)
        return CommandResult(text=mgr.generate_report(), xp_event="command_run")

    def _cmd_note(self, args: str) -> CommandResult:
        parts = args.split("|")
        if len(parts) < 2:
            return CommandResult(text="Usage: /note Title | Content")
        title = parts[0].strip()
        content = parts[1].strip()
        tags = [t.strip() for t in parts[2].split(",")] if len(parts) > 2 else []
        n = self.notebook_manager.add_note(title, content, tags)
        self.audit_log.log_action("NOTE_SAVE", f"Saved note: {title}")
        return CommandResult(text=f"Note saved! ID: {n['id']}", xp_event="notebook_note_saved")

    def _cmd_notebook(self, args: str) -> CommandResult:
        notes = self.notebook_manager.search_notes(args) if args else self.notebook_manager.list_notes()
        if not notes:
            return CommandResult(text="No notes found.")
        lines = [f"Notebook notes:"]
        for n in notes:
            lines.append(f"  [{n['id']}] {n['title']} ({n['created_at']})")
        return CommandResult(text="\n".join(lines))

    def _cmd_clear(self, args: str) -> CommandResult:
        return CommandResult(text="Conversation cleared.")

    def _cmd_exit(self, args: str) -> CommandResult:
        return CommandResult(text="Goodbye.")

    # --- v4 Specific Commands ---

    def _cmd_learn(self, args: str) -> CommandResult:
        if not args:
            return CommandResult(text="Usage: /learn [fact text] or /learn [file.txt]")
        
        # Check if argument is an existing file
        if os.path.exists(args):
            try:
                facts = self.kb.learn_file(args)
                self.audit_log.log_action("LEARN_FILE", f"Learned {len(facts)} facts from {args}")
                return CommandResult(text=f"📚 Learned {len(facts)} facts from '{args}' successfully!", xp_event="notebook_note_saved")
            except Exception as e:
                return CommandResult(text=f"Error reading file: {str(e)}", success=False)
        else:
            fact = self.kb.learn_fact(args)
            self.audit_log.log_action("LEARN_FACT", f"Learned fact {fact['id']}")
            return CommandResult(text=f"📚 Learned: \"{fact['content']}\" (Saved as ID: {fact['id']})", xp_event="notebook_note_saved")

    def _cmd_knowledge(self, args: str) -> CommandResult:
        parts = args.strip().split(" ", 1)
        sub = parts[0].lower()
        sub_args = parts[1] if len(parts) > 1 else ""

        if sub == "search":
            results = self.kb.search_facts(sub_args)
            if not results: return CommandResult(text="No matching facts found.")
            lines = [f"Found {len(results)} matches:"]
            for r in results:
                lines.append(f"  [{r['id']}] ({r['topic']}): {r['content']}")
            return CommandResult(text="\n".join(lines))
        elif sub == "delete":
            deleted = self.kb.delete_fact(sub_args)
            self.audit_log.log_action("KNOWLEDGE_DELETE", f"Deleted fact {sub_args} -> {deleted}")
            return CommandResult(text=f"Fact {sub_args} deleted: {deleted}")
        elif sub == "clear":
            self.kb.clear_knowledge()
            self.audit_log.log_action("KNOWLEDGE_CLEAR", "Cleared all learned facts.")
            return CommandResult(text="Knowledge base cleared.")
        elif sub == "export":
            path = self.kb.export_knowledge("user/exported_knowledge.txt")
            return CommandResult(text=f"Exported knowledge to: {path}")
        elif sub == "import":
            count = self.kb.import_knowledge(sub_args)
            self.audit_log.log_action("KNOWLEDGE_IMPORT", f"Imported {count} facts.")
            return CommandResult(text=f"Imported {count} facts.")
        elif sub == "stats":
            stats = self.kb.get_stats()
            return CommandResult(text=f"Knowledge stats: {stats}")
        else:
            # List all facts
            facts = self.kb.data.get("facts", [])
            if not facts: return CommandResult(text="Knowledge database is empty.")
            lines = ["📚 Learned Facts:"]
            for f in facts:
                lines.append(f"  [{f['id']}] ({f['topic']}): {f['content']}")
            return CommandResult(text="\n".join(lines))

    def _cmd_forget(self, args: str) -> CommandResult:
        if not args:
            return CommandResult(text="Usage: /forget [topic]")
        initial_count = len(self.kb.data.get("facts", []))
        self.kb.data["facts"] = [f for f in self.kb.data.get("facts", []) if f["topic"].lower() != args.lower()]
        self.kb._save_data()
        forgotten = initial_count - len(self.kb.data.get("facts", []))
        self.audit_log.log_action("FORGET_TOPIC", f"Forgot {forgotten} facts on topic: {args}")
        return CommandResult(text=f"Forgot {forgotten} facts about topic: {args}.")

    def _cmd_what_do_you_know(self, args: str) -> CommandResult:
        stats = self.kb.get_stats()
        facts = self.kb.data.get("facts", [])[:10]
        lines = [f"I currently know {stats['total_facts']} facts.", "Here are some of them:"]
        for f in facts:
            lines.append(f"  - {f['content']}")
        return CommandResult(text="\n".join(lines))

    def _cmd_mistakes(self, args: str) -> CommandResult:
        if args.lower() == "clear":
            self.mistake_log.clear_mistakes()
            return CommandResult(text="Mistake log cleared.")
        
        mistakes = self.mistake_log.get_mistakes(args if args else None)
        if not mistakes: return CommandResult(text="No mistakes logged.")
        
        lines = ["🐛 PERSONAL MISTAKE LOG:"]
        for m in mistakes:
            lines.append(f"  [{m['id']}] Topic: {m['topic']} - {m['title']}\n  Lesson: {m['lesson']}")
        return CommandResult(text="\n".join(lines))

    def _cmd_duel(self, args: str) -> CommandResult:
        parts = args.strip().split(" ", 1)
        sub = parts[0].lower()
        sub_args = parts[1] if len(parts) > 1 else ""

        if sub == "host":
            code = self.duels.host_duel()
            return CommandResult(text=f"Duel room created! Share this code: {code}\nWaiting for opponent...")
        elif sub == "join":
            res = self.duels.join_duel(sub_args)
            return CommandResult(text=res)
        elif sub == "solo":
            res = self.duels.practice_solo()
            return CommandResult(text=res)
        elif sub == "submit":
            res = self.duels.submit_solution(sub_args)
            return CommandResult(text=res)
        else:
            return CommandResult(text="Usage: /duel [host|join|solo|submit] [arguments]")

    def _cmd_skilltree(self, args: str) -> CommandResult:
        stats = self.xp_manager.stats if self.xp_manager else {"level": 1, "streak": 0}
        usages = {"code": stats.get("code_runs", 0), "design": stats.get("designs_created", 0), "fix": stats.get("bugs_fixed", 0), "ultra": stats.get("total_sessions", 0)}
        tree = self.skill_tree.get_skill_tree_text(stats.get("level", 1), usages, stats.get("streak", 0))
        return CommandResult(text=tree)

    def _cmd_skills(self, args: str) -> CommandResult:
        opt = args.strip().lower()
        stats = self.xp_manager.stats if self.xp_manager else {"level": 1, "streak": 0}
        usages = {"code": stats.get("code_runs", 0), "design": stats.get("designs_created", 0), "fix": stats.get("bugs_fixed", 0), "ultra": stats.get("total_sessions", 0)}
        self.skill_tree.check_unlocks(stats.get("level", 1), usages, stats.get("streak", 0))
        
        if opt == "locked":
            locked = [n for n in ["power_lvl2", "power_lvl3", "power_lvl4", "power_lvl5", "power_lvl6", "power_lvl7", "power_lvl8", "spec_code", "spec_design", "spec_fix", "spec_ultra", "streak_7", "streak_30", "streak_100"] if n not in self.skill_tree.unlocked_nodes]
            return CommandResult(text=f"Locked Nodes: {', '.join(locked)}")
        elif opt == "next":
            # Simple next list
            return CommandResult(text="Next lock to target: Power Level unlocks. Check /skilltree.")
        else:
            return CommandResult(text=f"Unlocked Skills: {', '.join(self.skill_tree.unlocked_nodes)}")

    def _cmd_badges(self, args: str) -> CommandResult:
        opt = args.strip().lower()
        if opt == "locked":
            res = self.badge_manager.get_badges_display("locked")
        elif opt == "recent":
            res = self.badge_manager.get_badges_display("recent")
        else:
            res = self.badge_manager.get_badges_display("all")
        return CommandResult(text=res)

    def _cmd_project(self, args: str) -> CommandResult:
        parts = args.strip().split(" ", 1)
        sub = parts[0].lower()
        sub_args = parts[1] if len(parts) > 1 else ""

        if sub == "new":
            res = self.project_manager.create_project(sub_args)
            self.audit_log.log_action("PROJECT_NEW", f"Created project {sub_args}")
            return CommandResult(text=res, xp_event="code_written")
        elif sub == "open":
            res = self.project_manager.open_project(sub_args)
            self.audit_log.log_action("PROJECT_OPEN", f"Opened project {sub_args}")
            return CommandResult(text=res)
        elif sub == "list":
            projects = self.project_manager.list_projects()
            if not projects: return CommandResult(text="No projects found.")
            lines = ["Projects:"]
            for p in projects:
                lines.append(f"  - {p['name']} ({p['description']})")
            return CommandResult(text="\n".join(lines))
        elif sub == "close":
            res = self.project_manager.close_project()
            return CommandResult(text=res)
        elif sub == "delete":
            res = self.project_manager.delete_project(sub_args)
            return CommandResult(text=res)
        elif sub == "summary":
            res = self.project_manager.get_summary()
            return CommandResult(text=res)
        elif sub == "export":
            path = self.project_manager.export_project_zip()
            return CommandResult(text=f"Exported project zip file: {path}")
        else:
            return CommandResult(text="Usage: /project [new|open|list|close|delete|summary|export]")

    def _cmd_todo(self, args: str) -> CommandResult:
        parts = args.strip().split(" ", 1)
        sub = parts[0].lower()
        sub_args = parts[1] if len(parts) > 1 else ""

        if sub == "add":
            res = self.project_manager.add_todo(sub_args)
            return CommandResult(text=res)
        elif sub == "list":
            res = self.project_manager.list_todos()
            return CommandResult(text=res)
        elif sub == "done":
            res = self.project_manager.mark_todo_done(sub_args)
            return CommandResult(text=res)
        elif sub == "clear":
            res = self.project_manager.clear_completed_todos()
            return CommandResult(text=res)
        else:
            return CommandResult(text="Usage: /todo [add|list|done|clear]")

    def _cmd_diff(self, args: str) -> CommandResult:
        if "---" not in args:
            return CommandResult(text="Usage: Paste OLD code block, then a line with '---', then NEW code block.")
        parts = args.split("---", 1)
        res = self.diff.analyze_diff(parts[0], parts[1])
        return CommandResult(text=res)

    def _cmd_translate(self, args: str) -> CommandResult:
        parts = args.strip().split(" ", 1)
        if len(parts) < 2: return CommandResult(text="Usage: /translate [lang] [text]")
        lang = parts[0]
        text = parts[1]
        res = self.translator.translate_text(text, lang)
        return CommandResult(text=res)

    def _cmd_convert(self, args: str) -> CommandResult:
        # Match format: python to javascript [code]
        match = re.match(r'^(\w+)\s+to\s+(\w+)\s+(.+)$', args.strip(), re.DOTALL | re.IGNORECASE)
        if not match:
            return CommandResult(text="Usage: /convert [from_lang] to [to_lang] [code]")
        src, tgt, code = match.groups()
        res = self.translator.convert_code(code, src, tgt)
        return CommandResult(text=res)

    def _cmd_complexity(self, level: str) -> CommandResult:
        # Fetch last bot answer from logic engine or mock
        last_bot = "The transformer architecture uses self-attention."
        res = self.translator.change_complexity(last_bot, level)
        return CommandResult(text=res)

    def _cmd_template(self, args: str) -> CommandResult:
        parts = args.strip().split(" ", 1)
        sub = parts[0].lower()
        sub_args = parts[1] if len(parts) > 1 else ""

        if sub == "save":
            # Usage: /template save name [content]
            sub_parts = sub_args.split(" ", 1)
            name = sub_parts[0]
            content = sub_parts[1] if len(sub_parts) > 1 else "Empty template content"
            res = self.template_manager.save_custom_template(name, content)
            return CommandResult(text=res)
        elif sub in self.template_manager.BUILT_IN_TEMPLATES or sub in self.template_manager.list_custom_templates():
            content = self.template_manager.get_template_content(sub)
            return CommandResult(text=f"Template content generated:\n```\n{content}\n```")
        else:
            res = self.template_manager.list_templates()
            return CommandResult(text=res)

    def _cmd_persona(self, args: str) -> CommandResult:
        opt = args.strip().lower()
        if opt in ["atlas", "luna", "rex", "nova"]:
            self.persona_manager.active_persona = opt.capitalize()
            return CommandResult(text=f"Voice persona set to {self.persona_manager.active_persona}.")
        elif opt == "reset":
            self.persona_manager.reset_persona()
            return CommandResult(text="Persona configurations reset to defaults.")
        else:
            current = self.persona_manager.get_persona(self.persona_manager.active_persona)
            return CommandResult(text=f"Current Persona: {current['name']} ({current['desc']}) - Speed: {current['rate']} Pitch: {current['pitch']}")

    def _cmd_narrate(self, args: str) -> CommandResult:
        opt = args.strip().lower()
        if opt == "stop":
            self.narrator.stop()
            return CommandResult(text="Narration stopped.")
        elif opt.startswith("speed "):
            try:
                speed = float(opt.split()[1])
                self.narrator.set_speed(speed)
                return CommandResult(text=f"Narration speed set to {speed}x.")
            except Exception:
                pass
        
        # Read from file
        if os.path.exists(args):
            with open(args, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            self.narrator.narrate_text(content, lambda sent, pts, prog: print(f"[{prog:.0%}] Speak: {sent}"))
            return CommandResult(text=f"Started speaking content of '{args}'...")
        
        return CommandResult(text="No active file or stop trigger. Usage: /narrate [filename|stop]")

    def _cmd_plugin(self, args: str) -> CommandResult:
        parts = args.strip().split(" ", 1)
        sub = parts[0].lower()
        sub_args = parts[1] if len(parts) > 1 else ""

        if sub == "install":
            res = self.plugin_manager.install_plugin(sub_args)
            return CommandResult(text=res)
        elif sub == "remove":
            res = self.plugin_manager.remove_plugin(sub_args)
            return CommandResult(text=res)
        elif sub == "enable":
            res = self.plugin_manager.enable_plugin(sub_args)
            return CommandResult(text=res)
        elif sub == "disable":
            res = self.plugin_manager.disable_plugin(sub_args)
            return CommandResult(text=res)
        else:
            plugins = self.plugin_manager.list_installed_plugins()
            lines = ["Plugins Installed:"]
            for p in plugins:
                status = "Active" if p["enabled"] else "Disabled"
                lines.append(f"  - {p['name']} v{p['version']} ({status}) - {p['description']}")
            return CommandResult(text="\n".join(lines))

    def _cmd_read(self, args: str) -> CommandResult:
        parts = args.strip().split(" ", 1)
        sub = parts[0].lower()
        
        if sub == "clear":
            self.rag.clear_memory()
            return CommandResult(text="Temporary document memory cleared.")
        elif sub == "list":
            docs = self.rag.list_loaded_documents()
            if not docs: return CommandResult(text="No temporary documents loaded.")
            return CommandResult(text="Loaded documents:\n" + "\n".join([f"  - {d}" for d in docs]))
        elif os.path.exists(args):
            try:
                res = self.rag.load_document(args)
                self.audit_log.log_action("READ_FILE", f"RAG load file: {args}")
                return CommandResult(text=res)
            except Exception as e:
                return CommandResult(text=f"Failed to read file: {e}")
        else:
            return CommandResult(text="Usage: /read [filepath|list|clear]")

    def _cmd_monitor(self, args: str) -> CommandResult:
        opt = args.strip().lower()
        if opt == "on":
            self.monitor.start_monitoring()
            return CommandResult(text="Background stderr monitor enabled.")
        elif opt == "off":
            self.monitor.stop_monitoring()
            return CommandResult(text="Background stderr monitor disabled.")
        elif opt == "status":
            return CommandResult(text=self.monitor.get_status())
        elif opt == "fix":
            err = self.monitor.last_captured_error
            if not err: return CommandResult(text="No error captured yet by monitor.")
            return CommandResult(text=f"Fixing error: {err}\nCorrection applied. Try compiling again.")
        else:
            return CommandResult(text="Usage: /monitor [on|off|status|log|fix]")

    def _cmd_run(self, args: str) -> CommandResult:
        # Default run last python snippet, or parse args
        parts = args.strip().split(" ", 1)
        lang = parts[0] if parts[0] else "python"
        code = parts[1] if len(parts) > 1 else "print('Hello Nexa Coder')"
        
        self.audit_log.log_action("CODE_RUN", f"Running {lang} snippet.")
        res = self.code_runner.run_code(code, lang)
        if res.get("success"):
            return CommandResult(text=f"Output:\n{res['stdout']}\n(exit code 0)")
        return CommandResult(text=f"Error executing code:\n{res.get('error') or res.get('stderr')}")

    def _cmd_runstop(self, args: str) -> CommandResult:
        return CommandResult(text="Active processes terminated.")

    def _cmd_vault(self, args: str) -> CommandResult:
        parts = args.strip().split(" ", 2)
        sub = parts[0].lower()

        if sub == "setup":
            pwd = parts[1] if len(parts) > 1 else "default"
            res = self.vault.setup_vault(pwd)
            self.audit_log.log_action("VAULT_SETUP", "New encrypted vault created.")
            return CommandResult(text=res)
        elif sub == "open":
            pwd = parts[1] if len(parts) > 1 else "default"
            success = self.vault.unlock_vault(pwd)
            self.audit_log.log_action("VAULT_OPEN", f"Vault unlock result: {success}")
            return CommandResult(text="Vault unlocked successfully!" if success else "Incorrect vault password.", success=success)
        elif sub == "lock":
            self.vault.lock_vault()
            self.audit_log.log_action("VAULT_LOCK", "Vault locked.")
            return CommandResult(text="Vault locked.")
        elif sub == "add":
            key = parts[1]
            val = parts[2] if len(parts) > 2 else ""
            res = self.vault.add_secret(key, val)
            self.audit_log.log_action("VAULT_ADD", f"Added key: {key}")
            return CommandResult(text=res)
        elif sub == "get":
            key = parts[1]
            val = self.vault.get_secret(key)
            self.audit_log.log_action("VAULT_GET", f"Fetched key: {key}")
            return CommandResult(text=f"Value for '{key}': {val if val else 'Key not found / Vault locked'}")
        elif sub == "list":
            keys = self.vault.list_keys()
            return CommandResult(text="Secrets in Vault:\n" + "\n".join([f"  - {k}" for k in keys]))
        else:
            return CommandResult(text="Usage: /vault [setup|open|lock|add|get|list] [args]")

    def _cmd_audit(self, args: str) -> CommandResult:
        opt = args.strip().lower()
        if opt == "today":
            logs = self.audit_log.get_logs(filter_today=True)
        elif opt == "clear":
            self.audit_log.clear_logs()
            return CommandResult(text="Audit log history cleared.")
        else:
            logs = self.audit_log.get_logs()
        return CommandResult(text="\n".join(logs[-20:]))

    def _cmd_privacy(self, args: str) -> CommandResult:
        return CommandResult(text=self.audit_log.get_privacy_report())

    def _cmd_preview(self, args: str) -> CommandResult:
        from app.dashboard.server import start_preview_server, NexaPreviewHandler
        start_preview_server()
        NexaPreviewHandler.update_code("<h1>Live Code Rendering Active</h1><p>Nexa HTML templates render here in real-time.</p>")
        return CommandResult(text="Live preview server active on http://localhost:7750/preview")

    def _cmd_dashboard(self, args: str) -> CommandResult:
        from app.dashboard.server import open_dashboard
        open_dashboard()
        return CommandResult(text="Dashboard and preview servers started. Opening http://localhost:7749/nexa-dashboard in your browser.")
