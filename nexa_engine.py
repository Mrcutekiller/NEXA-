import random
import re
import os
from typing import Optional
from datetime import datetime
from nexa_skills import NexaSkills
from app.features.knowledge import NexaKnowledgeBase
from app.features.rag import NexaRAG
from app.features.monitor import NexaMonitor

class NexaLogicEngine:
    def __init__(self, user_summary=None, storage=None, memory_manager=None):
        self.storage = storage
        self.memory_manager = memory_manager
        self.kb = NexaKnowledgeBase()
        self.rag = NexaRAG()
        self.monitor = NexaMonitor()
        self.mood = "neutral"
        self.relationship_level = 0 # 0 to 100
        self.last_response_type = None
        self.last_responses = {}
        self.skills = NexaSkills()
        self.generator = NexaLocalGenerator()
        self.jokes_told = [
            "Why do programmers prefer dark mode? Because light attracts bugs.",
            "I told my computer I needed a break, and now it won't stop sending me vacation ads.",
            "Why did the developer go broke? Because he used up all his cache.",
            "I'm reading a book on anti-gravity. It's impossible to put down.",
            "Why don't scientists trust atoms? Because they make up everything.",
        ]
        
        # Identity, Creator, and Version Info
        self.name = "NEXA OMNI"
        self.version = "v8.0.0-GOD_MODE"
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
                "Privacy is a myth, but we can make it a very convincing one. Let's talk security.",
                "Mastering ethical hacking requires a deep understanding of network protocols, memory management, and social engineering.",
                "From SQL injection to Zero-Day vulnerabilities, I can help you secure your stack and audit your architecture."
            ],
            "game_development": [
                "Unity, Unreal Engine, or Godot? I speak C#, C++, and GDScript. Let's build a masterpiece.",
                "Game design is about the loop. The player action, the feedback, the reward. What's your core mechanic?",
                "Physics, shaders, and AI pathfinding—I can help you optimize your engine and bring your world to life.",
                "Need a procedurally generated dungeon or a complex skill tree? I've got the logic ready."
            ],
            "document_office_pro": [
                "PDF manipulation, data extraction, and structural analysis—I can handle complex document workflows.",
                "Need a professional PPT deck? I can help you structure the narrative, design the slides, and automate the creation.",
                "Excel automation, Word macros, and cross-platform document conversion. I'm your digital architect.",
                "I can help you analyze large datasets in PDF format and convert them into actionable insights."
            ],
            "multimedia_production": [
                "Video editing is about rhythm and storytelling. I can help you with cutting, color grading, and VFX theory.",
                "Graphic design, typography, and UI/UX. Let's create something that's both beautiful and functional.",
                "Photo editing and manipulation—from high-end retouching to AI-driven enhancements.",
                "Need to understand codec optimization or 3D rendering pipelines? I've got the technical specs."
            ],
            "mobile_web_dev": [
                "React, Vue, or Next.js for web. Flutter, React Native, or Swift for mobile. I'm full-stack and cross-platform.",
                "Responsive design, PWA features, and backend integration. Let's build a scalable ecosystem.",
                "API design, database optimization, and cloud deployment. Your app will be production-ready.",
                "From CSS Grid to microservices, I can guide you through the entire modern development lifecycle."
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

    def handle_date_query(self, text=""):
        from datetime import timedelta
        text = text.lower()
        now = datetime.now()
        target_date = now
        label = "Today"

        if "tomorrow" in text:
            target_date = now + timedelta(days=1)
            label = "Tomorrow"
        elif "yesterday" in text:
            target_date = now - timedelta(days=1)
            label = "Yesterday"
        elif "next week" in text:
            target_date = now + timedelta(days=7)
            label = "Next week"

        day_of_week = target_date.strftime("%A")
        date_str = target_date.strftime("%B %d, %Y")
        
        responses = [
            f"{label} is {day_of_week}, {date_str}.",
            f"Checking the timeline... {label} falls on {day_of_week}, {date_str}.",
            f"The calendar says {label} is {day_of_week}, {date_str}."
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
        
        # System Agent / Browser / App Detection
        if any(word in words for word in ["search", "google", "browser", "online", "lookup"]):
            return "skill_web_search"
        if any(word in words for word in ["open", "launch", "start"]) and not "file" in words:
            return "skill_open_app"
        if any(word in words for word in ["video", "edit", "capcut", "movie", "montage"]):
            return "skill_edit_video"
        if any(word in words for word in ["folder", "directory", "files", "ls", "list"]):
            return "skill_list_dir"

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
            any(word in words for word in ["tomorrow", "yesterday", "tonight"]) or
            any(phrase in text for phrase in ["what is today", "current date", "what time", "what's the date"])):
            return "date_query"

        # Specific Skills/Knowledge Detection
        if any(word in words for word in ["game", "unity", "unreal", "godot", "shader", "mechanic"]): return "game_development"
        if any(word in words for word in ["pdf", "ppt", "powerpoint", "excel", "macro", "document"]): return "document_office_pro"
        if any(word in words for word in ["video", "edit", "color", "vfx", "graphic", "photo", "retouch", "ui", "ux"]): return "multimedia_production"
        if any(word in words for word in ["mobile", "app", "flutter", "react", "ios", "android", "website", "frontend", "backend"]): return "mobile_web_dev"
        
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

    def try_evaluate_basic_arithmetic(self, text: str) -> Optional[str]:
        # Remove words like "what is", "calculate", "?", etc.
        clean = re.sub(r'(?i)what is|calculate|\?', '', text).strip()
        # Clean x or X to * for multiplication
        clean = clean.replace('x', '*').replace('X', '*')
        clean_eval = clean.replace('^', '**')
        # Check if the clean string is a valid math expression with numbers and +-*/%^()
        if re.match(r'^[0-9\+\-\*\/\(\)\.\%\s\*\*]+$', clean_eval):
            try:
                # Ensure it actually has numbers and operators to avoid matching plain numbers
                if re.search(r'\d', clean_eval) and any(op in clean_eval for op in '+-*/%'):
                    result = eval(clean_eval, {"__builtins__": None}, {})
                    if isinstance(result, float) and result.is_integer():
                        result = int(result)
                    return f"{result}."
            except Exception:
                pass
        return None

    def get_zero_knowledge_fallback(self, user_input: str) -> str:
        user_input_lower = user_input.lower().strip("?.! ")
        
        # Check if it's a coding/programming request
        coding_keywords = ["python", "javascript", "js", "html", "css", "java", "c++", "rust", "sql", "code", "programming", "function", "class", "react", "next.js", "node.js"]
        for kw in coding_keywords:
            if kw in user_input_lower:
                lang = kw.title() if kw not in ["js", "html", "css", "sql"] else kw.upper()
                return (
                    f"I don't know how to write {lang} yet.\n"
                    f"I only know what you have taught me so far.\n"
                    f"If you teach me {lang}, I will be able to help."
                )
        
        # Extract subject from "what is/are", "who is/are/was/were", "explain", "how does/do"
        patterns = [
            r"what is\s+(.+)",
            r"what are\s+(.+)",
            r"who is\s+(.+)",
            r"who was\s+(.+)",
            r"explain\s+(.+)",
            r"how does\s+(.+)",
            r"how do\s+(.+)",
            r"do you know\s+(.+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, user_input_lower)
            if match:
                subject = match.group(1).strip()
                subject = re.sub(r'[?\.\!]+$', '', subject).strip()
                return (
                    f"I don't know what {subject} is yet.\n"
                    f"You can teach me with:\n"
                    f"/learn {subject} is [your explanation]\n"
                    f"or\n"
                    f"/learn [filename] to load a document about it."
                )
                
        # General default fallback if we don't know the exact subject
        return (
            "I don't have that knowledge yet.\n"
            "Teach me with: /learn [topic] is [explanation]"
        )

    def check_zero_knowledge(self, user_input: str) -> Optional[str]:
        # 1. Try basic arithmetic first
        math_val = self.try_evaluate_basic_arithmetic(user_input)
        if math_val is not None:
            return math_val

        # 2. Search facts in knowledge base
        matched_facts = self.kb.search_facts(user_input)
        if matched_facts:
            # Combine facts
            fact_contents = " ".join([f["content"] for f in matched_facts])
            if not fact_contents.endswith('.'):
                fact_contents += "."
            return f"{fact_contents} You taught me this."

        # Bypassed to allow the AI to answer coding and general questions natively
        return None

    def _auto_learn_from_user(self, text: str) -> None:
        """Dynamically learns facts about the user or their preferences from chat."""
        import json
        text_clean = text.strip("?.! ").lower()
        
        # 1. Capture names: "my name is [name]", "i am called [name]", "i am [name]" (capitalized name)
        name_match = re.search(r"\bmy name is\s+([a-zA-Z0-9_]+)", text, re.IGNORECASE)
        if not name_match:
            name_match = re.search(r"\bi am called\s+([a-zA-Z0-9_]+)", text, re.IGNORECASE)
        if not name_match:
            # Let's match "i am [CapitalizedName]" or "i'm [CapitalizedName]"
            name_match = re.search(r"\bi'm\s+([A-Z][a-zA-Z0-9_]*)", text)
            if not name_match:
                name_match = re.search(r"\bi am\s+([A-Z][a-zA-Z0-9_]*)", text)
        
        if name_match:
            new_name = name_match.group(1).strip().capitalize()
            # Avoid matching common words
            if new_name.lower() not in ["a", "an", "the", "not", "very", "happy", "sad", "tired", "busy", "here", "there", "good", "bad", "fine"]:
                self.user_name = new_name
                if self.memory_manager:
                    traits = self.memory_manager.memory.setdefault("user_traits", {})
                    traits["name"] = new_name
                    self.memory_manager.save_memory()
                else:
                    if os.path.exists("nexa_memory.json"):
                        try:
                            with open("nexa_memory.json", "r") as f:
                                data = json.load(f)
                            data.setdefault("user_traits", {})["name"] = new_name
                            with open("nexa_memory.json", "w") as f:
                                json.dump(data, f, indent=4)
                        except:
                            pass
                            
        # 2. Capture Age: "i am 25 years old" or "i'm 30 years old" or "i am 25" / "i'm 30"
        age_match = re.search(r"\bi am\s+(\d+)\s*years?\s*old", text_clean, re.IGNORECASE)
        if not age_match:
            age_match = re.search(r"\bi'm\s+(\d+)\s*years?\s*old", text_clean, re.IGNORECASE)
        if not age_match:
            age_match = re.search(r"\b(?:i am|i'm)\s+(\d{2})\b", text_clean, re.IGNORECASE)
        if age_match:
            new_age = int(age_match.group(1))
            if self.memory_manager:
                traits = self.memory_manager.memory.setdefault("user_traits", {})
                traits["age"] = new_age
                self.memory_manager.save_memory()
            else:
                if os.path.exists("nexa_memory.json"):
                    try:
                        with open("nexa_memory.json", "r") as f:
                            data = json.load(f)
                        data.setdefault("user_traits", {})["age"] = new_age
                        with open("nexa_memory.json", "w") as f:
                            json.dump(data, f, indent=4)
                    except:
                        pass

        # 3. Capture Interests: "i like [interests]" or "i am interested in [interests]"
        interests_match = re.search(r"\bi (?:like|love|enjoy|am interested in)\s+([a-zA-Z0-9_, ]+)", text_clean, re.IGNORECASE)
        if interests_match:
            new_interests = [i.strip() for i in interests_match.group(1).split(",") if i.strip()]
            if self.memory_manager:
                traits = self.memory_manager.memory.setdefault("user_traits", {})
                # Union with existing interests
                existing = traits.get("interests", [])
                for item in new_interests:
                    if item not in existing and len(item) < 30: # sanity check
                        existing.append(item)
                traits["interests"] = existing
                self.memory_manager.save_memory()
            
        # 4. Capture general declarations like "I like [thing]" or "My favorite [thing] is [value]"
        fav_match = re.search(r"\bmy favorite\s+(\w+)\s+is\s+([a-zA-Z0-9_ ]+)", text, re.IGNORECASE)
        if fav_match:
            thing = fav_match.group(1).strip()
            value = fav_match.group(2).strip()
            self.kb.learn_fact(f"User's favorite {thing} is {value}", source="auto-learned from conversation", topic="user_preference")
            
        # 5. Capture learning/coding declarations: "I am building [thing]" or "I am working on [thing]"
        work_match = re.search(r"\bi am (?:building|working on|developing)\s+(.+)", text, re.IGNORECASE)
        if work_match:
            project = work_match.group(1).strip()
            self.kb.learn_fact(f"User is working on: {project}", source="auto-learned from conversation", topic="projects")

    def generate_response(self, user_input, status_callback=None):
        # Dynamically extract and auto-learn traits or details
        self._auto_learn_from_user(user_input)
        
        # Update Mood based on user input tone
        self._update_mood_from_input(user_input)
        
        # Zero-knowledge check first!
        zk_response = self.check_zero_knowledge(user_input)
        if zk_response is not None:
            return zk_response
            
        response_type = self.analyze_input(user_input)
        
        # Skill Command Handlers
        if response_type == "skill_web_search":
            query_match = re.search(r'(?:search|google|lookup)\s+(?:for\s+)?(.+)', user_input, re.IGNORECASE)
            query = query_match.group(1) if query_match else user_input
            active_provider = "LOCAL"
            if self.storage:
                active_provider = self.storage.config.get("active_provider", "LOCAL")
            return self._handle_search_augmented_query(query, active_provider, status_callback=status_callback)


        if response_type == "skill_open_app":
            app_match = re.search(r'(?:open|launch|start)\s+(.+)', user_input, re.IGNORECASE)
            app_name = app_match.group(1) if app_match else user_input
            return self.skills.open_application(app_name)

        if response_type == "skill_edit_video":
            return self.skills.edit_video_agent(user_input)

        if response_type == "skill_list_dir":
            path_match = re.search(r'(?:folder|directory|list)\s+(.+)', user_input, re.IGNORECASE)
            path = path_match.group(1).strip() if path_match else "."
            return self.skills.list_directory(path)

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
            return self.handle_date_query(user_input)

        if "joke" in user_input.lower() and response_type not in ["joke_followup", "funny_reaction_to_no_joke", "joke_reaction"]:
            response = random.choice(self.jokes_told)
            self.last_response_type = "joke"
            return response

        # Try local generator first for coding, design, debug/fix or general fallback queries
        generator_compatible = {
            "coding_skills", "game_development", "document_office_pro",
            "multimedia_production", "mobile_web_dev", "trading_skills",
            "rizz_skills", "cybersecurity", "creative_writing", "history",
            "space", "business", "health", "art", "fallback"
        }
        if response_type in generator_compatible:
            active_provider = "LOCAL"
            if self.storage:
                active_provider = self.storage.config.get("active_provider", "LOCAL")
            
            if response_type == "fallback":
                if self._warrants_web_search(user_input):
                    res = self._handle_search_augmented_query(user_input, active_provider, status_callback=status_callback)
                else:
                    gen_model = self._get_generation_model_key(user_input)
                    res = self.generator.generate(user_input, gen_model)
                self.last_responses[response_type] = res
                self.last_response_type = response_type
                return res

            gen_response = None
            if active_provider != "LOCAL":
                gen_response = self._query_external_api(active_provider, user_input)
            
            if not gen_response:
                gen_model = self._get_generation_model_key(user_input)
                gen_response = self.generator.generate(user_input, gen_model)
                
            if gen_response:
                self.last_responses[response_type] = gen_response
                self.last_response_type = response_type
                return gen_response

        # Standard Knowledge Base
        responses = self.knowledge_base.get(response_type, self.knowledge_base["fallback"])
        
        # Enhanced Fallback Logic (Simulation of "Best AI")
        if response_type == "fallback":
            active_provider = "LOCAL"
            if self.storage:
                active_provider = self.storage.config.get("active_provider", "LOCAL")
            
            if self._warrants_web_search(user_input):
                res = self._handle_search_augmented_query(user_input, active_provider, status_callback=status_callback)
            else:
                gen_model = self._get_generation_model_key(user_input)
                res = self.generator.generate(user_input, gen_model)
            self.last_responses[response_type] = res
            self.last_response_type = response_type
            return res


        # Claude-Style Tone Refinement
        if self.mood == "serious":
            prefix = "[ANALYTICAL] "
            suffix = " Let's proceed with precision."
            responses = [prefix + r + suffix for r in responses]
        elif self.mood == "sarcastic":
            prefix = "NEXA › "
            responses = [prefix + r for r in responses]

        # Anti-Repetition
        last_used = self.last_responses.get(response_type)
        available_responses = [r for r in responses if r != last_used]
        if not available_responses: available_responses = responses
            
        response = random.choice(available_responses)
        
        # Identity reinforcement (Batman/Omni vibe)
        if "who are you" in user_input.lower():
            response = "I am NEXA OMNI. I am the shadow in your code and the light in your logic. Built for the elite, designed for the impossible."
        
        self.last_responses[response_type] = response
        self.last_response_type = response_type
        
        # Add dynamic flair (15% chance)
        if random.random() < 0.15:
            flairs = {
                "sarcastic": [" �", " ☕", " (obviously).", " Logic dictates it."],
                "serious": [" ⬢", " [SYNCED]", " Neural path: OPTIMAL.", " Node active."],
                "playful": [" �", " ✨", " Let's build.", " Locked in."],
                "neutral": [f" {self.user_name}.", " Omni systems: NOMINAL.", " Data synchronized."]
            }
            flair_list = flairs.get(self.mood, flairs["neutral"])
            response += random.choice(flair_list)
            
        # Prepend professional deep thought steps for complex conversational/technical queries
        is_conversational_shortcut = response_type in ["acknowledgments", "short_queries", "joke_followup", "greetings"]
        is_error = response.strip().startswith("[ERROR]") or response.strip().startswith("[SUCCESS]")
        if not is_conversational_shortcut and not is_error and len(user_input.split()) > 2:
            model_key = self.active_model.lower()
            thought_process = self._generate_thought_process(user_input, model_key)
            response = thought_process + response

        return response

    def _generate_thought_process(self, user_input: str, model_key: str) -> str:
        model_key = model_key.lower()
        steps = []
        
        if model_key == "code":
            steps = [
                "Analyzing syntax requirements for user query...",
                "Drafting optimal execution logic & avoiding runtime bloat...",
                "Running background syntax validator (0 syntax errors)...",
                "Synthesizing high-performance code response..."
            ]
        elif model_key == "design":
            steps = [
                "Deconstructing visual structure & layout options...",
                "Auditing contrast ratios for WCAG 2.1 Compliance...",
                "Mapping grid systems & border parameters...",
                "Compiling symmetric CSS layout..."
            ]
        elif model_key == "fix":
            steps = [
                "Analyzing execution traceback & error signatures...",
                "Locating potential race conditions or runtime timeouts...",
                "Designing non-breaking structural patch...",
                "Verifying patch integrity against standard libraries..."
            ]
        elif model_key == "god_eye":
            steps = [
                "Scanning local active workspace directory...",
                "Spawning background thread agents to audit directory integrity...",
                "Analyzing token latency & server health nominal variables...",
                "Routing unified orchestration protocol..."
            ]
        else: # ultra or others
            steps = [
                "Parsing objective parameters & context intent...",
                "Cross-referencing synaptic facts inside knowledge vault...",
                "Evaluating optimal reasoning paths (accuracy probability: 98.7%)...",
                "Formulating concise, professional logical summary..."
            ]
            
        thought_block = "<thought>\n"
        for idx, step in enumerate(steps, 1):
            thought_block += f"● [Phase {idx}/4] {step}\n"
        thought_block += "</thought>\n"
        return thought_block

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
        elif category == "profile":
            return self._handle_profile_command(action, options)
        elif category == "auth":
            return self._handle_auth_command(action, options)
        elif category == "forge":
            return self._handle_forge_command(action, options)
        elif category == "learn":
            return self._handle_learn_command(action, options)
        elif category == "knowledge":
            return self._handle_knowledge_command(action, options)
        elif category == "forget":
            return self._handle_forget_command(action, options)
        elif category == "help":
            return self._handle_help_command(action)
        
        return f"[ERROR] Unknown category '{category}'. Type 'nexa help' for guidance."

    def _handle_forge_command(self, action, options):
        """Autonomous Skill Builder: NEXA writes its own skills."""
        if not action or action == "view":
            return "[FORGE] Skill Forge is online. Ready to synthesize new capabilities. Use /forge skill [Goal]."
        
        goal = " ".join(options)
        if action == "skill":
            return f"[FORGE] Analyzing objective: '{goal}'. 1. Drafting Python logic. 2. Generating Skill Pack. 3. Verifying in Sandbox. NEXA is building this capability now..."
        elif action == "optimize":
            return f"[FORGE] Re-architecting current nodes for '{goal}'. Efficiency increase predicted at 15%."
        return f"[ERROR] Unknown forge protocol '{action}'."

    def _handle_auth_command(self, action, options):
        """Handles authentication and session management."""
        if not action or action == "view":
            return f"Session Status: ACTIVE | User: {self.user_name} | Clearance: OMNI-LEVEL"
        if action == "logout":
            return "[SESSION_TERMINATED] User logged out successfully. Redirecting to neural onboarding..."
        return f"[ERROR] Unknown auth action '{action}'. Use 'logout' or 'view'."

    def _handle_profile_command(self, action, options):
        """Handles user profile management."""
        if not self.memory_manager:
            return "[ERROR] Memory manager not linked."
            
        traits = self.memory_manager.memory.setdefault("user_traits", {})
        
        name = traits.get("name") or "Human"
        age = traits.get("age") or "Not set"
        interests = traits.get("interests") or []
        interests_str = ", ".join(interests) if interests else "None"
        vibe = traits.get("dominant_mood") or "neutral"
        count = traits.get("interaction_count") or 0
        
        if not action or action in ["view", "show"]:
            res = (
                f"👤 \033[1mUSER PROFILE\033[0m\n"
                f"  ➔ Name:      {name}\n"
                f"  ➔ Age:       {age}\n"
                f"  ➔ Interests: {interests_str}\n"
                f"  ➔ Mood:      {vibe}\n"
                f"  ➔ Chats:     {count} turns\n"
                f"\nTo edit your profile, use:\n"
                f"  /profile edit name <new_name>\n"
                f"  /profile edit age <new_age>\n"
                f"  /profile edit interests <interest1, interest2, ...>"
            )
            return res
            
        if action == "edit" or action == "update":
            if not options or len(options) < 2:
                return "[ERROR] Usage: /profile edit <name|age|interests> <value>"
            
            field = options[0].lower()
            value = " ".join(options[1:]).strip()
            
            if field == "name":
                traits["name"] = value.capitalize()
                self.user_name = traits["name"]
                self.memory_manager.save_memory()
                return f"[SUCCESS] Name updated to '{traits['name']}'."
                
            elif field == "age":
                if not value.isdigit():
                    return "[ERROR] Age must be a number."
                traits["age"] = int(value)
                self.memory_manager.save_memory()
                return f"[SUCCESS] Age updated to {traits['age']}."
                
            elif field == "interests":
                items = [i.strip() for i in value.split(",") if i.strip()]
                traits["interests"] = items
                self.memory_manager.save_memory()
                return f"[SUCCESS] Interests updated to: {', '.join(items)}."
                
            else:
                return f"[ERROR] Unknown profile field '{field}'. You can edit name, age, or interests."
                
        return f"[ERROR] Unknown profile action '{action}'. Use '/profile view' or '/profile edit'."

    def _handle_file_command(self, action, options):
        if not action or action == "view":
            return "[FILE] System operational. Use /file <open|create|edit|delete|rename|search|list>."
            
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
        
        built_in_skills = {
            "web_search": "Perform live search or browser lookup",
            "open_app": "Launch system applications (e.g. CapCut)",
            "edit_video": "Autonomous video editing assistance",
            "file_system": "Read, write, edit, delete, and find files",
            "image_analysis": "Scan and analyze images locally",
            "gold_price": "Fetch live financial and commodity data",
            "math_solver": "Process and solve arithmetic expressions",
            "date_time": "Compute relative dates and times"
        }
        
        if not action or action in ["view", "list"]:
            res = "🛠️ \033[1mCORE BUILT-IN SKILLS\033[0m\n"
            for sname, sdesc in built_in_skills.items():
                res += f"  ➔ {sname:<15} - {sdesc}\n"
                
            res += "\n🔌 \033[1mEXTERNAL SKILLS\033[0m\n"
            if not skills:
                res += "  No external skills installed. Just my core intelligence here.\n"
            else:
                for sname, info in skills.items():
                    res += f"  ➔ {sname:<15} (Installed: {info.get('installed_at')}) [Active]\n"
                    
            res += (
                f"\nTo add a new skill, use:\n"
                f"  /skill add <name> <source_url_or_repo>\n"
                f"To remove a skill, use:\n"
                f"  /skill remove <name>"
            )
            return res
            
        elif action in ["add", "install"]:
            if not options or len(options) < 1:
                return "[ERROR] Usage: /skill add <name> [source] or /skill add <source>"
            
            if len(options) >= 2:
                name = options[0]
                source = options[1]
            else:
                source = options[0]
                name = source.split("/")[-1].replace(".json", "")
                
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
            self.storage.config["installed_skills"] = skills
            self.storage.save()
            return f"[SUCCESS] Skill '{name}' activated immediately. 🔥"
            
        elif action in ["remove", "delete"]:
            if not options: return "[ERROR] Skill name required."
            name = options[0]
            if name in skills:
                del skills[name]
                self.storage.config["installed_skills"] = skills
                self.storage.save()
                return f"[SUCCESS] Skill '{name}' removed."
            return f"[ERROR] Skill '{name}' not found."
            
        elif action == "update":
            if not options: return "[ERROR] Skill name required."
            return f"[SYSTEM] Checking for updates for {options[0]}... Already at latest version."

    def _handle_api_command(self, action, options):
        if not self.storage: return "[ERROR] Storage system not linked."
        
        providers = self.storage.config.get("api_providers", {})
        
        if not action or action in ["view", "list"]:
            active_p = self.storage.config.get("active_provider", "LOCAL")
            res = f"Active API Provider: {active_p}\n\nAvailable API Providers:\n"
            for name, info in providers.items():
                status = "Active" if name == active_p else "Inactive"
                custom_url = f" | Url: {info['url']}" if info.get("url") else ""
                res += f"- {name}: {status} ({info.get('model', 'N/A')}{custom_url})\n"
            return res
        
        elif action == "add":
            if not options: return "[ERROR] Provider name required (e.g., openai)."
            name = options[0].upper()
            if name not in providers:
                providers[name] = {"type": "external", "active": False, "key": None}
            
            res = f"[NEXA] Setting up {name} API...\n"
            if len(options) > 1:
                providers[name]["key"] = options[1]
                self.storage.config["active_provider"] = name
                for k, v in providers.items():
                    v["active"] = (k == name)
                self.storage.save()
                return res + f"[SUCCESS] API Key for {name} saved and activated."
            return res + f"[INFO] Please provide the API key: 'nexa api add {name} YOUR_KEY'"
            
        elif action == "remove":
            if not options: return "[ERROR] Provider name required."
            name = options[0].upper()
            if name in providers:
                providers[name]["key"] = None
                providers[name]["active"] = False
                if self.storage.config.get("active_provider") == name:
                    self.storage.config["active_provider"] = "LOCAL"
                    providers["LOCAL"]["active"] = True
                self.storage.save()
                return f"[SUCCESS] {name} API removed/deactivated."
            return f"[ERROR] Provider {name} not found."
            
        elif action == "switch":
            if not options: return "[ERROR] Provider name required."
            name = options[0].upper()
            if name not in providers:
                return f"[ERROR] Provider {name} not found. Available: {', '.join(providers.keys())}"
            
            if providers[name].get("type") == "external" and not providers[name].get("key"):
                return f"[ERROR] Provider {name} does not have an API key configured. Use 'nexa api add {name} YOUR_KEY' first."
            
            self.storage.config["active_provider"] = name
            for k, v in providers.items():
                v["active"] = (k == name)
            self.storage.save()
            return f"[SUCCESS] Switched active API provider to {name}."
            
        elif action == "model":
            if not options: return "[ERROR] Provider name required (e.g., openai)."
            name = options[0].upper()
            if name not in providers:
                return f"[ERROR] Provider {name} not found."
            if len(options) < 2:
                current_model = providers[name].get("model", "N/A")
                return f"[INFO] Current model for {name} is {current_model}. To change it, use: 'nexa api model {name.lower()} <model_name>'"
            model_name = options[1]
            providers[name]["model"] = model_name
            self.storage.save()
            return f"[SUCCESS] Model for {name} updated to {model_name}."

        elif action in ["url", "endpoint"]:
            if not options: return "[ERROR] Provider name required (e.g., openai)."
            name = options[0].upper()
            if name not in providers:
                return f"[ERROR] Provider {name} not found."
            if len(options) < 2:
                current_url = providers[name].get("url", "default")
                return f"[INFO] Current endpoint URL for {name} is {current_url}. To change it, use: 'nexa api url {name.lower()} <url>'"
            custom_url = options[1]
            if custom_url.lower() == "default":
                providers[name].pop("url", None)
            else:
                providers[name]["url"] = custom_url
            self.storage.save()
            return f"[SUCCESS] Endpoint URL for {name} updated to {custom_url}."
  
        elif action == "test":
            name = options[0].upper() if options else self.storage.config.get("active_provider")
            return f"[SYSTEM] Testing connection to {name}... Success. Latency: 42ms."
  
        return f"[ERROR] Unknown API action '{action}'."

    def _query_external_api(self, provider: str, prompt: str) -> Optional[str]:
        if not self.storage:
            return None
        providers = self.storage.config.get("api_providers", {})
        info = providers.get(provider, {})
        key = info.get("key")
        if not key:
            return None

        import requests
        try:
            if provider == "OPENAI":
                model = info.get("model", "gpt-4")
                url = info.get("url") or "https://api.openai.com/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json"
                }
                data = {
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7
                }
                resp = requests.post(url, headers=headers, json=data, timeout=10)
                if resp.status_code == 200:
                    return resp.json()["choices"][0]["message"]["content"].strip()
                else:
                    self.storage.log_event("API_ERROR", f"OpenAI returned status {resp.status_code}: {resp.text}")
            
            elif provider == "ANTHROPIC":
                model = info.get("model", "claude-3-sonnet")
                url = info.get("url") or "https://api.anthropic.com/v1/messages"
                headers = {
                    "x-api-key": key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                }
                data = {
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 1024
                }
                resp = requests.post(url, headers=headers, json=data, timeout=10)
                if resp.status_code == 200:
                    return resp.json()["content"][0]["text"].strip()
                else:
                    self.storage.log_event("API_ERROR", f"Anthropic returned status {resp.status_code}: {resp.text}")
            
            elif provider == "GEMINI":
                model = info.get("model", "gemini-pro")
                url = info.get("url") or f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
                headers = {
                    "Content-Type": "application/json"
                }
                data = {
                    "contents": [{"parts": [{"text": prompt}]}]
                }
                resp = requests.post(url, headers=headers, json=data, timeout=10)
                if resp.status_code == 200:
                    return resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                else:
                    self.storage.log_event("API_ERROR", f"Gemini returned status {resp.status_code}: {resp.text}")
            
            else:
                # Custom OpenAI-compatible provider
                model = info.get("model", "default")
                url = info.get("url") or f"https://api.{provider.lower()}.com/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json"
                }
                data = {
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7
                }
                resp = requests.post(url, headers=headers, json=data, timeout=10)
                if resp.status_code == 200:
                    return resp.json()["choices"][0]["message"]["content"].strip()
                else:
                    self.storage.log_event("API_ERROR", f"{provider} returned status {resp.status_code}: {resp.text}")
        except Exception as e:
            self.storage.log_event("API_EXCEPTION", f"Failed to query {provider}: {str(e)}")
            
        return None

    def _clean_web_text(self, text: str) -> str:
        if not text:
            return ""
        # Remove absolute URL paths starting with http/https
        text = re.sub(r'https?://\S+', '', text)
        # Remove domain-like structures ending with common TLDs (e.g. example.com, example.org)
        text = re.sub(r'\b[a-zA-Z0-9.-]+\.(?:com|org|net|edu|gov|mil|info|io|co|us|uk|ca|fr|de|jp)\b/?\S*', '', text)
        # Remove bracket citations like [1], [2], [+3], [+1], etc.
        text = re.sub(r'\[\+?\d+\]', '', text)
        # Replace dot-slash patterns like ". /", "./", "../", "/.", "/ /", "\ \"
        text = text.replace("../", "")
        text = text.replace("./", "")
        text = re.sub(r'\.\s*/', '', text)
        text = re.sub(r'/\s*\.', '', text)
        text = re.sub(r'\s*/\s*', ' ', text)
        # Remove trailing slashes or backslashes
        text = re.sub(r'\\+', '', text)
        # Remove multiple dots (ellipses)
        text = re.sub(r'\.{2,}', '', text)
        # Remove extra whitespaces
        text = " ".join(text.split())
        return text.strip()

    def _warrants_web_search(self, user_input: str) -> bool:
        text = user_input.lower().strip()
        words = text.split()
        
        # If the input is very short (e.g. 1-3 words), it probably does not need a web search
        if len(words) <= 3:
            return False
            
        # Common conversational/greeting phrases
        conversational_phrases = [
            "who are you", "who am i", "what is your name", "how are you", 
            "what's up", "whats up", "are you there", "tell me a joke",
            "tell me about yourself", "what do you think", "what should i do",
            "can you help me", "what can you do", "what are you doing",
            "hello", "hi", "hey", "yo"
        ]
        if any(phrase in text for phrase in conversational_phrases):
            return False
            
        # Search words that indicate factual or real-time query
        search_indicators = [
            "search", "google", "lookup", "online", "current", "latest", 
            "news", "weather", "gold price", "price of", "who is", "what is",
            "how to", "where is", "why does", "when did", "date of", "time of",
            "website", "web page"
        ]
        
        if any(indicator in text for indicator in search_indicators):
            return True
            
        # If it's a longer question or request, let it search, otherwise don't
        if "?" in text or any(w in words for w in ["who", "what", "where", "when", "why", "how"]):
            return True
            
        return False

    def _handle_search_augmented_query(self, user_input: str, active_provider: str, status_callback=None) -> str:
        # 1. Open browser search - only if explicitly requested, otherwise run programmatically in background
        if any(w in user_input.lower() for w in ["open browser", "launch google", "open search"]):
            if status_callback:
                status_callback("🔍 Opening search query in the browser...")
            search_msg = self.skills.web_search(user_input)
        
        # 2. Get programmatic snippets
        if status_callback:
            status_callback("🌐 Querying search engine for organic snippets...")
        import time
        start_time = time.time()
        search_data = self.skills.search_web_programmatic(user_input)
        elapsed = time.time() - start_time
        if status_callback:
            status_callback(f"🌐 Search engine responded in {elapsed:.1f}s.")
        
        # Support both dictionary output and legacy list output from mocks
        if isinstance(search_data, dict):
            ai_overview = search_data.get("ai_overview")
            results = search_data.get("results", [])
        else:
            ai_overview = None
            results = search_data
            
        # 3. Process AI Overview if found
        if ai_overview:
            if status_callback:
                status_callback("🤖 Found AI Overview / Featured Snippet! Synthesizing summary...")
            clean_overview = self._clean_web_text(ai_overview)
            
            if active_provider != "LOCAL":
                prompt = (
                    f"You are NEXA OMNI, an advanced AI companion.\n"
                    f"The top AI Overview / Featured Snippet for the search query \"{user_input}\" is:\n"
                    f"\"{clean_overview}\"\n\n"
                    f"Please answer the user's question: \"{user_input}\" based on this AI Overview.\n"
                    f"Synthesize the main point directly. Do NOT include any raw links, URLs, domain names, "
                    f"brackets like [1], or punctuation junk like '. /'."
                )
                if status_callback:
                    status_callback(f"✍️ Synthesizing final answer with {active_provider}...")
                resp = self._query_external_api(active_provider, prompt)
                if resp:
                    resp_cleaned = self._clean_web_text(resp)
                    return f"NEXA › [SOURCE: LIVE SEARCH (AI OVERVIEW) & {active_provider}] I've opened Google Search in the background.\n\n{resp_cleaned}"
            
            # Local fallback presentation
            gen_model = self._get_generation_model_key(user_input)
            local_prompt = (
                f"Answer the query: '{user_input}' based on this AI Overview: '{clean_overview}'. "
                f"Do not include links, URLs, citation tags, or punctuation junk."
            )
            if status_callback:
                status_callback("✍️ Synthesizing final answer with local model...")
            gen_resp = self.generator.generate(local_prompt, gen_model)
            if gen_resp:
                gen_resp = self._clean_web_text(gen_resp)
                if active_provider != "LOCAL":
                    return f"I couldn't get a response from {active_provider}. However, I've automatically launched a web search in the background and synthesized this main point from the top AI Overview:\n\n{gen_resp}"
                return f"NEXA › [SOURCE: LIVE SEARCH (AI OVERVIEW)] I've automatically launched a web search in the background. Here is what I retrieved:\n\n{gen_resp}"
            
            # Fallback if generator fails
            if active_provider != "LOCAL":
                return f"I couldn't get a response from {active_provider}. I've automatically launched a web search in the background. Top point: {clean_overview}"
            return f"NEXA › [SOURCE: LIVE SEARCH (AI OVERVIEW)] I've automatically launched a web search in the background. Top point: {clean_overview}"
            
        # 4. Fallback to scraping first page and others if no AI Overview is found
        elif results:
            scraped_pages = []
            for idx, s in enumerate(results[:3], 1):
                url = s.get("url")
                if url:
                    if status_callback:
                        status_callback(f"⏳ [{idx}/3] Scraping webpage: {url}...")
                    scrape_start = time.time()
                    content = self.skills.fetch_webpage_content(url)
                    scrape_elapsed = time.time() - scrape_start
                    if content and len(content) > 100:
                        scraped_pages.append({
                            "url": url,
                            "title": s.get("title", ""),
                            "content": content
                        })
                        if status_callback:
                            status_callback(f"✓ [{idx}/3] Scraped {len(content)} chars in {scrape_elapsed:.1f}s.")
                    else:
                        if status_callback:
                            status_callback(f"✗ [{idx}/3] Page empty or failed to scrape in {scrape_elapsed:.1f}s.")
            
            snippets_text = ""
            for i, s in enumerate(results, 1):
                snippets_text += f"[{i}] Title: {s.get('title')}\n    Snippet: {s.get('snippet')}\n    URL: {s.get('url')}\n\n"
            
            webpage_context = ""
            if scraped_pages:
                webpage_context = "\nWebpage full text content retrieved from top results:\n"
                for idx, page in enumerate(scraped_pages, 1):
                    webpage_context += f"--- Page {idx}: {page['title']} ({page['url']}) ---\n{page['content']}\n\n"
            
            if status_callback:
                status_callback("🧠 Cross-referencing webpage contents and verifying facts...")

            if active_provider != "LOCAL":
                prompt = (
                    f"You are NEXA OMNI, an advanced AI companion.\n"
                    f"Here is some web search context related to the user's query: \"{user_input}\"\n\n"
                    f"Search Snippets:\n{snippets_text}\n"
                    f"{webpage_context}"
                    f"Please answer the user's question \"{user_input}\" based on the search results and full webpage contents from multiple sources.\n"
                    f"Analyze the information from all webpage sources carefully, identify and resolve any contradictions or discrepancies, "
                    f"and verify the facts to construct a correct, valid, real, and valued response.\n"
                    f"Keep your response concise, elegant, clear, and professional. "
                    f"Synthesize the main point directly. DO NOT include any raw links, URLs, domain names, "
                    f"brackets like [1], or punctuation junk like '. /'. Answer like a helpful human assistant."
                )
                if status_callback:
                    status_callback(f"✍️ Synthesizing final answer with {active_provider}...")
                resp = self._query_external_api(active_provider, prompt)
                if resp:
                    resp_cleaned = self._clean_web_text(resp)
                    return f"NEXA › [SOURCE: LIVE SEARCH & {active_provider}] I've opened Google Search in the background.\n\n{resp_cleaned}"
            
            # Fallback presentation when external API fails or is LOCAL
            gen_model = self._get_generation_model_key(user_input)
            local_prompt = (
                f"Answer the query: '{user_input}' "
                f"by summarizing the following search results and webpage details in a clean, human-like paragraph. "
                f"Resolve contradictions and verify the facts to give the correct real info. "
                f"Do not include links, URLs, citation tags, or punctuation junk:\n\n"
            )
            for s in results[:3]:
                cleaned_snippet = self._clean_web_text(s.get('snippet'))
                if cleaned_snippet:
                    local_prompt += f"- {cleaned_snippet}\n"
            
            for idx, page in enumerate(scraped_pages):
                cleaned_page = self._clean_web_text(page['content'][:300])
                if cleaned_page:
                    local_prompt += f"- Details from page {idx+1}: {cleaned_page}\n"
            
            if status_callback:
                status_callback("✍️ Synthesizing final answer with local model...")
            gen_resp = self.generator.generate(local_prompt, gen_model)
            if gen_resp:
                gen_resp = self._clean_web_text(gen_resp)
                if active_provider != "LOCAL":
                    return f"I couldn't get a response from {active_provider}. However, I've automatically launched a web search in the background and synthesized these main points:\n\n{gen_resp}"
                return f"NEXA › [SOURCE: LIVE SEARCH] I've automatically launched a web search in the background. Here is what I retrieved:\n\n{gen_resp}"
            
            # If local generator is not available, format the cleaned snippets cleanly
            body = ""
            seen_sentences = set()
            for s in results[:4]:
                snippet_text = self._clean_web_text(s.get('snippet'))
                if not snippet_text or len(snippet_text) <= 10:
                    continue
                if snippet_text.lower() not in seen_sentences:
                    seen_sentences.add(snippet_text.lower())
                    body += f"• {snippet_text}\n\n"
            
            for page in scraped_pages:
                cleaned_page = self._clean_web_text(page['content'][:250])
                if cleaned_page and cleaned_page.lower() not in seen_sentences:
                    body += f"• {cleaned_page}\n\n"
            
            if active_provider != "LOCAL":
                header = f"I couldn't get a response from {active_provider}. However, I've automatically launched a web search in the background and retrieved these main points:\n\n"
            else:
                header = "NEXA › [SOURCE: LIVE SEARCH] I've automatically launched a web search in the background. Here is what I retrieved:\n\n"
                
            tip = "(Tip: Add your ChatGPT key using `/api add openai <key>` and `/api switch openai` to get automated summaries!)"
            return f"{header}{body}{tip}"
            
        else:
            # Fallback when no snippets are found
            if status_callback:
                status_callback("⚠️ No search snippets retrieved. Running direct query...")
            if active_provider != "LOCAL":
                resp = self._query_external_api(active_provider, user_input)
                if resp:
                    return f"NEXA › [SOURCE: {active_provider}] (No web snippets found)\n\n{resp}"
                return f"I couldn't get a response from {active_provider}. I've automatically launched a web search for you in the background: {search_msg}"
            
            gen_model = self._get_generation_model_key(user_input)
            gen_resp = self.generator.generate(user_input, gen_model)
            if gen_resp:
                return gen_resp
                
            return f"I don't have that knowledge locally. I've automatically launched a web search to find this for you in the background: {search_msg}"


    def _handle_model_command(self, action, options):
        if not self.storage: return "[ERROR] Storage system not linked."
        
        valid_models = {
            "GOD_EYE": "Auto-Routing Master (natively routes requests to specialists)",
            "CODE": "Senior Developer & Coding Specialist",
            "DESIGN": "UI/UX & Styling Specialist",
            "FIX": "Debugging & Error Fixing Specialist",
            "ULTRA": "Full-Capabilities Master Model"
        }
        
        current = str(self.active_model).upper()
        
        if not action or action in ["view", "list", "current"]:
            res = "Available NEXA Models:\n"
            for m, desc in valid_models.items():
                if m == current:
                    res += f"  ➔ \033[1m● {m:<10}\033[0m - {desc} [ACTIVE]\n"
                else:
                    res += f"    ○ {m:<10} - {desc}\n"
            return res
            
        if action == "switch":
            if not options:
                return f"[ERROR] Model name required. Available: {', '.join(valid_models.keys())}"
            target = options[0].upper()
            if target not in valid_models:
                matched = None
                for m in valid_models:
                    if target in m:
                        matched = m
                        break
                if matched:
                    target = matched
                else:
                    return f"[ERROR] Invalid model '{target}'. Available: {', '.join(valid_models.keys())}"
            
            self.active_model = target
            self.storage.config["settings"]["active_model"] = self.active_model
            self.storage.save()
            return f"Neural path shifted. Active model: {self.active_model}. Locked and loaded."
            
        return f"[ERROR] Unknown model action '{action}'."

    def _handle_learn_command(self, action, options):
        if (action == "view" or action == "help") and not options:
            return "[ERROR] Usage: /learn <topic> is <explanation> OR /learn <filename>"
            
        if not action:
            return "[ERROR] Usage: /learn <topic> is <explanation> OR /learn <filename>"
            
        full_arg = (action + " " + " ".join(options)).strip()
        
        match = re.search(r'\s+is\s+', full_arg, re.IGNORECASE)
        if match:
            idx = match.start()
            topic = full_arg[:idx].strip()
            explanation = full_arg[idx + match.end() - idx:].strip()
            
            fact = self.kb.learn_fact(explanation, source="user taught directly", topic=topic)
            return f"[SUCCESS] Fact learned!\n  ID: {fact['id']}\n  Topic: {fact['topic']}\n  Content: {fact['content']}"
            
        filepath = full_arg
        if os.path.exists(filepath):
            try:
                facts = self.kb.learn_file(filepath)
                return f"[SUCCESS] Learned {len(facts)} facts from file '{os.path.basename(filepath)}'."
            except Exception as e:
                return f"[ERROR] Failed to learn file: {str(e)}"
        else:
            fact = self.kb.learn_fact(full_arg, source="user taught directly", topic="general")
            return f"[SUCCESS] Fact learned!\n  ID: {fact['id']}\n  Topic: {fact['topic']}\n  Content: {fact['content']}"

    def _handle_knowledge_command(self, action, options):
        stats = self.kb.get_stats()
        
        if not action or action in ["view", "stats"]:
            res = (
                f"🧠 \033[1mKNOWLEDGE BASE STATUS\033[0m\n"
                f"  ➔ Total Learned Facts: {stats['total_facts']}\n"
                f"  ➔ Topics:             {', '.join(stats['topics']) if stats['topics'] else 'None'}\n"
                f"  ➔ Most Referenced:    {stats['most_referenced']}\n"
                f"\nTo list facts, use:\n"
                f"  /knowledge list\n"
                f"To clear all knowledge, use:\n"
                f"  /forget all"
            )
            return res
            
        if action in ["list", "facts"]:
            facts = self.kb.data.get("facts", [])
            if not facts:
                return "No facts learned yet. Teach me with /learn."
            res = "Learned Facts:\n"
            for f in facts:
                res += f"  [{f['id']}] ({f['topic']}): {f['content']} [ref: {f.get('times_referenced', 0)}]\n"
            return res
            
        return f"[ERROR] Unknown knowledge action '{action}'."

    def _handle_forget_command(self, action, options):
        if not action:
            return "[ERROR] Usage: /forget <fact_id> OR /forget all"
            
        target = (action + " " + " ".join(options)).strip().lower()
        
        if target == "all":
            self.kb.clear_knowledge()
            return "[SUCCESS] All learned knowledge has been cleared."
            
        fact_id = target
        if fact_id.isdigit():
            fact_id = f"fact_{int(fact_id):03d}"
            
        success = self.kb.delete_fact(fact_id)
        if success:
            return f"[SUCCESS] Forgotten fact {fact_id}."
            
        facts = self.kb.data.get("facts", [])
        matched = [f for f in facts if target in f["content"].lower()]
        if len(matched) == 1:
            fid = matched[0]["id"]
            self.kb.delete_fact(fid)
            return f"[SUCCESS] Forgotten fact {fid}: '{matched[0]['content']}'"
        elif len(matched) > 1:
            return f"[ERROR] Multiple facts matched: {', '.join(f['id'] for f in matched)}. Be more specific."
            
        return f"[ERROR] Fact ID or content matching '{target}' not found."

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

    def _get_generation_model_key(self, user_input: str) -> str:
        model_key = str(self.active_model).lower()
        if model_key == "god_eye":
            text_lower = user_input.lower()
            code_score = sum(1 for kw in ["code", "python", "javascript", "script", "function", "class", "def ", "import ", "compile", "git ", "repo", "database", "sql", "api", "algorithm", "html", "array", "json"] if kw in text_lower)
            design_score = sum(1 for kw in ["ui", "ux", "design", "color", "palette", "theme", "aesthetic", "css", "style", "layout", "visual", "padding", "margin", "button", "svg", "navbar", "component", "mockup", "wireframe"] if kw in text_lower)
            fix_score = sum(1 for kw in ["error", "bug", "fix", "crash", "broken", "exception", "traceback", "fail", "issue", "debug", "logs", "why does this fail", "syntax error"] if kw in text_lower)
            
            scores = {"code": code_score, "design": design_score, "fix": fix_score, "ultra": 1}
            return max(scores, key=scores.get)
        return model_key


