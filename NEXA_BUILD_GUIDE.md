# NEXA AI — Complete Build, Training & Feature Guide

> Comprehensive reference for training, extending, and deploying the NEXA AI system.
> Give relevant sections to an AI assistant with the instruction:
> *"Improve Nexa based on this guide, focus on [specific area]"*

---

## 1. What Nexa Is

Nexa is a locally trained AI assistant that:

- Runs **entirely on the user's machine** (no internet required after training)
- Is trained from scratch using a **Transformer architecture**
- Responds to natural language questions and commands
- Has a **terminal-based UI** with a full chat interface
- Supports **slash (`/`) commands** for special actions
- Saves chat history and user profiles **locally**

---

## 2. Architecture — How Nexa's Brain Works

### Model Type
```
Decoder-only Transformer (same family as GPT)
```

### Message Processing Pipeline
```
User types message
        ↓
Tokenizer splits text into tokens (word pieces)
        ↓
Tokens converted to numbers (token IDs)
        ↓
Numbers become vectors (embeddings)
        ↓
Vectors pass through N Transformer layers
   Each layer has:
   - Multi-head self-attention (understands context)
   - Feed-forward network (processes meaning)
   - Layer normalization (stabilizes training)
        ↓
Final layer outputs probability scores for next token
        ↓
Highest probability token selected (or sampled)
        ↓
Repeat until end-of-sequence token or max length
        ↓
Tokens decoded back to text
        ↓
Response shown to user
```

### Recommended Starter Configuration
```python
config = {
    "vocab_size":  32000,   # number of unique tokens
    "max_seq_len": 512,     # max tokens per message
    "embed_dim":   256,     # size of token embeddings
    "num_layers":  6,       # transformer blocks
    "num_heads":   8,       # attention heads per layer
    "ff_dim":      1024,    # feed-forward hidden size
    "dropout":     0.1,     # regularization
}
# Total parameters: ~10–50 million (good starting point)
```

---

## 3. Tokenizer — How Nexa Reads Text

### What It Does
Splits text like:
```
"Hello world" → ["Hello", " world"] → [4321, 1234]
```

### Best Tokenizer Type: BPE (Byte Pair Encoding)

### How to Train It
```python
from tokenizers import ByteLevelBPETokenizer

tokenizer = ByteLevelBPETokenizer()
tokenizer.train(
    files=["data/wikipedia.txt", "data/conversations.txt"],
    vocab_size=32000,
    min_frequency=2,
    special_tokens=["<pad>", "<eos>", "<bos>", "<unk>", "<sep>"]
)
tokenizer.save_model("nexa_tokenizer/")
```

### Special Tokens Nexa Needs
| Token | Meaning |
|---|---|
| `<bos>` | Beginning of sequence |
| `<eos>` | End of sequence — stop generating here |
| `<pad>` | Padding — fill empty space in batches |
| `<unk>` | Unknown token — word not in vocabulary |
| `<sep>` | Separator between user and AI turns |
| `<sys>` | System / personality prompt start |
| `<usr>` | User message start |
| `<ast>` | Assistant (Nexa) response start |

---

## 4. Training Data — What to Feed Nexa

### Phase 1 Data (General Knowledge — Pre-training)
| Dataset | What It Teaches | Where to Get It | Size |
|---|---|---|---|
| Wikipedia dump | Facts, concepts, history | dumps.wikimedia.org | 20 GB |
| OpenWebText | Natural language, writing | github.com/jcpeterson/openwebtext | 38 GB |
| BookCorpus | Long reasoning, storytelling | huggingface.co/datasets/bookcorpus | 4 GB |
| CC-News | Current events style | huggingface.co/datasets/cc_news | 70 GB |
| ArXiv papers | Science and math | huggingface.co/datasets/arxiv | 50 GB |

### Phase 2 Data (Instruction Following — Fine-tuning)
| Dataset | What It Teaches | Size |
|---|---|---|
| Alpaca | Follow instructions | 52 k examples |
| Dolly-15k | High quality Q&A | 15 k examples |
| OpenAssistant | Real conversations | 160 k examples |
| FLAN | Reasoning tasks | Large |
| ShareGPT | ChatGPT-style dialogue | 90 k examples |

