# NEXA OMNI SYSTEM 🧠🔥

**NEXA OMNI** is a professional, high-fidelity AI Operating System and technical agent suite. Designed for developers and power users, it provides a dual-interface experience: an elite Terminal CLI and a modern, glassmorphic Web Dashboard.

---

## 🚀 Step-by-Step Guide

### 1. Prerequisites
Ensure you have the following installed on your system:
- Python 3.8+
- pip (Python package manager)
- SQLite3 (usually comes with Python)

### 2. Installation
```bash
git clone https://github.com/Mrcutekiller/NEXA-.git
cd NEXA-
pip install -r requirements.txt
```

### 3. Launching the Neural Link
- **Terminal Interface**: Run `python main.py`. This is your primary command center.
- **Web Dashboard**: Run `python nexa_api.py` and open `http://localhost:8000`.

### 4. Initialization
Upon first launch, NEXA will ask for your identity and objectives. This synchronizes the neural vault with your specific needs.

### 5. Core Interaction
- **Chat**: Simply type naturally. NEXA uses OMNI-level logic to analyze and respond.
- **Protocols**: Type `/` to access the high-speed command menu.
- **Voice**: Type `voice on` to activate the deep "Batman-style" neural synthesis.

---

## 🛠️ Advanced Capabilities

*   **Neural Voice Synthesis**: Features a deep, authoritative male voice with a calculated, "Batman-tier" cadence for maximum focus.
*   **Autonomous Skill Forge**: NEXA can build its own capabilities. Use `/forge skill [Goal]` to have the AI write and install new Python-based skills.
*   **Universal Knowledge Mastery**: Deep expertise in **Cybersecurity**, **Game Dev**, **Video/Multimedia Editing**, **Mobile/Web Development**, and **Office Suite Automation**.
*   **System Agent Protocols**:
    *   **Browser**: `nexa browser search [Query]`
    *   **App Launcher**: `nexa open [App Name]` (Optimized for CapCut, VS Code, etc.)
    *   **File Agent**: Complete project-wide file manipulation (`open`, `create`, `edit`, `search`).
*   **Omni-Interface Control**: Seamlessly switch between CLI and Web. Core logic and memory are fully synchronized.

---

## ⌨️ Command System (Slash Protocols)

### Engine Commands
| Protocol | Action | Description |
| :--- | :--- | :--- |
| `/model` | `view` | Display current neural node status |
| `/profile` | `update` | Synchronize user identity |
| `/skill` | `list` | View active skill packs |
| `/forge` | `skill` | Initialize autonomous skill synthesis |
| `/auth` | `logout` | Terminate neural session |
| `/file` | `search` | Query project filesystem |

### Terminal Workspace Commands (v9.0+)
| Protocol | Action | Description |
| :--- | :--- | :--- |
| `/tab` | `new <label>` | Create a new workspace tab |
| `/tab` | `swap <a> <b>` | Swap two tabs by index |
| `/tab` | `pin [ref]` | Pin/unpin tab (prevents accidental close) |
| `/tab` | `close [ref]` | Close a tab |
| `/pane` | `split vertical\|horizontal` | Split current pane |
| `/pane` | `resize <pct>` | Resize active pane (10–90%) |
| `/pane` | `focus <ref>` | Focus a specific pane |
| `/search` | `--regex <p>` | Regex search in pane output |
| `/search` | `--fixed <t> --context 2` | Fixed text search with context lines |
| `/export` | `pane [path]` | Dump pane output to a text file |
| `/theme` | `dark\|light\|high-contrast` | Switch accessibility theme |
| `/sidebar` | `toggle\|show\|hide` | Collapse / expand metrics rail |
| `/bookmark` | `add\|run <idx>` | Save and replay commands |
| `/settings` | `delay <ms>` | Configure autocomplete delay |
| `/voice` | `on\|off\|listen-on` | Toggle voice synthesis |

---

## 💻 Tech Stack

- **Core Engine**: Python 3.8+, SQLite3
- **Terminal UI**: `prompt_toolkit`, `colorama`, `pyttsx3` (Custom Batman Voice Config)
- **Web Interface**: FastAPI, Jinja2, Tailwind CSS, Framer Motion
- **Agents**: `subprocess`, `webbrowser`, `speech_recognition`
- **Accessibility**: WCAG 2.1 AA compliant themes (dark / light / high-contrast)
- **Architecture**: Modular "Skill Pack" System with Forge Protocol

---

## 🎨 Design Rationale

The NEXA OMNI visual identity follows **High-Fidelity Minimalist** principles inspired by Claude. It balances technical transparency with brand credibility. The "Thought-Action-Result" loop ensures you are never in the dark about the AI's logic.

The v9.0 terminal redesign adds:
- **Adaptive banner** that scales to any terminal width
- **Box-drawing pane borders** (`╔╗╚╝` for active, `┌┐└┘` for passive)
- **Atomic session saves** — crash-safe write-to-temp-then-rename
- **Buffered output flush** — single `sys.stdout.write` per response for < 100 ms latency

---

## 📖 Additional Resources

*   **[NEXA Strategy Guide](NEXA_STRATEGY.md)**: Roadmap, training datasets, and engineering strategies to make Nexa feel like it knows everything.
*   **[NEXA Build Guide](NEXA_BUILD_GUIDE.md)**: Complete architecture, tokenizer training, dataset reference, slash command spec, and project file structure.
*   **[Terminal Performance Report](NEXA_TERMINAL_REPORTS.md)**: Latency benchmarks, WCAG contrast ratios, cross-platform test matrix, and user testing summary.

---

**NEXA OMNI** - *Dangerously smart, uniquely alive.* 🔥
