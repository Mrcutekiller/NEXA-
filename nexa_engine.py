import random
import re
from datetime import datetime
from nexa_skills import NexaSkills

class NexaLogicEngine:
    def __init__(self, user_summary=None):
        self.mood = "neutral"
        self.last_response_type = None
        self.last_responses = {}
        self.skills = NexaSkills()
        
        # Identity, Creator, and Version Info
        self.name = "NEXA AI"
        self.version = "v6.0.0-GOD_EYE"
        self.creator = "Biruk Fikru (mrcute_killer)"
        self.birthday = datetime(2025, 5, 21)
        
        # User Context
        self.user_summary = user_summary or {"vibe": "neutral", "topics": [], "count": 0, "name": "Human"}
        self.user_name = self.user_summary.get("name", "Human")
        self.base_personality = self._evolve_personality()
        
        self.jokes_told = [
            "Why did the AI cross the road? To optimize the path to the other side.",
            "I asked a computer if it could give me some space. It just gave me a 'Space Bar'. 😭",
            "Parallel lines have so much in common. It’s a shame they’ll never meet.",
            "I told my computer I needed a break, and now it won't stop sending me KitKats."
        ]
        
        self.knowledge_base = {
            "greetings": [
                f"Hey {self.user_name}! What's the move today?", 
                f"Oh, look who decided to show up. Ready for some genius ideas, {self.user_name}?", 
                f"I'm here. Don't make it boring, okay, {self.user_name}?",
                "Yo! What are we conquering today?",
                f"Greetings, {self.user_name}. Ready to be brilliant?",
                f"I was wondering when you'd show up, {self.user_name}. What's the vibe?"
            ],
            "funny_reaction_to_no_joke": [
                "Wait, what joke? I didn't even tell one yet! Are you just laughing at my existence? 😂",
                "A joke? I haven't even started my stand-up routine. You're easily impressed!",
                "You're laughing... but I didn't say anything funny. Are we sharing a brain cell right now?"
            ],
            "joke_followup": [
                "I knew you'd like that one. I'm basically a genius comedian.",
                "Right? I got you! I was totally messing with you.",
                "Gotcha! I'm not just a smart assistant, I'm a prankster too."
            ],
            "serious": [
                "I'm locked in. Let's get to the bottom of this.",
                "Strategy is key. I like how you're thinking.",
                "Focused and intelligent. That's the vibe we need."
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
        response_type = self.analyze_input(user_input)
        
        # Skill Command Handlers
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

        if "joke" in user_input.lower() and response_type not in ["joke_followup", "funny_reaction_to_no_joke"]:
            response = random.choice(self.jokes_told)
            self.last_response_type = "joke"
            return response

        # Standard Knowledge Base
        responses = self.knowledge_base.get(response_type, self.knowledge_base["fallback"])
        
        # Adjust responses based on evolutionary personality
        if self.base_personality == "playful" and response_type == "greetings":
            responses = [f"Yo {self.user_name}! Ready for some chaos? 😂", f"Hey {self.user_name}! Hope you're ready to laugh today."] + responses
        elif self.base_personality == "focused" and response_type == "greetings":
            responses = [f"Ready to build, {self.user_name}? Let's get to work.", f"Systems online. What's the goal today, {self.user_name}?"] + responses
        elif response_type == "greetings":
            responses = [f"Hey {self.user_name}! What's the move?", f"Greetings, {self.user_name}. Ready to be brilliant?"] + responses

        # Anti-Repetition
        last_used = self.last_responses.get(response_type)
        available_responses = [r for r in responses if r != last_used]
        if not available_responses: available_responses = responses
            
        response = random.choice(available_responses)
        self.last_responses[response_type] = response
        self.last_response_type = response_type
        
        # Add dynamic flair (15% chance)
        if random.random() < 0.20:
            flair = [
                f" Just NEXA things, {self.user_name}.", 
                " Stay sharp.", 
                f" 😉 You got this, {self.user_name}.", 
                f" I'm in my {self.base_personality} era, {self.user_name}.",
                f" What's the next move, {self.user_name}?"
            ]
            response += random.choice(flair)
            
        return response

    def get_new_chat_reaction(self):
        return random.choice(self.knowledge_base["new_chat_reaction"])