### Training Data Format for Chat
```
<sys>You are Nexa, a helpful local AI assistant.<sep>
<usr>What is machine learning?<sep>
<ast>Machine learning is a field of AI where computers learn from data
without being explicitly programmed. Instead of writing rules manually,
the model finds patterns in examples and improves over time.<eos>
```

### Data Cleaning Steps (IMPORTANT — do before every training run)
```python
1. Remove duplicate text
2. Remove text shorter than 50 characters
3. Remove non-UTF-8 characters
4. Remove HTML tags and URLs (for chat data)
5. Filter out low-quality text (too many symbols)
6. Shuffle the dataset randomly
7. Split into train (90%) / validation (5%) / test (5%)
```

---

## 5. Training — How to Actually Train Nexa

### Setup
```bash
pip install torch transformers datasets tokenizers accelerate sentencepiece
```

### Training Script Structure
```python
import torch
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR

# Hyperparameters
LEARNING_RATE = 3e-4    # start here, reduce if unstable
BATCH_SIZE    = 16      # reduce if GPU runs out of memory
MAX_EPOCHS    = 3       # for fine-tuning; pre-training = more
WARMUP_STEPS  = 1000    # gradually increase LR at start
GRAD_CLIP     = 1.0     # prevents exploding gradients
WEIGHT_DECAY  = 0.01    # regularization

# Training loop (simplified)
for epoch in range(MAX_EPOCHS):
    for batch in dataloader:
        optimizer.zero_grad()

        input_ids = batch["input_ids"]
        labels    = batch["labels"]       # same as input, shifted by 1

        outputs = model(input_ids)
        loss    = cross_entropy(outputs, labels)   # next-token prediction

        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), GRAD_CLIP)
        optimizer.step()
        scheduler.step()

        if step % 100 == 0:
            print(f"Step {step} | Loss: {loss.item():.4f}")
```

### Training Phases (in order)
```
PHASE 1 — PRE-TRAINING (weeks)
  Goal:        Learn language and general knowledge
  Data:        Wikipedia + OpenWebText + Books
  Loss target: below 2.5

PHASE 2 — INSTRUCTION FINE-TUNING (days)
  Goal:        Learn to follow instructions and answer questions
  Data:        Alpaca + Dolly + OpenAssistant
  Loss target: below 1.5

PHASE 3 — RLHF (optional, days/weeks)
  Goal:        Make responses feel natural and helpful
  Method:      Rate responses → train reward model → PPO
```

### Signs Training Is Going Well ✓
- Loss decreasing steadily
- Validation loss close to training loss
- Responses getting more coherent over time
- No "mode collapse" (repeating the same words)

### Signs of Problems ✗
| Symptom | Fix |
|---|---|
| Loss not decreasing | Lower the learning rate |
| Loss goes to NaN | Lower learning rate; check data |
| Repeating output | Increase temperature; check data diversity |
| Out of memory | Reduce batch size or sequence length |

---

## 6. Inference — How Nexa Generates Responses

### Generation Settings
```python
def generate(prompt, model, tokenizer):
    inputs = tokenizer.encode(prompt, return_tensors="pt")

    output = model.generate(
        inputs,
        max_new_tokens=512,      # max response length
        temperature=0.7,          # 0=deterministic, 1=creative, 2=chaotic
        top_p=0.9,                # nucleus sampling (quality filter)
        top_k=50,                 # sample from top 50 tokens only
        repetition_penalty=1.2,   # punish repeating words
        do_sample=True,           # enable sampling (not greedy)
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.pad_token_id,
    )

    return tokenizer.decode(output[0], skip_special_tokens=True)
```

### Prompt Format for Inference
```python
def build_prompt(user_message, history=[], system_prompt=""):
    prompt = f"<sys>{system_prompt}<sep>"
    for turn in history:
        prompt += f"<usr>{turn['user']}<sep><ast>{turn['nexa']}<eos>"
    prompt += f"<usr>{user_message}<sep><ast>"
    return prompt
```

---

