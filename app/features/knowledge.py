# app/features/knowledge.py
import os
import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional

class NexaKnowledgeBase:
    def __init__(self, storage_dir: str = "user"):
        self.storage_dir = storage_dir
        self.knowledge_file = os.path.join(storage_dir, "knowledge.json")
        os.makedirs(storage_dir, exist_ok=True)
        self.data = self._load_data()

    def _load_data(self) -> Dict[str, Any]:
        if os.path.exists(self.knowledge_file):
            try:
                with open(self.knowledge_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "facts": [],
            "total_facts": 0,
            "topics": [],
            "last_updated": datetime.now().strftime("%Y-%m-%d")
        }

    def _save_data(self):
        self.data["total_facts"] = len(self.data["facts"])
        self.data["topics"] = list(set(fact["topic"] for fact in self.data["facts"] if "topic" in fact))
        self.data["last_updated"] = datetime.now().strftime("%Y-%m-%d")
        with open(self.knowledge_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def detect_topic(self, content: str) -> str:
        content_lower = content.lower()
        if any(w in content_lower for w in ["python", "js", "javascript", "code", "programming", "function", "variable", "class", "def "]):
            return "coding"
        if any(w in content_lower for w in ["css", "html", "design", "color", "palette", "layout", "border", "font", "ui", "ux"]):
            return "design"
        if any(w in content_lower for w in ["bug", "fix", "error", "traceback", "crash", "issue", "compile"]):
            return "debugging"
        if any(w in content_lower for w in ["math", "arithmetic", "equation", "sum", "multiply"]):
            return "math"
        return "general"

    def learn_fact(self, content: str, source: str = "user taught directly", topic: Optional[str] = None) -> Dict[str, Any]:
        fact_id = f"fact_{len(self.data['facts']) + 1:03d}"
        # Prevent duplicate IDs if facts were deleted
        existing_ids = {f["id"] for f in self.data["facts"]}
        idx = len(self.data["facts"]) + 1
        while f"fact_{idx:03d}" in existing_ids:
            idx += 1
        fact_id = f"fact_{idx:03d}"

        if not topic:
            topic = self.detect_topic(content)

        fact = {
            "id": fact_id,
            "content": content.strip(),
            "source": source,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "topic": topic,
            "times_referenced": 0
        }
        self.data["facts"].append(fact)
        self._save_data()
        return fact

    def learn_file(self, filepath: str) -> List[Dict[str, Any]]:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")

        _, ext = os.path.splitext(filepath.lower())
        content = ""

        # Extract text based on file type
        if ext in [".txt", ".md", ".csv", ".json", ".py", ".js", ".html", ".css"]:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        elif ext == ".pdf":
            # Basic fallback PDF extraction or try import pypdf/pdfplumber
            try:
                import pypdf
                reader = pypdf.PdfReader(filepath)
                content = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
            except Exception:
                # Mock or raw extract strings
                content = f"[PDF Parsing Fallback: {os.path.basename(filepath)} content]"
        elif ext in [".docx", ".doc"]:
            try:
                import docx
                doc = docx.Document(filepath)
                content = "\n".join([p.text for p in doc.paragraphs])
            except Exception:
                content = f"[DOCX Parsing Fallback: {os.path.basename(filepath)} content]"
        else:
            raise ValueError(f"Unsupported file format for learning: {ext}")

        # Split content into distinct sentences/facts
        # Simple splitting by sentences or newlines
        sentences = re.split(r'(?<=[.!?])\s+', content)
        learned_facts = []
        for sent in sentences:
            sent_clean = sent.strip()
            if len(sent_clean) > 10 and not sent_clean.startswith("[") and not sent_clean.endswith("]"):
                fact = self.learn_fact(sent_clean, source=f"file: {os.path.basename(filepath)}")
                learned_facts.append(fact)

        return learned_facts

    def search_facts(self, query: str) -> List[Dict[str, Any]]:
        query_words = set(re.findall(r'\w+', query.lower()))
        if not query_words:
            return []

        results = []
        for fact in self.data["facts"]:
            fact_words = set(re.findall(r'\w+', fact["content"].lower()))
            overlap = query_words.intersection(fact_words)
            if overlap:
                score = len(overlap) / len(query_words)
                results.append((score, fact))

        # Sort by overlap score descending
        results.sort(key=lambda x: x[0], reverse=True)
        matched_facts = []
        for score, fact in results:
            if score >= 0.2:  # Threshold
                fact["times_referenced"] += 1
                matched_facts.append(fact)
        
        if matched_facts:
            self._save_data()
            
        return matched_facts

    def delete_fact(self, fact_id: str) -> bool:
        initial_len = len(self.data["facts"])
        self.data["facts"] = [f for f in self.data["facts"] if f["id"] != fact_id]
        if len(self.data["facts"]) < initial_len:
            self._save_data()
            return True
        return False

    def clear_knowledge(self):
        self.data = {
            "facts": [],
            "total_facts": 0,
            "topics": [],
            "last_updated": datetime.now().strftime("%Y-%m-%d")
        }
        self._save_data()

    def export_knowledge(self, filepath: str) -> str:
        with open(filepath, "w", encoding="utf-8") as f:
            for fact in self.data["facts"]:
                f.write(f"[{fact['id']}] ({fact['topic']}): {fact['content']}\n")
        return filepath

    def import_knowledge(self, filepath: str) -> int:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")

        imported_count = 0
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                # Match format: [ID] (topic): content
                match = re.match(r'^\[fact_\d+\]\s*\(([^)]+)\):\s*(.+)$', line.strip())
                if match:
                    topic, content = match.groups()
                    self.learn_fact(content, source="imported file", topic=topic)
                    imported_count += 1
                else:
                    # Raw lines can be learned as plain text
                    line_clean = line.strip()
                    if len(line_clean) > 10:
                        self.learn_fact(line_clean, source="imported file")
                        imported_count += 1
        return imported_count

    def get_stats(self) -> Dict[str, Any]:
        if not self.data["facts"]:
            return {
                "total_facts": 0,
                "topics": [],
                "most_referenced": "None"
            }
        
        # Most referenced
        sorted_by_ref = sorted(self.data["facts"], key=lambda x: x.get("times_referenced", 0), reverse=True)
        most_ref = sorted_by_ref[0] if sorted_by_ref else None
        most_ref_str = f"{most_ref['id']} ({most_ref['times_referenced']} times)" if most_ref else "None"

        return {
            "total_facts": len(self.data["facts"]),
            "topics": self.data["topics"],
            "most_referenced": most_ref_str
        }
