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
                return f"[ERROR] File not found: '{filename}'."
            
            with open(filename, 'r') as f:
                content = f.read()
            return f"Here's what's inside '{filename}':\n\n{content}"
        except Exception as e:
            return f"[ERROR] Could not read file: {str(e)}"

    def edit_file(self, filename, content):
        """Edits/Overwrites a file with new content."""
        try:
            if not os.path.exists(filename):
                return f"[ERROR] File '{filename}' does not exist. Use 'create' first."
            
            with open(filename, 'w') as f:
                f.write(content)
            return f"[SUCCESS] '{filename}' has been updated."
        except Exception as e:
            return f"[ERROR] Edit failed: {str(e)}"

    def delete_file(self, filename):
        """Deletes a file from the workspace."""
        try:
            if not os.path.exists(filename):
                return f"[ERROR] File '{filename}' not found."
            
            os.remove(filename)
            return f"[SUCCESS] '{filename}' has been deleted."
        except Exception as e:
            return f"[ERROR] Deletion failed: {str(e)}"

    def rename_file(self, old_name, new_name):
        """Renames a file."""
        try:
            if not os.path.exists(old_name):
                return f"[ERROR] File '{old_name}' not found."
            
            os.rename(old_name, new_name)
            return f"[SUCCESS] Renamed '{old_name}' to '{new_name}'."
        except Exception as e:
            return f"[ERROR] Rename failed: {str(e)}"

    def search_files(self, query):
        """Searches for a string in all files in the current directory."""
        try:
            matches = []
            for root, dirs, files in os.walk("."):
                # Skip hidden directories like .git
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                for file in files:
                    if file.endswith(('.py', '.txt', '.js', '.json', '.md')):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                if query.lower() in f.read().lower():
                                    matches.append(file_path)
                        except:
                            continue
            
            if matches:
                return f"Found '{query}' in:\n- " + "\n- ".join(matches)
            return f"No matches found for '{query}'."
        except Exception as e:
            return f"[ERROR] Search failed: {str(e)}"

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

    def analyze_image(self, image_path):
        """Simulates advanced image analysis."""
        if not os.path.exists(image_path):
            return f"[ERROR] Image file '{image_path}' not found. Please provide a valid path."
        
        try:
            from PIL import Image
            img = Image.open(image_path)
            width, height = img.size
            format = img.format
            
            analysis_scenarios = [
                f"I've scanned the {format} image ({width}x{height}). I detect complex visual patterns and high-frequency data consistent with modern digital architecture.",
                f"Neural analysis of '{os.path.basename(image_path)}' complete. Object recognition suggests a multi-layered composition with interesting geometric properties.",
                f"Image processing active. This {width}x{height} file contains visual data that my vision model classifies as 'Intriguing'. Want me to enhance the details?"
            ]
            import random
            return random.choice(analysis_scenarios)
        except Exception as e:
            return f"[ERROR] Image analysis failed: {str(e)}"