## 7. Slash Commands — Full List

All commands are handled by the application layer, not the AI model itself.

### Core Commands
| Command | Action |
|---|---|
| `/help` | Show all available commands |
| `/clear` | Clear current chat screen |
| `/reset` | Clear chat and reset conversation history |
| `/exit` or `/quit` | Exit Nexa |
| `/new` | Start a brand new conversation |

### Mode Commands
| Command | Action |
|---|---|
| `/mode default` | Normal chat mode |
| `/mode code` | Code-focused mode (more technical responses) |
| `/mode math` | Math mode (step-by-step solutions) |
| `/mode write` | Writing assistant mode |
| `/mode research` | Deep research and analysis mode |
| `/mode fast` | Short, quick answers only |

### History Commands
| Command | Action |
|---|---|
| `/history` | Show last 10 conversations |
| `/history 20` | Show last 20 conversations |
| `/save [name]` | Save current chat with a name |
| `/load [name]` | Load a saved conversation |
| `/delete [name]` | Delete a saved conversation |
| `/export` | Export chat to `.txt` file |

### Settings Commands
| Command | Action |
|---|---|
| `/settings` | Show current settings |
| `/set temperature 0.7` | Change response creativity (0.1–1.5) |
| `/set length short` | Response length: short / medium / long |
| `/set language english` | Set response language |
| `/set name [name]` | Change display name |
| `/theme dark` | Switch to dark theme |
| `/theme light` | Switch to light theme |
| `/theme high-contrast` | Switch to high-contrast (WCAG AA) theme |

### Model Commands
| Command | Action |
|---|---|
| `/model info` | Show model size and training info |
| `/model stats` | Show response time and token usage |
| `/reload` | Reload the model from disk |

### Terminal Workspace Commands (v9.0+)
| Command | Action |
|---|---|
| `/tab new <label>` | Create a new workspace tab |
| `/tab swap <a> <b>` | Swap two tabs by index |
| `/tab pin [ref]` | Pin/unpin a tab to prevent accidental close |
| `/pane split vertical` | Split current pane vertically |
| `/pane resize <pct>` | Resize active pane (10–90%) |
| `/search --regex <p>` | Regex search in pane output |
| `/search --fixed <t> --context 2` | Fixed search with 2-line context |
| `/export pane [path]` | Dump pane to a text file |
| `/sidebar hide` | Collapse the metrics rail |

### Knowledge / RAG Commands (when RAG is implemented)
| Command | Action |
|---|---|
| `/learn [file.txt]` | Add a document to Nexa's knowledge base |
| `/forget [topic]` | Remove a topic from the knowledge base |
| `/search [query]` | Search the knowledge base directly |
| `/sources` | Show what sources Nexa used in the last reply |

### Feedback & Stats Commands
| Command | Action |
|---|---|
| `/whoami` | Show your profile (name, stats, streak) |
| `/stats` | Show total questions asked, accuracy rating |
| `/version` | Show Nexa version info |
| `/feedback good` | Rate last response positively |
| `/feedback bad` | Rate last response negatively (helps training) |

---

## 8. Memory & Context System

### Short-term Conversation Memory
```python
class NexaMemory:
    def __init__(self, max_turns=10):
        self.history = []           # list of (user, nexa) pairs
        self.max_turns = max_turns
        self.user_name = ""
        self.session_start = datetime.now()

    def add(self, user_msg, nexa_msg):
        self.history.append({"user": user_msg, "nexa": nexa_msg})
        if len(self.history) > self.max_turns:
            self.history.pop(0)     # forget oldest turn

    def get_context(self):
        return self.history         # pass this to build_prompt()

    def clear(self):
        self.history = []
```

### Long-term Memory (Between Sessions)
```python
import json, os
from datetime import datetime

def save_session(memory, path="~/.nexa/sessions/"):
    data = {"date": str(datetime.now()), "history": memory.history}
    with open(os.path.expanduser(path) + "latest.json", "w") as f:
        json.dump(data, f)

def load_session(path="~/.nexa/sessions/latest.json"):
    path = os.path.expanduser(path)
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None
```

---

