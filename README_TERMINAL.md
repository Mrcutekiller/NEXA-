# NEXA OMNI TERMINAL: Professional Workspace Documentation

## 🚀 Overview
The NEXA OMNI Terminal is a high-performance, functionally robust workspace designed for professional developers. It bridges the gap between a standard shell and an AI-driven IDE, providing advanced session management, real-time metrics, and elite intelligence protocols.

---

## 🛠️ Key Features

### 1. Advanced Session Management
- **Tabbed Workspace**: Manage unlimited sessions with `/tab`. Each tab is persisted across launches.
- **Split-Pane Layouts**: Divide your focus with `/pane split`. Supports vertical and horizontal tiling.
- **Session Restoration**: Automatic state preservation. If the application closes, your tabs, panes, and command history are restored instantly.

### 2. Elite Usability & UI
- **Adaptive Layout**: Dynamically adjusts to your terminal dimensions for maximum readability.
- **Accessibility Themes**: Built-in Dark and Light modes (`/theme toggle`) optimized for WCAG 2.1 AA contrast standards.
- **Syntax Highlighting**: Real-time coloring for shell commands, file paths, and system logs.
- **Collapsible Metrics Rail**: A persistent sidebar (`/sidebar`) showing disk usage, network status, and active bookmarks.

### 3. Functional Power Tools
- **Deep Autocomplete**: Context-aware suggestions based on command history, system utilities, and project file paths.
- **Regex Search**: Instantly find patterns in your output history with `/search`.
- **Quick-Access Bookmarks**: Pin frequently used commands with `/bookmark` for rapid execution.
- **Omni-Logic Integration**: Full access to NEXA AI protocols (`/model`, `/forge`, `/skill`, etc.) directly from the prompt.

---

## ⌨️ Command Reference

| Protocol | Action | Description |
| :--- | :--- | :--- |
| `/tab` | `new <label>` | Create a new workspace tab |
| `/tab` | `switch <index>` | Jump to a specific tab |
| `/pane` | `split <v\|h>` | Split the active view vertically or horizontally |
| `/search` | `--regex <p>` | Search output history using Regular Expressions |
| `/theme` | `toggle` | Switch between high-contrast light and dark modes |
| `/sidebar` | `toggle` | Expand or collapse the metrics rail |
| `/bookmark` | `add <cmd>` | Save a command to your quick-access list |
| `/settings` | `delay <ms>` | Configure autocomplete trigger delay (0-500ms) |

---

## 🏗️ Technical Architecture
- **Engine**: Python 3.10+
- **Frontend**: `prompt_toolkit` (High-performance TUI framework)
- **Metrics**: `psutil` (System-level resource monitoring)
- **Persistence**: SQLite (Logs) + JSON (Workspace State)

---

**NEXA OMNI** - *The professional standard for AI-integrated terminal workspaces.*
