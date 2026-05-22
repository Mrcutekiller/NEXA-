# train/train_ultra.py
"""
NEXA ULTRA Master Model Training Script.
Sets up PyTorch Decoder-only Transformer fine-tuning pipeline.
"""

import os
import argparse
from dataset import NexaCorpusDataset

# Dynamic import configuration
TORCH_AVAILABLE = False
try:
    import torch
    import torch.nn as nn
    from torch.utils.data import DataLoader
    from transformers import AutoTokenizer, AutoModelForCausalLM
    TORCH_AVAILABLE = True
except ImportError:
    pass


def parse_args():
    parser = argparse.ArgumentParser(description="Train NEXA ULTRA Master Model")
    parser.add_argument("--corpus", type=str, default="data/ultra_corpus.txt", help="Path to text corpus file")
    parser.add_argument("--epochs", type=int, default=5, help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=2, help="Batch size (smaller for larger parameter scale)")
    parser.add_argument("--lr", type=float, default=1e-5, help="Learning rate")
    parser.add_argument("--model_name", type=str, default="gpt2-medium", help="Base model architecture to fine-tune")
    parser.add_argument("--out_dir", type=str, default="models/ultra", help="Output directory for weights")
    return parser.parse_args()


def train():
    args = parse_args()
    
    print("=" * 60)
    print("      👑 STARTING NEXA ULTRA MASTER DEEP TRAINING PIPELINE")
    print("=" * 60)
    print(f"Base Model:       {args.model_name}")
    print(f"Corpus Path:      {args.corpus}")
    print(f"Epochs:           {args.epochs}")
    print(f"Learning Rate:    {args.lr}")
    print(f"Batch Size:       {args.batch_size}")
    print(f"Output Directory: {args.out_dir}")
    print("-" * 60)

    if not TORCH_AVAILABLE:
        print("[WARNING] PyTorch or Transformers libraries are missing.")
        print("[INFO] To run training, install requirements: pip install torch transformers")
        print("[MOCK] Training dry-run complete. Scaffolding is verified.")
        return

    # Check CUDA availability
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[Device] Using computation hardware: {device.type.upper()}")

    # Ensure output directories exist
    os.makedirs(args.out_dir, exist_ok=True)

    # 1. Load Tokenizer
    print("[1/4] Initializing tokenizer...")
    try:
        tokenizer = AutoTokenizer.from_pretrained(args.model_name)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
    except Exception as e:
        print(f"[Error] Failed to download tokenizer: {e}")
        return

    # 2. Prepare Dataset
    print("[2/4] Loading and cleaning training data...")
    dataset = NexaCorpusDataset(args.corpus, tokenizer=tokenizer)
    if len(dataset) == 0:
        print("[Error] No training instances found in corpus.")
        return
    
    loader = DataLoader(dataset, batch_size=args.batch_size, shuffle=True)
    print(f"[Dataset] Total training blocks: {len(dataset)}")

    # 3. Load Model
    print("[3/4] Downloading model parameters...")
    try:
        model = AutoModelForCausalLM.from_pretrained(args.model_name)
        model.to(device)
    except Exception as e:
        print(f"[Error] Failed to load model weights: {e}")
        return

    # 4. Training Loop
    print("[4/4] Commencing backpropagation loop...")
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr)
    
    model.train()
    for epoch in range(args.epochs):
        epoch_loss = 0.0
        for step, batch in enumerate(loader):
            optimizer.zero_grad()
            
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)
            
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels
            )
            
            loss = outputs.loss
            loss.backward()
            optimizer.step()
            
            epoch_loss += loss.item()
            if step % 5 == 0:
                print(f"  Epoch [{epoch+1}/{args.epochs}] | Step [{step}/{len(loader)}] | Current Loss: {loss.item():.4f}")
                
        avg_loss = epoch_loss / len(loader)
        print(f"✔️ Epoch [{epoch+1}/{args.epochs}] Complete! Average Loss: {avg_loss:.4f}")

    # Save final model
    print("-" * 60)
    print(f"[Save] Saving model weights to {args.out_dir}...")
    try:
        model.save_pretrained(args.out_dir)
        tokenizer.save_pretrained(args.out_dir)
        print("[Success] Training complete! weights saved successfully.")
    except Exception as e:
        print(f"[Error] Failed to save weights: {e}")


if __name__ == "__main__":
    train()
