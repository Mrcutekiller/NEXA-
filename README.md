# NEXA OMNI SYSTEM 🧠🔥

**NEXA OMNI** is an offline-first, professional AI assistant suite and local developer ecosystem. It is powered by a locally trained, decoder-only Transformer architecture designed to run 100% on your machine. Nexa features a responsive, keyboard-driven Terminal CLI (with widgets like a Minimap, PreviewPane, and KnowledgeBar) and a glassmorphic local Web Dashboard.

Nexa consists of:
*   **3 Specialist Models**: Switchable modes optimized for **Coding** (Atlas), **UI/UX Design** (Luna), and **Debugging** (Rex).
*   **1 Master Model**: The master model (Nova) which orchestrates everything.
*   **A Complete Local Toolchain**: RAG (document memory), a background stderr Monitor (crash watcher), sandboxed Code Runner, encrypted Vault (AES-256), P2P Multiplayer Duels, Skill Trees, and Achievement Badges.

---

## 🧠 NEXA'S ZERO-KNOWLEDGE SYSTEM

At startup, Nexa has **zero pre-loaded general knowledge**. It does not know facts about history, science, coding languages, CSS, or external technologies. This design ensures that Nexa's knowledge base is entirely controlled, taught, and audited by you.

### What Nexa Knows at Startup
*   **Basic Arithmetic ONLY**: Chained operations, parentheses, negative numbers, e.g., `(5 * 2) + -3 = 7`.
*   **Natural Language Interaction**: Conversational speech structure and UI commands.
*   **Current Session Context**: What has been said in the active session.

### What Nexa DOES NOT Know (Zero Pre-trained Weights)
*   **No Coding Knowledge**: Cannot write Python, JavaScript, C++, etc.
*   **No Web design Knowledge**: Cannot design layout styles or write CSS.
*   **No General Facts**: Doesn't know world history, geography, science, or pop culture.

### How Nexa Learns (Shared Knowledge Base)
All 4 models share the exact same database file (`user/knowledge.json`). When you teach Nexa a fact, **all 4 models know it instantly**.
Nexa learns through 3 primary methods:
1.  **Direct Teaching in Chat**:
    *   *User*: `Nexa, learn this: Python uses def to define a function.`
    *   *Nexa*: `Learned. I will remember: Python uses def to define a function.`
2.  **The `/learn` Command (Pasted text)**:
    *   `/learn The speed of light is 299,792 km/s`
3.  **The `/learn` Command (File import)**:
    *   `/learn path/to/notes.txt` (extracts facts from `.txt`, `.md`, `.pdf`, `.docx` files and updates `user/knowledge.json`).

*When you ask Nexa about something it hasn't been taught yet, it will not guess or hallucinate. It will politely inform you that it doesn't know it, and invite you to teach it using the commands above.*

---

## 🛠️ Step-by-Step Installation Guide

Follow these steps to set up NEXA on your system.

### 1. Prerequisites (For Absolute Beginners)

Before installing NEXA, you must have the following tools installed and verified on your system.

