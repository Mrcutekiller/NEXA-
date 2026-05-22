# app/features/translate.py
import re
from typing import Dict, List, Any

class NexaTranslator:
    def __init__(self):
        # Offline vocabulary dictionary
        self.vocab = {
            "french": {
                "hello": "bonjour", "how are you": "comment allez-vous", "goodbye": "au revoir",
                "thank you": "merci", "welcome": "bienvenue", "yes": "oui", "no": "non",
                "python is a programming language": "Python est un langage de programmation"
            },
            "spanish": {
                "hello": "hola", "how are you": "cómo estás", "goodbye": "adiós",
                "thank you": "gracias", "welcome": "bienvenido", "yes": "sí", "no": "no",
                "python is a programming language": "Python es un lenguaje de programación"
            },
            "german": {
                "hello": "hallo", "how are you": "wie geht es dir", "goodbye": "auf wiedersehen",
                "thank you": "danke", "welcome": "willkommen", "yes": "ja", "no": "nein",
                "python is a programming language": "Python ist eine Programmiersprache"
            }
        }

    def translate_text(self, text: str, target_lang: str) -> str:
        target_lower = target_lang.lower().strip()
        text_lower = text.lower().strip().strip('"').strip("'")
        
        lang_dict = self.vocab.get(target_lower)
        if not lang_dict:
            return f"I don't have offline vocabulary for '{target_lang}' yet. Teach me vocabulary using /learn."

        # Direct phrase lookup
        if text_lower in lang_dict:
            return lang_dict[text_lower]

        # Word-by-word fallback
        words = re.findall(r'\w+', text_lower)
        translated_words = []
        for w in words:
            translated_words.append(lang_dict.get(w, w))
        
        return " ".join(translated_words).capitalize()

    def convert_code(self, code: str, source_lang: str, target_lang: str) -> str:
        src = source_lang.lower().strip()
        tgt = target_lang.lower().strip()
        
        if src == "python" and tgt == "javascript":
            # Simple conversion rule simulations
            js_code = code
            # replace def func_name(args): with function func_name(args) {
            js_code = re.sub(r'def\s+(\w+)\(([^)]*)\):', r'function \1(\2) {', js_code)
            # replace print(...) with console.log(...)
            js_code = re.sub(r'print\((.*)\)', r'console.log(\1)', js_code)
            # replace None with null
            js_code = js_code.replace("None", "null")
            js_code = js_code.replace("True", "true")
            js_code = js_code.replace("False", "false")
            
            # Simple indentation closed brackets
            lines = js_code.splitlines()
            formatted_lines = []
            indent_stack = [0]
            
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    formatted_lines.append(line)
                    continue
                
                current_indent = len(line) - len(line.lstrip())
                while indent_stack[-1] > current_indent:
                    indent_stack.pop()
                    formatted_lines.append(" " * indent_stack[-1] + "}")
                
                if "{" in line:
                    indent_stack.append(current_indent + 4)
                
                formatted_lines.append(line)
                
            while len(indent_stack) > 1:
                indent_stack.pop()
                formatted_lines.append(" " * indent_stack[-1] + "}")
                
            js_out = "\n".join(formatted_lines)
            notes = """
Nexa Conversion Notes:
1. Python is indentation-based; JS uses curly braces. Added appropriate braces.
2. console.log is the equivalent to Python's print function.
3. Python's None maps to JS's null.
"""
            return f"```javascript\n{js_out}\n```\n{notes}"
            
        return f"Code conversion from '{source_lang}' to '{target_lang}' is supported for Python -> JS. Teach me patterns for other languages."

    def change_complexity(self, text: str, level: str) -> str:
        lvl = level.lower().strip()
        # Clean text
        text_clean = re.sub(r'\[[A-Z]+\]\s*', '', text)
        
        if lvl == "eli5":
            return f"👶 [ELI5]: Think of it like a toy box. {text_clean.split('.')[0]}. If you put a toy inside, it stays there until you take it out. That's how it stores things!"
        elif lvl == "simplify":
            return f"💡 [SIMPLE]: Basically, {text_clean.split('.')[0]}. It lets you read, write, and execute items in simple steps without needing complex setups."
        elif lvl == "complexify":
            return f"🔬 [ACADEMIC]: Leveraging advanced modular structures, the subject system implements '{text_clean}' via low-level abstraction matrices, optimizing CPU thread scheduling and memory pointer allocations."
        elif lvl == "eli-expert":
            return f"🎓 [PHD]: Architecturally speaking, the mechanism functions as a distributed non-blocking state machine, yielding high transactional throughput and deterministic memory bound guarantees. \nDetail: {text_clean}"
        return text
