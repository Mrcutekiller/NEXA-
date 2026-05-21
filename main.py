import os
import sys
import time
import textwrap
import pyttsx3
from colorama import Fore, Style, init

from nexa_engine import NexaLogicEngine
from memory_manager import MemoryManager

# Initialize colorama
init(autoreset=True)

class NexaAI:
    def __init__(self):
        self.memory = MemoryManager()
        # Initialize engine with long-term memory summary
        self.engine = NexaLogicEngine(user_summary=self.memory.get_context_summary())
        
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
{Fore.MAGENTA}{Style.BRIGHT}    _   _  _______  __  _      _ 
{Fore.MAGENTA}{Style.BRIGHT}   | \ | || ____\ \/ / / \    | |
{Fore.MAGENTA}{Style.BRIGHT}   |  \| ||  _|  \  / / _ \   | |
{Fore.MAGENTA}{Style.BRIGHT}   | |\  || |___ /  \/ ___ \  |_|
{Fore.MAGENTA}{Style.BRIGHT}   |_| \_||_____/_/\_/_/   \_\ (_)
        """
        print(logo)
        print(f"{Fore.CYAN}{Style.BRIGHT}    > {self.engine.name} - Version {self.engine.version}")
        print(f"{Fore.CYAN}    > Created by {self.engine.creator}")
        print(f"{Fore.GREEN}    > Status: GOD_EYE LINK ESTABLISHED | ALL SYSTEMS NOMINAL")
        print(f"{Fore.MAGENTA}    ---------------------------------------------------------")

    def start_chat(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        self.show_logo()
        
        # Onboarding for first-time users
        traits = self.memory.memory["user_traits"]
        if traits["name"] is None:
            print(f"{Fore.YELLOW}{Style.BRIGHT}NEXA: {Style.RESET_ALL}Wait... I don't think we've been properly introduced yet.")
            print(f"{Fore.CYAN}NEXA needs a few details to synchronize with your vibe.\n")
            
            name = input(f"{Fore.GREEN}┌──(NEXA)─[Name?]\n└─> {Style.RESET_ALL}").strip()
            age = input(f"{Fore.GREEN}┌──(NEXA)─[Age?]\n└─> {Style.RESET_ALL}").strip()
            interests = input(f"{Fore.GREEN}┌──(NEXA)─[What are you into? (Interests, comma separated)]\n└─> {Style.RESET_ALL}").strip()
            
            traits["name"] = name if name else "Human"
            traits["age"] = age
            traits["interests"] = [i.strip() for i in interests.split(",")] if interests else []
            self.memory.save_memory()
            
            # Refresh engine with new name
            self.engine.user_name = traits["name"]
            
            print(f"\n{Fore.MAGENTA}{Style.BRIGHT}NEXA: {Style.RESET_ALL}Nice to meet you, {traits['name']}. I've locked your data into my memory bank. Let's get started.\n")
            time.sleep(1)
        
        # Check for new session reaction
        summary = self.memory.get_context_summary()
        if summary.get("new_session"):
            reaction = self.engine.get_new_chat_reaction()
            print(f"{Fore.MAGENTA}{Style.BRIGHT}NEXA: {Style.RESET_ALL}{reaction}\n")
            self.speak(reaction)
        
        # Birthday Check on Startup
        bday_message = self.engine.check_birthday()
        if bday_message:
            print(f"{Fore.YELLOW}{Style.BRIGHT}    [BIRTHDAY ALERT] {bday_message}\n")
        
        if not summary.get("new_session"):
            print(f"{Fore.WHITE}    Ready for input. Type 'quit' to exit.\n")

    def get_response(self, user_input):
        # Handle Slash Commands
        if user_input.startswith("/"):
            return self.handle_command(user_input)

        # Analyze and update user vibe/traits in long-term memory
        self.memory.analyze_and_update_vibe(user_input)
        self.memory.add_chat_turn("user", user_input)
        
        # Get response
        response_text = self.engine.generate_response(user_input)
        
        self.memory.add_chat_turn("nexa", response_text)
        return response_text

    def handle_command(self, cmd_input):
        """Processes built-in slash commands."""
        parts = cmd_input.split()
        cmd = parts[0].lower()
        
        if cmd == "/profile":
            print(f"\n{Fore.YELLOW}[PROFILE EDITOR] {Fore.WHITE}Updating your identity...")
            new_name = input(f"{Fore.GREEN}└─> New Name: {Style.RESET_ALL}").strip()
            new_age = input(f"{Fore.GREEN}└─> New Age: {Style.RESET_ALL}").strip()
            
            traits = self.memory.memory["user_traits"]
            if new_name: traits["name"] = new_name
            if new_age: traits["age"] = new_age
            self.memory.save_memory()
            self.engine.user_name = traits["name"]
            return f"Profile synchronized. Welcome, {traits['name']}."

        elif cmd == "/model":
            print(f"\n{Fore.YELLOW}[MODEL SELECTOR] {Fore.WHITE}Current: {self.engine.active_model}")
            print(f"{Fore.CYAN}1. BALANCED | 2. ELITE | 3. GOD_EYE")
            choice = input(f"{Fore.GREEN}└─> Select (1-3): {Style.RESET_ALL}").strip()
            
            modes = {"1": "BALANCED", "2": "ELITE", "3": "GOD_EYE"}
            if choice in modes:
                self.engine.active_model = modes[choice]
                return f"Neural path shifted. Active model: {modes[choice]}"
            return "Invalid selection. Keeping current model."

        elif cmd == "/plan":
            return "Task Architect active. What project are we planning today, Biruk? I can break down complex goals into actionable steps."

        elif cmd == "/engine":
            return f"System Diagnostic: {self.engine.name} {self.engine.version} is stable. Latency: 0.02ms. Memory: OPTIMAL."

        elif cmd == "/help":
            return "/profile - Edit your data\n/model - Switch AI modes\n/plan - Project planning\n/engine - System status"

        return f"Unknown command: {cmd}. Type /help for a list of available protocols."

def main():
    nexa = NexaAI()
    nexa.start_chat()

    while True:
        try:
            # Personalised Claude-style prompt
            user_name = nexa.memory.memory["user_traits"].get("name", "User")
            user_input = input(f"{Fore.GREEN}{Style.BRIGHT}┌──({Fore.WHITE}{user_name}{Fore.GREEN})─[{Fore.WHITE}~{Fore.GREEN}]\n└─> {Style.RESET_ALL}")
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print(f"\n{Fore.MAGENTA}{Style.BRIGHT}NEXA: {Style.RESET_ALL}Shutting down systems. Catch you later, human. 😉")
                nexa.memory.mark_session_end()
                break

            if not user_input.strip():
                continue

            # Processing animation
            print(f"{Fore.MAGENTA}NEXA is thinking...", end="\r")
            time.sleep(0.4)
            
            response = nexa.get_response(user_input)
            
            # Print response with smart text wrapping and typing effect
            print(f"{Fore.MAGENTA}{Style.BRIGHT}NEXA: {Style.RESET_ALL}", end="")
            
            term_width = 80
            try:
                term_width = os.get_terminal_size().columns
            except:
                pass
                
            wrapped_lines = textwrap.wrap(response, width=term_width - 10)
            
            # Start speaking in a non-blocking way if possible, or right before typing
            # For simplicity in terminal, we speak then type, or vice versa. 
            # Most users prefer hearing while reading.
            
            for i, line in enumerate(wrapped_lines):
                if i > 0:
                    print("      ", end="")
                for char in line:
                    print(char, end="", flush=True)
                    time.sleep(0.015)
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