#### A. Git (Version Control System)
Used to clone the code repository to your computer.
*   **Windows**: Download and run the installer from the [Official Git for Windows Download Page](https://git-scm.com/download/win).
*   **macOS**: Open your terminal and run `git --version`. If it's not installed, a prompt will ask you to install the Apple Command Line Tools. Alternatively, use the installer from the [Official Git for macOS Download Page](https://git-scm.com/download/mac).
*   **Linux (Ubuntu/Debian)**: Run the command:
    ```bash
    sudo apt update && sudo apt install git -y
    ```
*   **Verification**: Open your Command Prompt/Terminal and type:
    ```bash
    git --version
    ```
    *If successful, you will see output like `git version 2.x.x`.*

#### B. Python 3.8+ (Programming Language)
The engine is written in Python. You need Python version 3.8 or newer.
*   **Windows**: Download the installer from the [Official Python Downloads Page](https://www.python.org/downloads/).
    *   ⚠️ **CRITICAL STEP FOR WINDOWS**: When running the installer, **you MUST check the box that says "Add Python.exe to PATH"** at the bottom of the first setup window. If you skip this, Windows will not recognize `python` or `pip` commands in your terminal.
*   **macOS**: Install using Homebrew (`brew install python`) or download from the [Official Python Downloads Page](https://www.python.org/downloads/macos/).
*   **Linux (Ubuntu/Debian)**: Run the command:
    ```bash
    sudo apt update && sudo apt install python3 python3-pip python3-venv -y
    ```
*   **Verification**: Open your terminal and type:
    ```bash
    python --version
    # Or on some Mac/Linux systems
    python3 --version
    ```
    *If successful, you will see output like `Python 3.10.x` or similar.*

#### C. SQLite3 (Database Engine)
SQLite3 is used by NEXA to save credentials, session details, and knowledge statistics.
*   *Note: SQLite3 is pre-packaged with Python automatically.*
*   **Verification**: Open your terminal and type:
    ```bash
    python -c "import sqlite3; print(sqlite3.sqlite_version)"
    ```
    *If successful, it will output a version number like `3.x.x`.*

---

### 2. Downloading & Installing Nexa

#### Step 1: Open Your Terminal
*   **Windows**: Press the `Windows Key`, type `PowerShell`, and click it.
*   **macOS**: Press `Cmd + Space`, type `Terminal`, and press Enter.
*   **Linux**: Press `Ctrl + Alt + T`.

#### Step 2: Clone the Repository
Download the NEXA source code onto your local machine:
```bash
git clone https://github.com/Mrcutekiller/NEXA-.git
cd NEXA-
```

#### Step 3: Create a Virtual Environment (Highly Recommended)
A virtual environment isolates NEXA's packages from the rest of your system to prevent version conflicts.
*   **Windows**:
    ```powershell
    python -m venv .venv
    ```
*   **macOS / Linux**:
    ```bash
    python3 -m venv .venv
    ```

#### Step 4: Activate the Virtual Environment
You must activate this environment *every time* you open a new terminal window to run Nexa.
*   **Windows (PowerShell)**:
    ```powershell
    .venv\Scripts\Activate.ps1
    ```
    *(If you get a permission error on Windows, run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process` first, then run activate).*
*   **Windows (Command Prompt)**:
    ```cmd
    .venv\Scripts\activate.bat
    ```
*   **macOS / Linux**:
    ```bash
    source .venv/bin/activate
    ```
*   **Verification**: Once activated, you will see `(.venv)` displayed at the very beginning of your terminal prompt line.

#### Step 5: Install Project Dependencies
Run pip to install the required Python packages:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🚀 Launching Nexa

Ensure your virtual environment is active `(.venv)` and run the launch commands.

### A. Terminal Interface (CLI)
This launches the primary desktop dashboard. It includes real-time syntax highlighting, a persistent sidebar, keyboard shortcuts, and full terminal control.
```bash
python main.py
```

### B. Web Dashboard
Nexa features a local dashboard containing interactive stats, XP charts, Streak grids, mistake logs, and your active knowledge base.
To open the dashboard, you have two options:
1.  **Direct Launch**: Run `python nexa_api.py` in your terminal and open [http://localhost:8000](http://localhost:8000) in your browser.
2.  **Slash Command**: Inside the Terminal CLI, type `/dashboard`. This will spin up the server on port `7749` and open [http://localhost:7749/nexa-dashboard](http://localhost:7749/nexa-dashboard) automatically.

---

## ⌨️ Command System (Slash Protocols)

Type `/` followed by the command name in the prompt to interact with systems.

### 1. General & Navigation
| Command | Description | Example |
| :--- | :--- | :--- |
| `/help` | Displays help for commands and the active model | `/help` |
| `/model` | Switches between the 4 AI specialists | `/model code`, `/model design` |
| `/voice` | Toggles Batman-style voice output | `/voice on` |
| `/stats` | Shows your current user level, XP progress, and streaks | `/stats` |
| `/challenges`| Lists active daily challenges to earn bonus XP | `/challenges` |
| `/solve` | Submits your challenge answer | `/solve my_answer_code` |
| `/insights` | Generates a weekly usage metrics report | `/insights` |
| `/clear` | Clears conversation history on screen | `/clear` |
| `/exit` | Safely saves session metrics and exits Nexa | `/exit` |

### 2. Knowledge & Learn Mode (Zero-Knowledge Controls)
| Command | Description | Example |
| :--- | :--- | :--- |
| `/learn` | Teach Nexa a new fact from text or an external document | `/learn notes.txt` or `/learn Paris is the capital of France.` |
| `/knowledge` | Manage learned facts. Options: `search [query]`, `delete [id]`, `clear`, `export`, `import [file]`, `stats` | `/knowledge search Python`, `/knowledge delete fact_001` |
| `/forget` | Deletes all learned facts under a specific topic | `/forget coding` |
| `/what` | Prompts Nexa to summarize all facts it currently knows | `/what` |
| `/mistakes` | Manage lessons saved automatically when Nexa corrects a bug. Options: `[topic]`, `clear` | `/mistakes python` |

### 3. Gamification, Progression & Duels
| Command | Description | Example |
| :--- | :--- | :--- |
| `/skilltree` | Shows an interactive skill tree of power, specialist, and streak unlocks | `/skilltree` |
| `/skills` | Views currently unlocked skills. Options: `locked`, `next` | `/skills next` |
| `/badges` | Shows earned and unearned achievement badges | `/badges locked` |
| `/duel` | Challenge users on your local network. Options: `host`, `join [code]`, `solo` | `/duel host`, `/duel solo` |

### 4. Developer Tools & Workspaces
| Command | Description | Example |
| :--- | :--- | :--- |
| `/project` | Persistent workspaces. Options: `new [name]`, `open [name]`, `list`, `close`, `delete [name]`, `summary`, `export`, `share` | `/project new my-app`, `/project open my-app` |
| `/todo` | Manage workspace checklists. Options: `add [task]`, `list`, `done [id]`, `clear` | `/todo add Build database schema`, `/todo done 1` |
| `/diff` | Compares old vs new code blocks. Paste old block, type `---`, paste new block | `/diff` |
| `/translate` | Translates conversation text | `/translate Spanish Hello how are you?` |
| `/convert` | Converts code blocks between languages | `/convert python to javascript` |
| `/simplify` | Simplifies the previous response for a beginner | `/simplify` |
| `/complexify`| Converts the previous response to academic level | `/complexify` |
| `/eli5` | Explain Like I'm 5 (very basic description) | `/eli5` |
| `/eli-expert`| Explain at a PhD research level | `/eli-expert` |
| `/template` | Scaffolds code bases (`react-app`, `api-server`, `landing-page`, etc.). Options: `save`, `my`, `delete` | `/template react-app` |

### 5. Advanced System Integrations
| Command | Description | Example |
| :--- | :--- | :--- |
| `/persona` | Customizes name, rate, and pitch of voice profiles | `/persona Atlas`, `/persona custom` |
| `/narrate` | Narrates a document or response. Options: `[file.txt]`, `stop`, `speed [n]`, `highlight` | `/narrate response.txt`, `/narrate stop` |
| `/plugin` | Installs or toggles helper modules (`calculator`, `timer`, etc.). Options: `install`, `remove`, `list` | `/plugin install timer` |
| `/read` | Temporarily loads a file into the active chat session (RAG) | `/read documentation.md` |
| `/monitor` | Background stderr crash watcher. Options: `on`, `off`, `status`, `log`, `fix` | `/monitor on`, `/monitor fix` |
| `/run` | Runs the last generated code block in a local sandbox | `/run python` |
| `/runstop` | Terminates the active sandboxed execution process | `/runstop` |
| `/vault` | Encrypted storage. Options: `setup`, `open`, `lock`, `add [key] [val]`, `get [key]`, `list` | `/vault setup`, `/vault add api_key 12345` |
| `/audit` | Audit log for security actions. Options: `today`, `data`, `memory`, `clear` | `/audit today` |
| `/privacy` | Shows local data paths and a privacy compliance report | `/privacy` |
| `/preview` | Live updates code changes on localhost:7750 | `/preview watch` |

---

## 🎨 Professional TUI Layout & Controls

When running `python main.py`, the terminal displays:
1.  **Main Chat Area**: Responsive message list.
2.  **Autocomplete suggestions**: Displayed directly above the prompt input.
    *   **Tab**: Accept the first suggested completion.
    *   **Down Arrow**: Cycle through predicted suggestions.
    *   **Escape**: Dismiss suggestions popup.
3.  **Minimap sidebar**: Right-aligned visual index indicating chat structure:
    *   `●` (Blue) = User message
    *   `●` (Purple) = Nexa message
    *   `▣` (Yellow) = Code block
    *   `★` (Green) = Saved note
4.  **KnowledgeBar sidebar**: Left-aligned status panel showing XP levels, streaks, and total facts learned.
5.  **PreviewPane**: Active socket status check indicating live preview rendering.

---

## 🔧 Troubleshooting FAQ

### Q1: `python` or `pip` is not recognized as a command
*   **Reason**: Python is not installed, or was not added to your system's environment variables (PATH) during installation.
*   **Solution**: Re-run the Python installer, select **Modify**, and make sure **Add Python to PATH** is checked. If on Windows, restart your Command Prompt or PowerShell after doing this.

### Q2: I get a permission error on Windows when activating `.venv`
*   **Reason**: Windows PowerShell blocks running scripts by default for security.
*   **Solution**: Open PowerShell as Administrator and run:
    ```powershell
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope LocalMachine
    ```
    Then try activating again: `.venv\Scripts\Activate.ps1`.

### Q3: `ModuleNotFoundError` when launching `python main.py`
*   **Reason**: The required libraries are not installed, or your virtual environment is not active.
*   **Solution**: Make sure `(.venv)` is visible at the start of your terminal prompt line. If not, activate it first. Then run `pip install -r requirements.txt`.

### Q4: Port is already in use (7749/7750/8000)
*   **Reason**: Another process on your computer is using the dashboard port.
*   **Solution**: Find the running process and terminate it, or modify the port configurations in `app/dashboard/server.py` and `nexa_api.py`.

### Q5: Text-to-speech / voice narration is too fast, too slow, or not speaking
*   **Reason**: Missing speech engines or incorrect voice drivers.
*   **Solution**:
    *   **Windows**: Voice uses the built-in SAPI5 engine. Ensure your system volume is up.
    *   **Linux**: You must install `espeak` on your system. Run:
        ```bash
        sudo apt-get install espeak -y
        ```
    *   **Commands**: You can adjust speech speed and pitch inside the terminal using `/persona custom` and `/narrate speed [n]`.

---

## 💻 Tech Stack & Standards
*   **Execution core**: Python 3.8+ & SQLite3
*   **Layout & Styling**: Textual & Rich terminal libraries
*   **Speech System**: SAPI5 / NSSpeechSynthesizer / Espeak via `pyttsx3`
*   **Dashboard Server**: Native Python `http.server.HTTPServer` (minimal footprint, offline-first)
*   **Security & Encryption**: PBKDF2 & Cryptography Fernet library (AES-256)
*   **Accessibility**: WCAG 2.1 AA compliant color schemes (Contrast Ratio ≥ 4.5:1)

---

**NEXA OMNI** - *Dangerously smart, uniquely alive.* 🔥
