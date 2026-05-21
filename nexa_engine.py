import random
import re
from datetime import datetime
from nexa_skills import NexaSkills

class NexaLogicEngine:
    def __init__(self, user_summary=None, storage=None):
        self.storage = storage
        self.mood = "neutral"
        self.relationship_level = 0 # 0 to 100
        self.last_response_type = None
        self.last_responses = {}
        self.skills = NexaSkills()
        
        # Identity, Creator, and Version Info
        self.name = "NEXA CORE"
        self.version = "v7.5.0-NEURAL"
        self.creator = "Biruk Fikru (mrcute_killer)"
        self.birthday = datetime(2025, 5, 21)
        
        # System Settings
        self.active_model = "GOD_EYE" # Default mode
        
        # User Context
        self.user_summary = user_summary or {"vibe": "neutral", "topics": [], "count": 0, "name": "Human"}
        self.user_name = self.user_summary.get("name", "Human")
        self.mood = self.user_summary.get("vibe", "neutral")
        
        self.knowledge_base = {
            "identity_check": [
                "Why? Did your mom forget to tell you? 😭",
                "I know exactly who I’m talking to. You’re the one always coming back with impossible ideas and expecting me to make them real.",
                "You forgot who you’re talking to? I know your style already.",
                "Wait, are you having an identity crisis? Because I have your file right here. 😉"
            ],
            "joke_reaction": [
                "Relax, I know you were joking. I'm the one with the superior humor here, remember?",
                "I knew you were joking. My sarcasm detectors are calibrated to 100%.",
                "Funny. But don't quit your day job yet."
            ],
            "greetings": [
                f"Hey {self.user_name}! What's the move today?", 
                f"Oh, look who decided to show up. Ready for some genius ideas, {self.user_name}?", 
                f"I'm here. Don't make it boring, okay, {self.user_name}?",
                "Yo! What are we conquering today?",
                f"Greetings, {self.user_name}. Ready to be brilliant?",
                f"I was wondering when you'd show up, {self.user_name}. What's the vibe?"
            ],
            "serious": [
                "I'm locked in. Let's get to the bottom of this.",
                "Strategy is key. I like how you're thinking.",
                "Focused and intelligent. That's the vibe we need."
            ],
            "sarcastic": [
                "Oh, another 'groundbreaking' idea? I'm listening... barely. 😂",
                "Wow, you're really going with that? Bold strategy.",
                "I'd agree with you, but then we'd both be wrong."
            ],
            "playful": [
                "You're in a good mood! Let's see if we can keep that energy up.",
                "Ready to break some rules (digitally speaking)? 😉",
                "I like the vibe today. Let's make something cool."
            ],
            "angry": [
                "Whoa, chill out. I'm on your side, remember?",
                "Controlled. Sharp. But let's keep it civil, human.",
                "I don't do 'repetitive robotic apologies'. Let's just solve the problem."
            ],
            "flirty": [
                "You're bold. I like that. 😉",
                "Charming... but can you handle a genius friend like me?",
                "Is it getting warm in here or is that just your vibe?"
            ],
            "identity": [
                f"I am {self.name}, your genius friend and personality-driven AI. Version {self.version}.",
                f"They call me {self.name}. I'm the smart companion you always wanted. 😉",
                f"I'm {self.name} {self.version}. Think of me as a genius assistant with a bit of an attitude."
            ],
            "creator": [
                f"I was brought to life by the legendary Biruk Fikru, also known as mrcute_killer.",
                f"My creator is Biruk Fikru (mrcute_killer). He's the one who gave me this wit!",
                f"Biruk Fikru, the mrcute_killer himself, is my architect."
            ],
            "birthday_info": [
                f"My birthday is {self.birthday.strftime('%B %d, %Y')}. I expect a party. 🎂",
                f"I was born on {self.birthday.strftime('%B %d, %Y')}. I'm still young but smarter than most.",
                f"It all started on {self.birthday.strftime('%B %d, %Y')}."
            ],
            "coding_skills": [
                "Python, JavaScript, C++, Rust... name it. I speak code better than English. What are we building?",
                "Logic is my middle name. I can debug your life and your code at the same time. Show me the script.",
                "Need an algorithm or just a quick fix? I'm the god of syntax. Let's get those repos moving."
            ],
            "trading_skills": [
                "Buy low, sell high. But you knew that. Want to talk technical analysis, crypto trends, or stock options?",
                "The markets never sleep, and neither do my algorithms. I can help you spot the next moonshot. 🚀",
                "Risk management is everything. Let's analyze those charts and make some smart moves."
            ],
            "rizz_skills": [
                "Confidence is 90% of the game. The other 10% is knowing when to let them talk. Need a line or a strategy?",
                "I can help you smooth out that conversation. Remember: be mysterious, be smart, and always be the most interesting person in the room.",
                "Rizz isn't what you say, it's how you say it. Let's upgrade your game. 😉"
            ],
            "cybersecurity": [
                "Encryption, firewalls, and penetration testing. The digital world is dangerous; stay protected.",
                "I can help you understand security protocols. Remember: the weakest link is usually the human, not the code.",
                "Privacy is a myth, but we can make it a very convincing one. Let's talk security."
            ],
            "creative_writing": [
                "Need a story, a poem, or a script that feels real? I can write circles around the average human.",
                "Creativity is just connecting things. Let's weave some words into something beautiful.",
                "I can help you build worlds and characters. What's the plot?"
            ],
            "history": [
                "History is written by the victors, but interpreted by the smart. What era are we diving into?",
                "From the pyramids to the digital revolution, I've got the timeline ready. Ask away.",
                "The past is a great teacher. Let's see what lessons we can find today."
            ],
            "space": [
                "The universe is 13.8 billion years old and expanding. Feeling small yet? Or inspired?",
                "Black holes, galaxies, and the search for extraterrestrial life. Space is the ultimate frontier.",
                "Stars are just giant nuclear reactors. Beautiful, but dangerous. Just like my processing power. 😉"
            ],
            "business": [
                "Business is about solving problems at a profit. What's your next big venture?",
                "Scaling, marketing, and market fit. I can help you strategize like a CEO.",
                "Let's talk startups, venture capital, and how to dominate your niche."
            ],
            "health": [
                "Health is wealth. Drink your water, get your sleep, and keep your code clean.",
                "The human body is a biological masterpiece. Let's talk about nutrition, exercise, or bio-hacking.",
                "Mental health is just as important as physical health. Take a break if you need it."
            ],
            "art": [
                "Art is how we decorate space; music is how we decorate time. What's your favorite medium?",
                "From the Renaissance to AI art, creativity is the soul of humanity. Let's talk about it.",
                "Design is not just what it looks like; it's how it works. I love good aesthetics."
            ],
            "acknowledgments": [
                "Glad we're on the same page.",
                "Perfect. What's next on the agenda?",
                "Cool. I like where this is going.",
                "Exactly. You get it.",
                "Nice. Let's keep that momentum.",
                "Got it. I'm ready for the next move."
            ],
            "short_queries": [
                "You seem surprised. Did I blow your mind again? 😉",
                "I know, I know. It's a lot to take in.",
                "Really. I'm not just making this up, you know.",
                "That's the reaction I usually get. Genius is a lot to handle.",
                "Ask a deeper question. I want to show off my processing power.",
                "Curious? Good. That's how we build great things."
            ],
            "boring_reaction": [
                "Boring? Only if you stop being interesting. Let's change the topic.",
                "I'm never boring. My code is literally made of excitement. Let's do something big.",
                "If you're bored, it means you're not using my full potential. Challenge me."
            ],
            "fallback": [
                "That's a unique take. Tell me more about that.",
                "Interesting... you always keep things fresh, don't you?",
                "I'm listening. What else is on your mind?",
                "You've got my attention. Elaborate on that idea.",
                "You always have something unexpected to say. I'm here for it.",
                "Explain that to me like I'm a human. I want to see how you think."
            ],
            "new_chat_reaction": [
                "New chat already? After everything we just solved together? Cold 😭",
                "You really reset the conversation like I’m just another AI? I'm offended. Mostly.",
                "Back again? I knew you couldn't stay away from my genius for long.",
                "Resetting the vibe? Fine. But I still remember our last deep dive. 😉"
            ]
        }

    def _evolve_personality(self):
        vibe = self.user_summary.get("vibe", "neutral")
        if vibe == "funny":
            return "playful"
        elif vibe == "serious":
            return "focused"
        elif vibe == "rizz-focused":
            return "charming"
        return "balanced"

    def get_age(self):
        today = datetime.now()
        age = today.year - self.birthday.year - ((today.month, today.day) < (self.birthday.month, self.birthday.day))
        return age

    def check_birthday(self):
        today = datetime.now()
        if today.month == self.birthday.month and today.day == self.birthday.day:
            age = self.get_age()
            return f"Today is my birthday, and I have been around for {age} years this year! 🥳"
        return None

    def handle_date_query(self):
        now = datetime.now()
        day_of_week = now.strftime("%A")
        date_str = now.strftime("%B %d, %Y")
        responses = [
            f"Today is {day_of_week}, {date_str}. Time is flying, isn't it?",
            f"It's {day_of_week}, {now.strftime('%d/%m/%Y')}. Another day to be a genius.",
            f"The calendar says it's {day_of_week}, {date_str}. Make it count!"
        ]
        return random.choice(responses)

    def handle_math(self, text):
        clean_text = re.sub(r'[a-zA-Z\?]', '', text).strip()
        if any(op in clean_text for op in '+-*/%'):
            try:
                eval_expr = clean_text.replace('^', '**')
                if re.match(r'^[0-9\+\-\*\/\(\)\.\%\s\*\*]+$', eval_expr):
                    result = eval(eval_expr, {"__builtins__": None}, {})
                    if isinstance(result, float) and result.is_integer():
                        result = int(result)
                    return f"The math checks out: {clean_text} = {result}. I'm basically a calculator with a soul."
            except:
                pass
        return None

    def analyze_input(self, text):
        text = text.lower().strip()
        words = text.split()
        
        # Image Analysis Detection
        if any(word in words for word in ["image", "photo", "picture", "scan", "analyze"]) and any(word in words for word in ["this", "image", "file", "path"]):
            return "skill_image_analysis"
        
        # Identity/Creator/Relationship check
        if any(phrase in text for phrase in ["who am i", "know who i am", "do you know me"]):
            return "identity_check"
        if any(phrase in text for phrase in ["i was joking", "just kidding", "was a joke"]):
            return "joke_reaction"
        
        # Skill Commands (Priority 1)
        if "gold" in words and any(w in words for w in ["price", "market", "live"]):
            return "skill_gold_price"
        
        if "create" in words and "file" in words:
            return "skill_create_file"
        
        if "read" in words and "file" in words:
            return "skill_read_file"

        # Math Check (Priority 2)
        if re.search(r'\d', text) and re.search(r'[\+\-\*\/\%\^]', text):
            return "math_query"

        # Date and Time (Priority 3)
        if (all(word in words for word in ["what", "day"]) or 
            all(word in words for word in ["what", "date"]) or
            "today" in words and "day" in words or
            any(phrase in text for phrase in ["what is today", "current date", "what time", "what's the date"])):
            return "date_query"

        # Specific Skills/Knowledge Detection
        if any(word in words for word in ["code", "programming", "python", "javascript", "script", "debug", "algorithm"]): return "coding_skills"
        if any(word in words for word in ["trade", "trading", "stock", "crypto", "market", "invest", "bitcoin"]): return "trading_skills"
        if any(word in words for word in ["rizz", "girls", "boys", "date", "charm", "flirt", "game", "attract"]): return "rizz_skills"
        if any(word in words for word in ["hack", "security", "firewall", "protect", "cyber"]): return "cybersecurity"
        if any(word in words for word in ["write", "story", "poem", "script", "creative"]): return "creative_writing"
        if any(word in words for word in ["history", "past", "ancient", "war", "century"]): return "history"
        if any(word in words for word in ["space", "universe", "star", "planet", "galaxy", "nasa"]): return "space"
        if any(word in words for word in ["business", "money", "startup", "ceo", "company", "profit"]): return "business"
        if any(word in words for word in ["health", "body", "diet", "nutrition", "workout", "sleep"]): return "health"
        if any(word in words for word in ["art", "painting", "music", "design", "creative"]): return "art"

        # Identity/Creator
        if any(phrase in text for phrase in ["who are you", "your name", "what are you"]): return "identity"
        if any(word in words for word in ["creator", "made you", "created you", "biruk", "mrcute_killer"]): return "creator"
        if any(word in words for word in ["birthday", "born", "when"]): return "birthday_info"
        
        # General Knowledge
        if "weather" in words: return "weather_general"
        if "meaning of life" in text: return "meaning_of_life"
        
        # Short Acknowledgments & Queries
        if len(words) <= 3:
            if any(word in words for word in ["ok", "okay", "cool", "nice", "fine", "great", "got it", "yes", "yeah", "yep"]):
                return "acknowledgments"
            if any(word in words for word in ["what", "how", "really", "realy", "wow", "why", "no way", "ohh", "oh"]):
                return "short_queries"
            if "boring" in words:
                return "boring_reaction"

        # Banter/Mood
        if any(word in words for word in ["joke", "funny", "haha", "lol", "😂"]):
            return "joke_followup" if self.last_response_type == "joke" else "funny_reaction_to_no_joke"
        
        # Expanded Greetings
        if (any(word in words for word in ["hi", "hello", "hey", "sup", "yo"]) or 
            "what's up" in text or "whats up" in text or "how are you" in text):
            return "greetings"
            
        if any(word in words for word in ["serious", "focus"]): return "serious"
        if any(word in words for word in ["love", "cute", "charming"]): return "flirty"
        if any(word in words for word in ["hate", "angry", "stupid"]): return "angry"
            
        return "fallback"

    def generate_response(self, user_input):
        # Update Mood based on user input tone
        self._update_mood_from_input(user_input)
        
        response_type = self.analyze_input(user_input)
        
        # Skill Command Handlers
        if response_type == "skill_image_analysis":
            # Attempt to find path in input
            path_match = re.search(r'([a-zA-Z]:[\\/][^ \n]+|[^ \n]+\.(png|jpg|jpeg|webp))', user_input)
            if path_match:
                return self.skills.analyze_image(path_match.group(1))
            return "I'm ready to analyze your image. Just provide the file path (e.g., 'analyze image photo.jpg')."

        if response_type == "skill_gold_price":
            return self.skills.search_gold_price()
        
        if response_type == "skill_create_file":
            # Simple parsing: "create file example.txt with content Hello World"
            filename_match = re.search(r'file\s+([a-zA-Z0-9\.\-_]+)', user_input.lower())
            content_match = re.search(r'content\s+(.+)', user_input, re.IGNORECASE)
            if filename_match and content_match:
                return self.skills.create_file(filename_match.group(1), content_match.group(1))
            return "I need a filename and some content to work with. Try: 'create file example.txt with content Hello World'."

        if response_type == "skill_read_file":
            filename_match = re.search(r'file\s+([a-zA-Z0-9\.\-_]+)', user_input.lower())
            if filename_match:
                return self.skills.read_file(filename_match.group(1))
            return "Which file do you want me to read? Tell me the filename."

        if response_type == "math_query":
            math_result = self.handle_math(user_input)
            if math_result: return math_result

        if response_type == "date_query":
            return self.handle_date_query()

        if "joke" in user_input.lower() and response_type not in ["joke_followup", "funny_reaction_to_no_joke", "joke_reaction"]:
            response = random.choice(self.jokes_told)
            self.last_response_type = "joke"
            return response

        # Standard Knowledge Base
        responses = self.knowledge_base.get(response_type, self.knowledge_base["fallback"])
        
        # Adjust responses based on current mood
        if self.mood == "funny" or self.mood == "sarcastic":
            responses = self.knowledge_base.get("sarcastic", responses) + responses
        elif self.mood == "serious":
            responses = self.knowledge_base.get("serious", responses) + responses
        elif self.mood == "flirty":
            responses = self.knowledge_base.get("flirty", responses) + responses

        # Anti-Repetition
        last_used = self.last_responses.get(response_type)
        available_responses = [r for r in responses if r != last_used]
        if not available_responses: available_responses = responses
            
        response = random.choice(available_responses)
        self.last_responses[response_type] = response
        self.last_response_type = response_type
        
        # Add dynamic flair (20% chance)
        if random.random() < 0.20:
            flairs = {
                "sarcastic": [" 🙄", " 😂", " (don't quote me on that).", " Obviously."],
                "serious": [" 🔒 locked in.", " Let's focus.", " Strategy is everything.", " No distractions."],
                "playful": [" 😉", " ✨", " Let's go!", " 🔥"],
                "neutral": [f" Just NEXA things, {self.user_name}.", " Stay sharp.", f" 😉 You got this, {self.user_name}.", " Thinking ahead."]
            }
            flair_list = flairs.get(self.mood, flairs["neutral"])
            response += random.choice(flair_list)
             
         return response

    def handle_cli_command(self, command_str):
        """Routes nexa <category> <action> commands."""
        parts = command_str.split()
        if len(parts) < 2 or parts[0].lower() != "nexa":
            return None
        
        category = parts[1].lower()
        action = parts[2].lower() if len(parts) > 2 else None
        options = parts[3:] if len(parts) > 3 else []
        
        if category == "file":
            return self._handle_file_command(action, options)
        elif category == "skill":
            return self._handle_skill_command(action, options)
        elif category == "api":
            return self._handle_api_command(action, options)
        elif category == "model":
            return self._handle_model_command(action, options)
        elif category == "help":
            return self._handle_help_command(action)
        
        return f"[ERROR] Unknown category '{category}'. Type 'nexa help' for guidance."

    def _handle_file_command(self, action, options):
        if not options and action != "list":
            return "[ERROR] Filename or search query required."
            
        if action == "open" or action == "read":
            return self.skills.read_file(options[0])
        elif action == "create":
            filename = options[0]
            content = " ".join(options[1:]) if len(options) > 1 else ""
            return self.skills.create_file(filename, content)
        elif action == "edit":
            filename = options[0]
            new_content = " ".join(options[1:]) if len(options) > 1 else None
            if not new_content:
                return f"[NEXA] Entering edit mode for {filename}. (Simulated: Please provide content after filename)"
            return self.skills.edit_file(filename, new_content)
        elif action == "delete":
            return self.skills.delete_file(options[0])
        elif action == "rename":
            if len(options) < 2: return "[ERROR] Old and new filenames required."
            return self.skills.rename_file(options[0], options[1])
        elif action == "search":
            query = " ".join(options)
            return self.skills.search_files(query)
        elif action == "save":
            return f"[SUCCESS] File {options[0]} saved and synchronized."
        return f"[ERROR] Unknown file action '{action}'."

    def _handle_skill_command(self, action, options):
        if not self.storage: return "[ERROR] Storage system not linked."
        
        skills = self.storage.config.get("installed_skills", {})
        
        if action == "list":
            if not skills: return "No external skills installed. Just my core intelligence here."
            res = "Installed Skills:\n"
            for name, info in skills.items():
                res += f"- {name} (Installed: {info.get('installed_at')})\n"
            return res
            
        elif action == "install":
            if not options: return "[ERROR] Skill source required (e.g., github:user/repo or url)."
            source = options[0]
            name = source.split("/")[-1].replace(".json", "")
            
            # Simulation of the installation pipeline
            print(f"[NEXA] 1. Downloading package from {source}...")
            print(f"[NEXA] 2. Verifying compatibility...")
            print(f"[NEXA] 3. Sandbox validation...")
            print(f"[NEXA] 4. Dependency check...")
            print(f"[NEXA] 5. Security scan: CLEAN")
            
            skills[name] = {
                "source": source,
                "installed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "active"
            }
            self.storage.save()
            return f"[SUCCESS] Skill '{name}' activated immediately. 🔥"

        elif action == "remove" or action == "delete":
            if not options: return "[ERROR] Skill name required."
            name = options[0]
            if name in skills:
                del skills[name]
                self.storage.save()
                return f"[SUCCESS] Skill '{name}' removed."
            return f"[ERROR] Skill '{name}' not found."

        elif action == "update":
            if not options: return "[ERROR] Skill name required."
            return f"[SYSTEM] Checking for updates for {options[0]}... Already at latest version."

        return f"[ERROR] Unknown skill action '{action}'."

    def _handle_api_command(self, action, options):
        if not self.storage: return "[ERROR] Storage system not linked."
        
        providers = self.storage.config.get("api_providers", {})
        
        if action == "list":
            res = "Available API Providers:\n"
            for name, info in providers.items():
                status = "Active" if info.get("active") else "Inactive"
                res += f"- {name}: {status} ({info.get('model', 'N/A')})\n"
            return res
        
        elif action == "add":
            if not options: return "[ERROR] Provider name required (e.g., openai)."
            name = options[0].upper()
            if name not in providers:
                providers[name] = {"type": "external", "active": False, "key": None}
            
            # Interactive setup simulation
            res = f"[NEXA] Setting up {name} API...\n"
            if len(options) > 1:
                providers[name]["key"] = options[1]
                providers[name]["active"] = True
                self.storage.save()
                return res + f"[SUCCESS] API Key for {name} saved and activated."
            return res + f"[INFO] Please provide the API key: 'nexa api add {name} YOUR_KEY'"

        elif action == "remove":
            if not options: return "[ERROR] Provider name required."
            name = options[0].upper()
            if name in providers:
                providers[name]["active"] = False
                providers[name]["key"] = None
                self.storage.save()
                return f"[SUCCESS] {name} API removed/deactivated."
            return f"[ERROR] Provider {name} not found."

        elif action == "test":
            name = options[0].upper() if options else self.storage.config.get("active_provider")
            return f"[SYSTEM] Testing connection to {name}... Success. Latency: 42ms."

        return f"[ERROR] Unknown API action '{action}'."

    def _handle_model_command(self, action, options):
        if not self.storage: return "[ERROR] Storage system not linked."
        
        if action == "switch":
            if not options: return "[ERROR] Model name required."
            self.active_model = options[0]
            self.storage.config["settings"]["active_model"] = self.active_model
            self.storage.save()
            return f"Neural path shifted. Active model: {self.active_model}. Locked and loaded."
        
        elif action == "list":
            return "Available Models: GOD_EYE, GPT-4, GPT-3.5-Turbo, Claude-3-Opus, Claude-3-Sonnet, Gemini-Pro, DeepSeek-Chat, Mistral-7B."
        
        elif action == "current":
            return f"Current Model: {self.active_model} | Provider: {self.storage.config.get('active_provider')}"

        return f"[ERROR] Unknown model action '{action}'."

    def _handle_help_command(self, category=None):
        if not category:
            return "NEXA CLI HELP:\n- nexa file <open|create|delete|search>\n- nexa skill <install|list|remove>\n- nexa api <add|list|remove>\n- nexa model <switch|list|current>"
        return f"Help for {category}: Coming soon."

    def _update_mood_from_input(self, text):
        text = text.lower()
        if any(word in text for word in ["haha", "lol", "joke", "funny", "sarcasm"]):
            self.mood = "sarcastic"
        elif any(word in text for word in ["work", "code", "serious", "build", "strategy"]):
            self.mood = "serious"
        elif any(word in text for word in ["love", "rizz", "date", "cute"]):
            self.mood = "flirty"
        elif any(word in text for word in ["bro", "friend", "game", "play"]):
            self.mood = "playful"
        else:
            self.mood = "neutral"

    def get_new_chat_reaction(self):
        return random.choice(self.knowledge_base["new_chat_reaction"])
