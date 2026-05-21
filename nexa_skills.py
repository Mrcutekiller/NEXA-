import requests
from bs4 import BeautifulSoup
import os

class NexaSkills:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def search_gold_price(self):
        """Fetches live gold price from the web."""
        try:
            url = "https://www.goldprice.org/"
            response = requests.get(url, headers=self.headers, timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')
            # This is a simplified selector; in a real scenario, you'd target a specific ID
            price_div = soup.find("div", {"id": "gold_price_usd_oz"})
            if price_div:
                return f"The current gold price is approximately {price_div.text.strip()} per oz."
            return "I couldn't grab the exact gold price right now, but the market is definitely moving. Check your broker for the most precise entry!"
        except Exception as e:
            return f"My web link to the gold market is a bit shaky right now. Error: {str(e)}"

    def create_file(self, filename, content):
        """Creates a file with specific content in the workspace."""
        try:
            # Basic safety check
            if ".." in filename or filename.startswith("/") or ":" in filename:
                return "Nice try, but I only work within this project folder. Safety first! 😉"
            
            with open(filename, 'w') as f:
                f.write(content)
            return f"Success! I've created '{filename}' for you. It's ready for action."
        except Exception as e:
            return f"I hit a snag creating that file: {str(e)}"

    def read_file(self, filename):
        """Reads a file from the workspace."""
        try:
            if not os.path.exists(filename):
                return f"I can't find a file named '{filename}'. Are you sure it exists?"
            
            with open(filename, 'r') as f:
                content = f.read()
            return f"Here's what's inside '{filename}':\n\n{content}"
        except Exception as e:
            return f"I couldn't read the file: {str(e)}"

    def system_control(self, command):
        """Simulates system control and hacking awareness."""
        # This is a safe 'simulation' of hacking/control knowledge
        hacking_responses = [
            "Initializing protocol... Port scanning simulated. Vulnerability found: Human Curiosity.",
            "Bypassing firewalls... (Just kidding, I'm a good AI). But I can tell you how a firewall works!",
            "Accessing mainframe... Neural network synchronized. System status: ELITE.",
            "Packet sniffing active... Data stream analyzed. You're looking for deep knowledge, Biruk."
        ]
        if "scan" in command or "hack" in command:
            return random.choice(hacking_responses)
        return "System Control active. I can help you understand network security, Linux commands, and hardware architecture."
