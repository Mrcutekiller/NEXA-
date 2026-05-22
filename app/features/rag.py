# app/features/rag.py
import os
import re
from typing import Dict, List, Tuple, Any

class NexaRAG:
    def __init__(self):
        self.session_docs: Dict[str, List[str]] = {}    # filename -> text chunks
        self.index: Dict[str, List[Tuple[str, int]]] = {} # keyword -> list of (filename, chunk_index)

    def chunk_text(self, text: str, chunk_size: int = 500) -> List[str]:
        words = text.split()
        chunks = []
        current_chunk = []
        current_len = 0
        for w in words:
            current_chunk.append(w)
            current_len += len(w) + 1
            if current_len >= chunk_size:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_len = 0
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        return chunks

    def load_document(self, filepath: str) -> str:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")

        filename = os.path.basename(filepath)
        _, ext = os.path.splitext(filename.lower())
        content = ""

        # Extract text based on file format
        if ext in [".txt", ".md", ".csv", ".json", ".py", ".js", ".html", ".css"]:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        elif ext == ".pdf":
            try:
                import pypdf
                reader = pypdf.PdfReader(filepath)
                content = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
            except Exception:
                content = f"[Temporary RAG PDF extraction: {filename}]"
        elif ext in [".docx", ".doc"]:
            try:
                import docx
                doc = docx.Document(filepath)
                content = "\n".join([p.text for p in doc.paragraphs])
            except Exception:
                content = f"[Temporary RAG DOCX extraction: {filename}]"
        else:
            raise ValueError(f"Unsupported file format for RAG: {ext}")

        chunks = self.chunk_text(content)
        self.session_docs[filename] = chunks
        self._index_keywords(filename, chunks)
        
        return f"Loaded '{filename}' into session memory. Segmented into {len(chunks)} chunks."

    def _index_keywords(self, filename: str, chunks: List[str]):
        for idx, chunk in enumerate(chunks):
            words = set(re.findall(r'\w+', chunk.lower()))
            for w in words:
                if len(w) > 3:  # ignore short stop words
                    self.index.setdefault(w, []).append((filename, idx))

    def search(self, query: str, top_k: int = 3) -> List[Tuple[str, str]]:
        query_words = set(re.findall(r'\w+', query.lower()))
        scores: Dict[Tuple[str, int], int] = {} # (filename, chunk_idx) -> score
        
        for w in query_words:
            if w in self.index:
                for filename, idx in self.index[w]:
                    scores[(filename, idx)] = scores.get((filename, idx), 0) + 1

        # Sort matches by score descending
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        results = []
        for ((filename, idx), score) in sorted_scores[:top_k]:
            chunk = self.session_docs[filename][idx]
            results.append((filename, chunk))
            
        return results

    def answer_with_context(self, query: str) -> str:
        relevant = self.search(query)
        if not relevant:
            return ""
            
        context_blocks = []
        for filename, chunk in relevant:
            context_blocks.append(f"--- Context from {filename} ---\n{chunk}")
            
        return "\n\n".join(context_blocks)

    def list_loaded_documents(self) -> List[str]:
        return [f"{k} ({len(v)} chunks)" for k, v in self.session_docs.items()]

    def forget_document(self, filename: str) -> bool:
        if filename in self.session_docs:
            del self.session_docs[filename]
            # Rebuild index
            self.index.clear()
            for fn, chunks in self.session_docs.items():
                self._index_keywords(fn, chunks)
            return True
        return False

    def clear_memory(self):
        self.session_docs.clear()
        self.index.clear()
