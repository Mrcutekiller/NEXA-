# NEXA AI - Neural Engine & X-platform Assistant 🧠🔥

NEXA is a personality-driven, multi-model AI operating system designed for the terminal. It combines advanced emotional intelligence with a powerful CLI engine for developers, featuring local memory, skill integration, and cross-AI capabilities.

---

## 🚀 Key Features

*   **Adaptive Personality Engine**: NEXA changes its tone, humor, and behavior based on your interaction style (Serious, Playful, Sarcastic, etc.).
*   **Persistent Local Intelligence**: Built-in long-term memory system that remembers your preferences, project history, and past conversations.
*   **Powerful CLI Engine**: Manage files, skills, and AI models directly from the command line using the `nexa <category> <action>` syntax.
*   **Multi-Model Switching**: Seamlessly switch between local models and global APIs (OpenAI, Anthropic, Gemini, DeepSeek).
*   **Skill Installation System**: Import and activate new capabilities from GitHub, local packs, or custom JSON definitions.
*   **Encrypted Local Vault**: Secure storage for API credentials and user data using SQLite and simulated encryption.

---

## 🛠️ Installation

### 1. Prerequisites
Ensure you have the following installed on your system:
*   **Python 3.8+**
*   **pip** (Python package manager)
*   **SQLite3** (usually comes with Python)

### 2. Clone the Repository
```bash
git clone https://github.com/youruser/nexa-ai.git
cd nexa-ai
```

### 3. Install Dependencies
Run the following command to install required Python libraries:
```bash
pip install -r requirements.txt
```

*Note: On Windows, some libraries like `pyttsx3` might require additional system drivers (SAPI5).*

---

## 🎮 How to Run

### Windows (PowerShell/CMD)
```powershell
python main.py
```

### Linux / macOS
```bash
python3 main.py
```

---

## 📖 Usage Guide

### 1. Conversational Mode
Simply type anything to chat with NEXA. It will respond with its unique personality and track your "vibe" over time.

### 2. CLI Commands
NEXA supports structured commands for system operations:

#### File Operations
*   `nexa file create <filename> <content>` - Create a new file.
*   `nexa file open <filename>` - Read file content.
*   `nexa file search <query>` - Search for text across your project.
*   `nexa file delete <filename>` - Remove a file.

#### Skill Management
*   `nexa skill list` - See all active skills.
*   `nexa skill install github:user/repo` - Install a skill from GitHub.
*   `nexa skill update <skill_name>` - Update an existing skill.

#### AI & Model Control
*   `nexa model list` - View available AI models.
*   `nexa model switch <model_name>` - Change the active brain (e.g., GPT-4, Claude-3).
*   `nexa api add <provider> <key>` - Securely store an API key.

---

## 🏗️ Technology Stack

*   **Language**: Python 3
*   **Database**: SQLite (Local Vault)
*   **Storage**: JSON + SQLite for configuration and long-term memory.
*   **UI/UX**: Colorama (Terminal styling), Textwrap (Formatting).
*   **Logic Engine**: Custom NEXA Personality & CLI Routing Engine.

---

## 🔧 Troubleshooting

*   **Error: `ModuleNotFoundError`**: Ensure you ran `pip install -r requirements.txt` within your virtual environment.
*   **Voice issues**: If using the voice engine, ensure `pyttsx3` is properly configured for your OS. You can disable voice in `main.py` if not needed.
*   **Database Lock**: If the `.db` file is locked, ensure no other instance of NEXA is running.

---

## 🤝 Contribution Guidelines

We welcome contributions! To contribute:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/NewAbility`).
3. Commit your changes.
4. Push to the branch and open a Pull Request.

---

## ⚖️ License

This project is licensed under the **MIT License**. See the `LICENSE` file for details.

---

## 🎨 Design Rationale: NEXA OMNI Visual Identity

The NEXA OMNI v8.0.0 branding represents a shift from amateur terminal aesthetics to a high-fidelity, professional visual language.

### Core Principles:
*   **Isometric Geometry**: The "Omni-Core" logo utilizes isometric perspective to convey depth, stability, and multi-dimensional intelligence.
*   **Balanced Composition**: A side-by-side header layout ensures technical information and brand identity have equal visual weight, improving scannability.
*   **Neural Color Palette**: A cohesive mix of **Electric Cyan** (Neural Link), **Cyber Red** (Core Engine), and **Monochrome White** (Clarity) creates a sophisticated dark-mode aesthetic.
*   **Refined Typography**: Moving away from cluttered prompts to a minimalist `> ` directive inspired by industry-leading technical interfaces.

### Logo Variations:
*   **Full-Color (Terminal)**: Optimized for ANSI-compatible high-contrast environments.
*   **Monochrome (Print)**: Scalable vector-style ASCII for documentation and logs.
*   **Inverted**: High-visibility design for light-themed console environments.

---
