# train/dataset.py
"""
Dataset loader and text cleaning preprocessing pipeline for training NEXA v3 models.
Supports loading text datasets and tokenizing text buffers.
"""

import os
import re
from typing import List, Tuple

# Try importing torch/transformers, fallback gracefully if absent
TORCH_AVAILABLE = False
try:
    import torch
    from torch.utils.data import Dataset
    TORCH_AVAILABLE = True
except ImportError:
    class Dataset:
        pass


class NexaCorpusDataset(Dataset):
    """
    Loads text corpus files and tokenizes them for transformer decoder training.
    """
    def __init__(self, corpus_path: str, tokenizer=None, max_length: int = 512):
        self.corpus_path = corpus_path
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.texts: List[str] = []
        self._load_corpus()

    def _load_corpus(self):
        if not os.path.exists(self.corpus_path):
            # Create a mock/empty corpus if file doesn't exist
            os.makedirs(os.path.dirname(self.corpus_path) or ".", exist_ok=True)
            with open(self.corpus_path, "w") as f:
                f.write("Sample training data for NEXA AI model training.\n")
            print(f"[Dataset] Created default empty corpus file at: {self.corpus_path}")

        try:
            with open(self.corpus_path, "r", encoding="utf-8") as f:
                content = f.read()
                # Split by double newline to separate training examples
                self.texts = [chunk.strip() for chunk in content.split("\n\n") if chunk.strip()]
        except Exception as e:
            print(f"[Dataset] Load Error: {e}")
            self.texts = ["Fallback training instance for NEXA pipeline."]

    def __len__(self) -> int:
        return len(self.texts)

    def __getitem__(self, idx: int) -> Any:
        text = self.texts[idx]
        
        # Clean text
        text = self.clean_text(text)
        
        if not TORCH_AVAILABLE or not self.tokenizer:
            # Mock tokenization
            return {"text": text}

        # Tokenize
        encoding = self.tokenizer(
            text,
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        
        # Decoder-only transformer expects input_ids and labels (shifted right)
        input_ids = encoding["input_ids"].squeeze(0)
        attention_mask = encoding["attention_mask"].squeeze(0)
        
        # Labels are same as input_ids for self-supervised training
        labels = input_ids.clone()
        # Set padding tokens to -100 to ignore in PyTorch cross-entropy loss calculation
        if self.tokenizer.pad_token_id is not None:
            labels[labels == self.tokenizer.pad_token_id] = -100
            
        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "labels": labels
        }

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Strips non-printable chars or control structures.
        """
        # Remove multiple spaces
        text = re.sub(r"[ \t]+", " ", text)
        # Retain standard formatting
        return text.strip()