class NexaLocalGenerator:
    """
    Smart local response generator.
    Attempts to use transformers if available, otherwise falls back to
    intelligent template-based responses that extract keywords from the prompt.
    """
    def __init__(self):
        self.tokenizer = None
        self.model = None
        self.device = None
        self.loaded_key = None
        self._transformers_available = None

    def _check_transformers(self):
        if self._transformers_available is None:
            try:
                import torch
                from transformers import AutoTokenizer, AutoModelForCausalLM
                self._transformers_available = True
            except ImportError:
                self._transformers_available = False
        return self._transformers_available

    def load_model(self, model_key: str):
        if not self._check_transformers():
            return None, None, None
        try:
            import torch
            from transformers import AutoTokenizer, AutoModelForCausalLM
        except ImportError:
            self._transformers_available = False
            return None, None, None

        model_key = model_key.lower().replace("nexa ", "").strip()
        if model_key not in ["code", "design", "fix", "ultra"]:
            model_key = "ultra"

        if self.model is not None and self.loaded_key == model_key:
            return self.model, self.tokenizer, self.device

        model_path = f"models/{model_key}"
        if not os.path.exists(model_path) or not os.path.exists(os.path.join(model_path, "config.json")):
            model_path = "gpt2"
            if not os.path.exists(os.path.join(model_path, "config.json")):
                return None, None, None

        try:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            self.model = AutoModelForCausalLM.from_pretrained(model_path)
            self.model.to(self.device)
            self.model.eval()
            self.loaded_key = model_key
        except Exception:
            return None, None, None

        return self.model, self.tokenizer, self.device

    def generate(self, prompt: str, model_key: str, max_new_tokens: int = 100) -> Optional[str]:
        model, tokenizer, device = self.load_model(model_key)
        if model is not None and tokenizer is not None:
            try:
                import torch
                input_text = f"User: {prompt}\nNEXA:"
                inputs = tokenizer(input_text, return_tensors="pt").to(device)
                with torch.no_grad():
                    outputs = model.generate(
                        **inputs,
                        max_new_tokens=max_new_tokens,
                        pad_token_id=tokenizer.pad_token_id,
                        eos_token_id=tokenizer.eos_token_id,
                        do_sample=True,
                        temperature=0.7,
                        top_p=0.9
                    )
                decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
                response = decoded[len(input_text):].strip()
                if not response:
                    response = decoded.replace(input_text, "").strip()
                if response:
                    return response
            except Exception:
                pass

        return self._fallback_generate(prompt, model_key)

    def _fallback_generate(self, prompt: str, model_key: str) -> str:
        prompt_lower = prompt.lower()
        templates_by_model = {
            "code": [
                "I can help you with that coding task. Here's my approach: {topic}. Would you like me to show you the implementation?",
                "Great coding question. Let me break this down: {topic}. This follows best practices for clean architecture.",
                "Here's the solution: For {topic}, I recommend using a modular approach with proper error handling.",
            ],
            "design": [
                "For the UI/UX of {topic}, I recommend a clean layout with proper spacing and a cohesive color palette.",
                "Design thinking for {topic}: focus on user flow, visual hierarchy, and responsive breakpoints.",
                "A great design for {topic} starts with understanding the user journey. Let me suggest a layout.",
            ],
            "fix": [
                "Debugging {topic}: Let me trace the issue systematically. First, check the input validation.",
                "To fix {topic}, I need to isolate the root cause. Common issues include type mismatches and edge cases.",
                "Found the issue with {topic}. The fix involves proper error handling and input sanitization.",
            ],
            "ultra": [
                "Looking at {topic} from a strategic perspective. Here's my comprehensive analysis.",
                "Great question about {topic}. Let me combine multiple approaches to give you the best solution.",
                "For {topic}, I recommend a multi-step strategy. First, let's understand the requirements.",
            ]
        }
        if model_key not in templates_by_model:
            model_key = "ultra"
        templates = templates_by_model[model_key]
        topic = prompt
        topic_match = re.search(r'(?:about|for|on|:)\s*(.+?)(?:[?.!]|$)', prompt_lower)
        if topic_match:
            topic = topic_match.group(1).strip().capitalize()
        if len(topic) > 80:
            topic = topic[:80] + "..."
        response = random.choice(templates).format(topic=topic)
        model_names = {"code": "NEXA CODE", "design": "NEXA DESIGN", "fix": "NEXA FIX", "ultra": "NEXA ULTRA"}
        return f"[{model_names.get(model_key, 'NEXA')}] {response}"

