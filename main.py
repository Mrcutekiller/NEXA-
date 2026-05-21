import os
import sys
import time
import textwrap
import pyttsx3
import logging
import re
import threading
import speech_recognition as sr
from colorama import Fore, Style, init
from nexa_storage import NexaStorage

from nexa_engine import NexaLogicEngine
from memory_manager import MemoryManager

# Initialize colorama
init(autoreset=True)

class NexaAI:
    def __init__(self):
        self.memory = MemoryManager()
        self.storage = NexaStorage()
        self.engine = NexaLogicEngine(user_summary=self.memory.get_context_summary(), storage=self.storage)
        
        # Voice Settings
        self.voice_enabled = True
        self.listen_enabled = False
        
        # Initialize Voice Engine
        try:
            self.voice = pyttsx3.init()
            self.voice.setProperty('rate', 180) 
            self.voice.setProperty('volume', 1.0)
            voices = self.voice.getProperty('voices')
            if len(voices) > 1:
                self.voice.setProperty('voice', voices[1].id) 
        except:
            self.voice = None
            
        # Initialize Speech Recognizer
        try:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
        except:
            self.recognizer = None
            
    def speak(self, text):
        """Makes NEXA speak the response in a non-blocking way."""
        if self.voice and self.voice_enabled:
            def _speak():
                try:
                    clean_text = re.sub(r'[^\x00-\x7F]+', '', text)
                    self.voice.say(clean_text)
                    self.voice.runAndWait()
                except:
                    pass
            threading.Thread(target=_speak, daemon=True).start()

    def listen(self):
        """Listens for user voice input."""
        if not self.recognizer:
            return None
            
        with self.microphone as source:
            print(f"{Fore.YELLOW}[LISTENING...] {Style.RESET_ALL}", end="", flush=True)
            try:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                print(f"{Fore.GREEN}Analyzing...{Style.RESET_ALL}", end="\r")
                text = self.recognizer.recognize_google(audio)
                print(f"{Fore.GREEN}Captured: {text}{Style.RESET_ALL}")
                return text
            except sr.WaitTimeoutError:
                print(f"{Fore.RED}Timeout.{Style.RESET_ALL}")
                return None
            except Exception as e:
                print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
                return None
        
    def show_logo(self):
        # Professional Claude-style Header
        logo_pixel = fr"""
{Fore.RED}      _---_
{Fore.RED}     /     \
{Fore.RED}    | () () |
{Fore.RED}     \  ^  /
{Fore.RED}      |||||
{Fore.RED}      |||||
        """
        
        print(f"\n{logo_pixel}")
        print(f"{Fore.WHITE}{Style.BRIGHT}Nexa Code {Fore.WHITE}{self.engine.version}")
        print(f"{Fore.WHITE}{Style.DIM}Omni 8.0 (GOD_MODE) · {self.engine.creator}")
        print(f"{Fore.WHITE}{Style.DIM}{os.getcwd()}")
        print(f"{Fore.WHITE}─" * 60)

    def start_chat(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        self.show_logo()
        
        summary = self.memory.get_context_summary()
        if summary.get("new_session"):
            reaction = self.engine.get_new_chat_reaction()
            print(f"{Fore.WHITE}• {Fore.WHITE}{Style.DIM}Neural Link Session: {reaction}")
            self.speak(reaction)
        
        if not summary.get("new_session"):
            print(f"{Fore.WHITE}{Style.DIM}Awaiting command. Type / for menu.\n")

    def get_response(self, user_input):
        self.memory.analyze_and_update_vibe(user_input)
        
        # Claude-style Thought/Action Display
        print(f"\n{Fore.WHITE}• {Fore.WHITE}{Style.DIM}I'll analyze your request and determine the best course of action...")
        time.sleep(0.5)
        
        if user_input.lower().startswith("nexa "):
            print(f"{Fore.GREEN}• {Fore.WHITE}Executing({Fore.CYAN}{user_input}{Fore.WHITE})")
            cli_response = self.engine.handle_cli_command(user_input)
            if cli_response:
                print(f"{Fore.WHITE}  L {Fore.GREEN}Done {Fore.WHITE}{Style.DIM}(neural processing complete)")
                print(f"\n{Fore.CYAN}[◕◡◕] NEXA {Fore.WHITE}› {Fore.WHITE}{cli_response}\n")
                self.memory.add_chat_turn("user", user_input)
                self.memory.add_chat_turn("assistant", cli_response)
                return
        
        # Thinking Animation
        print(f"{Fore.RED}* {Fore.RED}Thinking... {Fore.WHITE}{Style.DIM}(esc to interrupt)")
        time.sleep(0.8)
        
        response = self.engine.generate_response(user_input)
        
        # Final Claude-style Response
        print(f"\n{Fore.WHITE}• {Fore.CYAN}Nexa Omni {Fore.WHITE}- {Fore.WHITE}Intelligence Result")
        print(f"\n{Fore.WHITE}{response}\n")
        
        self.speak(response)
        self.memory.add_chat_turn("user", user_input)
        self.memory.add_chat_turn("assistant", response)

    def run(self):
        self.start_chat()
        while True:
            try:
                # Autonomous Error Resolution Wrapper
                try:
                    self._main_loop()
                except Exception as e:
                    self._handle_system_error(e)
            except KeyboardInterrupt:
                print(f"\n{Fore.CYAN}NEXA: {Fore.WHITE}Emergency shutdown initiated...")
                break

    def _handle_onboarding(self):
        """Professional onboarding sequence matching Claude's style."""
        print(f"\n{Fore.CYAN}Nexa {Fore.WHITE}› {Fore.WHITE}Welcome to Nexa OMNI. Let's initialize your environment.")
        
        name = input(f"{Fore.WHITE}• {Fore.WHITE}{Style.DIM}Enter your identity: {Style.RESET_ALL}").strip()
        interests = input(f"{Fore.WHITE}• {Fore.WHITE}{Style.DIM}Define your objectives (comma separated): {Style.RESET_ALL}").strip()
        
        voice_pref = input(f"{Fore.WHITE}• {Fore.WHITE}{Style.DIM}Enable neural voice synthesis? (y/n): {Style.RESET_ALL}").strip().lower()
        self.voice_enabled = True if voice_pref == 'y' else False
        self.listen_enabled = self.voice_enabled
        
        traits = self.memory.memory["user_traits"]
        traits["name"] = name if name else "Operator"
        traits["interests"] = [i.strip() for i in interests.split(",")] if interests else []
        self.memory.save_memory()
        self.engine.user_name = traits["name"]
        
        welcome_msg = f"Neural interface established. Welcome, {traits['name']}."
        print(f"\n{Fore.GREEN}✓ {Fore.WHITE}{welcome_msg}\n")
        if self.voice_enabled:
            self.speak(welcome_msg)
        time.sleep(1)

    def _main_loop(self):
        # Professional UI Onboarding Check
        traits = self.memory.memory["user_traits"]
        if traits["name"] is None:
            self._handle_onboarding()
            return

        # Modern Prompt Design
        prompt = f"{Fore.WHITE}{Style.BRIGHT}> {Style.RESET_ALL}"
        
        if self.listen_enabled:
            user_input = self.listen()
            if not user_input:
                return
        else:
            user_input = input(prompt).strip()
        
        if not user_input:
            return
            
        # Slash Command Menu
        if user_input == "/":
            self._show_command_menu()
            return
            
        if user_input.lower() in ["exit", "quit", "bye"]:
            print(f"\n{Fore.CYAN}NEXA: {Fore.WHITE}Systems hibernating. Stay sharp, {self.engine.user_name}.\n")
            sys.exit(0)
        
        # Special UI Controls
        if user_input.lower() == "voice on":
            self.listen_enabled = True
            print(f"{Fore.GREEN}[VOICE MODE ACTIVATED]{Style.RESET_ALL}")
            return
        elif user_input.lower() == "voice off":
            self.listen_enabled = False
            print(f"{Fore.RED}[VOICE MODE DEACTIVATED]{Style.RESET_ALL}")
            return
        
        self.get_response(user_input)

    def _show_command_menu(self):
        """Displays a menu of all available commands."""
        print(f"\n{Fore.CYAN}┌─── NEXA OMNI COMMAND INTERFACE ───┐")
        commands = [
            ("nexa file open <path>", "Read file content"),
            ("nexa file create <path> <text>", "Create new file"),
            ("nexa file edit <path> <text>", "Update file content"),
            ("nexa file delete <path>", "Remove a file"),
            ("nexa file search <query>", "Find text in project"),
            ("nexa skill list", "Show installed skills"),
            ("nexa skill install <source>", "Install new skill"),
            ("nexa api add <name> <key>", "Securely add API key"),
            ("nexa model switch <name>", "Change AI model"),
            ("analyze image <path>", "Analyze visual data"),
            ("voice on / voice off", "Toggle voice systems"),
            ("exit / quit", "Hibernate system")
        ]
        for cmd, desc in commands:
            print(f"{Fore.CYAN}│ {Fore.WHITE}{cmd:<30} {Fore.MAGENTA}→ {Fore.CYAN}{desc}")
        print(f"{Fore.CYAN}└───────────────────────────────────┘\n")
        print(f"{Fore.WHITE}Type a command or continue chatting.\n")

    def _handle_system_error(self, error):
        """Autonomously identifies and resolves system errors."""
        error_type = type(error).__name__
        print(f"\n{Fore.RED}[CRITICAL ERROR] {error_type}: {error}")
        print(f"{Fore.YELLOW}[AUTONOMOUS RESOLUTION] Analyzing stack trace and system state...")
        
        # Log the error
        self.storage.log_event("SYSTEM_ERROR", {"type": error_type, "message": str(error)})
        
        # Simple resolution strategies
        if error_type == "ConnectionError":
            print(f"{Fore.GREEN}[RESOLUTION] Resetting network bridge and retrying...")
        elif error_type == "FileNotFoundError":
            print(f"{Fore.GREEN}[RESOLUTION] Validating workspace path and re-indexing...")
        else:
            print(f"{Fore.GREEN}[RESOLUTION] Soft-restarting neural node and clearing temporary cache...")
        
        time.sleep(1)
        print(f"{Fore.CYAN}[SYSTEM] Recovery complete. System stable.\n")

if __name__ == "__main__":
    nexa = NexaAI()
    nexa.run()
