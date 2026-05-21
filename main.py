import os
import sys
import time
import textwrap
import pyttsx3
import logging
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
        # Initialize engine with long-term memory summary and storage
        self.engine = NexaLogicEngine(user_summary=self.memory.get_context_summary(), storage=self.storage)
        
        # Initialize Voice Engine
        try:
            self.voice = pyttsx3.init()
            self.voice.setProperty('rate', 175) # Speed of speech
            self.voice.setProperty('volume', 0.9) # Volume (0.0 to 1.0)
            # Set to a more "personality" driven voice if available
            voices = self.voice.getProperty('voices')
            if len(voices) > 1:
                self.voice.setProperty('voice', voices[1].id) # Usually a female/softer voice
        except:
            self.voice = None
            
    def speak(self, text):
        """Makes NEXA speak the response."""
        if self.voice:
            try:
                # Remove emojis for cleaner speech
                clean_text = re.sub(r'[^\x00-\x7F]+', '', text)
                self.voice.say(clean_text)
                self.voice.runAndWait()
            except:
                pass
        
    def show_logo(self):
        logo = fr"""
{Fore.CYAN}{Style.BRIGHT}          _______  _______  _______  _______ 
{Fore.CYAN}{Style.BRIGHT}         |    |  ||    ___||    _  ||   _   |
{Fore.CYAN}{Style.BRIGHT}         |       ||    ___||   |_| ||       |
{Fore.CYAN}{Style.BRIGHT}         |__|____||_______||_______||___|___|
{Fore.MAGENTA}          CORE INTELLIGENCE | NEURAL INTERFACE
        """
        avatar = f"""
{Fore.WHITE}                .--------------.
{Fore.WHITE}                | {Fore.MAGENTA}o {Fore.WHITE}          {Fore.MAGENTA}o {Fore.WHITE}|
{Fore.WHITE}                |     {Fore.CYAN}N E X A {Fore.WHITE}    |
{Fore.WHITE}                '--------------'
        """
        print(logo)
        print(avatar)
        print(f"{Fore.WHITE}    [SYSTEM] {self.engine.name} {self.engine.version}")
        print(f"{Fore.WHITE}    [ARCHITECT] {self.engine.creator}")
        print(f"{Fore.GREEN}    [STATUS] {self.engine.active_model} ONLINE | VAULT LINKED")
        print(f"{Fore.MAGENTA}    " + "─" * 50)

    def start_chat(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        self.show_logo()
        
        # Onboarding for first-time users
        traits = self.memory.memory["user_traits"]
        if traits["name"] is None:
            print(f"\n{Fore.CYAN}NEXA: {Fore.WHITE}Synchronizing neural patterns... I need a few details.")
            
            name = input(f"{Fore.MAGENTA}┌──(SYSTEM)─[Identity?]\n└─> {Style.RESET_ALL}").strip()
            interests = input(f"{Fore.MAGENTA}┌──(SYSTEM)─[Objectives? (comma separated)]\n└─> {Style.RESET_ALL}").strip()
            
            traits["name"] = name if name else "Operator"
            traits["interests"] = [i.strip() for i in interests.split(",")] if interests else []
            self.memory.save_memory()
            
            self.engine.user_name = traits["name"]
            print(f"\n{Fore.CYAN}NEXA: {Fore.WHITE}Identity confirmed. Welcome, {traits['name']}.\n")
            time.sleep(1)
        
        summary = self.memory.get_context_summary()
        if summary.get("new_session"):
            reaction = self.engine.get_new_chat_reaction()
            print(f"{Fore.CYAN}NEXA: {Fore.WHITE}{reaction}\n")
        
        if not summary.get("new_session"):
            print(f"{Fore.WHITE}    Neural link established. Awaiting input.\n")

    def get_response(self, user_input):
        self.memory.analyze_and_update_vibe(user_input)
        
        if user_input.lower().startswith("nexa "):
            cli_response = self.engine.handle_cli_command(user_input)
            if cli_response:
                print(f"{Fore.CYAN}{Style.BRIGHT}[NEXA CLI]:\n{Fore.WHITE}{cli_response}\n")
                self.memory.add_chat_turn("user", user_input)
                self.memory.add_chat_turn("assistant", cli_response)
                return
        
        response = self.engine.generate_response(user_input)
        
        # Professional UI Response Format
        print(f"\n{Fore.CYAN}NEXA {Fore.WHITE}⬢ {Fore.WHITE}", end="", flush=True)
        for char in response:
            print(char, end="", flush=True)
            time.sleep(0.005)
        print("\n")
        
        self.memory.add_chat_turn("user", user_input)
        self.memory.add_chat_turn("assistant", response)

    def run(self):
        self.start_chat()
        while True:
            try:
                # Modern Prompt Design
                prompt = f"{Fore.MAGENTA}┌──({Fore.WHITE}{self.engine.user_name}{Fore.MAGENTA})─[{Fore.WHITE}nexa-os{Fore.MAGENTA}]\n{Fore.MAGENTA}└─{Fore.CYAN}▶ {Style.RESET_ALL}"
                user_input = input(prompt).strip()
                
                if user_input.lower() in ["exit", "quit", "bye"]:
                    print(f"\n{Fore.CYAN}NEXA: {Fore.WHITE}Systems hibernating. Stay sharp, {self.engine.user_name}.\n")
                    break
                
                if not user_input:
                    continue
                
                self.get_response(user_input)
                
            except KeyboardInterrupt:
                print(f"\n{Fore.CYAN}NEXA: {Fore.WHITE}Emergency shutdown initiated...")
                break

if __name__ == "__main__":
    nexa = NexaAI()
    nexa.run()
                print()
            print()
            
            # NEXA Speaks after typing is done (to avoid terminal stutter)
            nexa.speak(response)

        except KeyboardInterrupt:
            print(f"\n\n{Fore.MAGENTA}NEXA: Emergency shutdown triggered. Bye!")
            nexa.memory.mark_session_end()
            break

if __name__ == "__main__":
    main()