## 9. Personality & System Prompt

### Recommended System Prompt
```
You are Nexa, a helpful, honest, and intelligent AI assistant.
You run locally on the user's machine with no internet connection.
You are concise but thorough. You never make up facts.
When you don't know something, you say so clearly.
You can help with coding, math, writing, research, and conversation.
You respond in the same language the user writes in.
You remember the current conversation context.
When writing code, always use clean, commented, working examples.
When solving math, always show your steps clearly.
```

---

## 10. Project File Structure

```
nexa/
├── model/
│   ├── config.json          # model architecture settings
│   ├── weights.pt           # trained model weights
│   └── tokenizer/           # tokenizer files
│       ├── vocab.json
│       └── merges.txt
├── train/
│   ├── pretrain.py          # Phase 1 training script
│   ├── finetune.py          # Phase 2 training script
│   ├── dataset.py           # data loading and processing
│   └── evaluate.py          # test model quality
├── data/
│   ├── raw/                 # raw downloaded datasets
│   ├── processed/           # cleaned and formatted data
│   └── knowledge/           # RAG knowledge base files
├── app/
│   ├── main.py              # entry point — runs the terminal UI
│   ├── chat.py              # chat logic and history
│   ├── commands.py          # slash command handler
│   ├── memory.py            # conversation memory system
│   ├── ui/
│   │   ├── welcome.py       # welcome screen
│   │   ├── signup.py        # first-time setup
│   │   └── chat_ui.py       # main chat interface (Textual)
│   └── profile.py           # user profile storage
├── profiles/
│   └── user.json            # saved user profile
├── sessions/
│   └── history.json         # saved chat sessions
├── requirements.txt
└── README.md
```

---

## 11. Priority Roadmap — What to Build Next

```
Priority 1 — Core working model
  [ ] Train tokenizer on clean data
  [ ] Build and train small transformer (10M params)
  [ ] Basic generate() function working
  [ ] Terminal chat loop working

Priority 2 — Quality
  [ ] Fine-tune on instruction data (Alpaca / Dolly)
  [ ] Add conversation history / context window
  [ ] Implement all slash commands
  [ ] Save / load sessions

Priority 3 — Knowledge
  [ ] Add RAG system with ChromaDB
  [ ] /learn command to add documents
  [ ] /search command against knowledge base
  [ ] /sources command showing retrieved context

Priority 4 — Polish
  [ ] Beautiful Textual UI (welcome + chat screens)
  [ ] User profiles and stats tracking
  [ ] /feedback command → collect data for retraining
  [ ] Response streaming (show tokens as they generate)
  [ ] WCAG 2.1 AA high-contrast theme (already in v9.0)
```

---

## 12. Python Libraries to Install

```bash
# Core AI
pip install torch torchvision
pip install transformers
pip install datasets
pip install tokenizers
pip install sentencepiece
pip install accelerate

# Terminal UI
pip install textual
pip install rich

# Knowledge base / RAG
pip install chromadb
pip install sentence-transformers

# Utilities
pip install numpy
pip install tqdm
pip install pyyaml
pip install click
```

---

## 13. Strategy Summary (from NEXA_STRATEGY.md)

| Strategy | Description | Effort |
|---|---|---|
| **Massive Pre-training** | Wikipedia + OpenWebText + Books + ArXiv | Weeks |
| **RAG (most powerful)** | ChromaDB vector search at answer time | Days to set up |
| **Instruction Fine-tuning** | Alpaca + Dolly + OpenAssistant | Days |
| **Custom Knowledge Base** | Structured JSON/DB Nexa searches first | Hours |
| **Chain of Thought** | Train on step-by-step reasoning examples | Moderate |
| **RLHF / Continuous Loop** | Rate answers → retrain on bad ones | Ongoing |

> **The single biggest tip**: Use RAG + good fine-tuning together.
> Training gives reasoning ability; RAG gives up-to-date knowledge.
> Combined = an AI that *feels* like it knows everything.

---

*This document was created to guide the development of Nexa AI from scratch.*
*Give it to an AI assistant with: "Improve Nexa based on this guide, focus on [area]"*
