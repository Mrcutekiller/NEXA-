# app/dashboard/server.py
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import webbrowser
import threading
from typing import Dict, Any

class NexaDashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/nexa-dashboard':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = self.generate_dashboard_html()
            self.wfile.write(html.encode('utf-8'))
        elif self.path == '/api/stats':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            stats = self.load_stats()
            self.wfile.write(json.dumps(stats).encode('utf-8'))
        elif self.path == '/api/knowledge':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            knowledge = self.load_json("user/knowledge.json", {"facts": []})
            self.wfile.write(json.dumps(knowledge).encode('utf-8'))
        elif self.path == '/api/mistakes':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            mistakes = self.load_json("user/mistakes.json", [])
            self.wfile.write(json.dumps(mistakes).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path.startswith('/api/knowledge/delete/'):
            fact_id = self.path.split('/')[-1]
            success = self.delete_fact(fact_id)
            self.send_response(200 if success else 400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"success": success}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def load_json(self, path: str, default: Any) -> Any:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return default

    def load_stats(self) -> Dict[str, Any]:
        profile = self.load_json("user/profile.json", {})
        stats = self.load_json("user/stats.json", {})
        badges = self.load_json("user/badges.json", {})
        skill_tree = self.load_json("user/skill_tree.json", [])
        
        # Merge metrics
        return {
            "profile": profile,
            "stats": stats,
            "badges_count": len(badges),
            "skills_count": len(skill_tree)
        }

    def delete_fact(self, fact_id: str) -> bool:
        path = "user/knowledge.json"
        if not os.path.exists(path):
            return False
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            initial_len = len(data.get("facts", []))
            data["facts"] = [f for f in data.get("facts", []) if f.get("id") != fact_id]
            data["total_facts"] = len(data["facts"])
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return len(data["facts"]) < initial_len
        except Exception:
            return False

    def generate_dashboard_html(self) -> str:
        # Load local data to hydrate UI
        profile = self.load_json("user/profile.json", {"name": "Developer", "level": 1, "total_xp": 100})
        stats = self.load_json("user/stats.json", {"streak": 1, "message_count": 12})
        knowledge = self.load_json("user/knowledge.json", {"facts": []})
        mistakes = self.load_json("user/mistakes.json", [])
        badges = self.load_json("user/badges.json", {})
        notes = self.load_json("user/notebook.json", [])

        facts_rows = "".join([
            f"<tr><td>{f['id']}</td><td>{f['topic']}</td><td>{f['content']}</td><td>{f['times_referenced']}</td></tr>"
            for f in knowledge.get("facts", [])
        ])

        mistakes_rows = "".join([
            f"<tr><td>{m['topic']}</td><td>{m['title']}</td><td>{m['lesson']}</td></tr>"
            for m in mistakes
        ])

        notes_cards = "".join([
            f"<div class='card note-card'><h3>{n['title']}</h3><p>{n['content']}</p><small>{n['created_at']}</small></div>"
            for n in notes
        ])

        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>NEXA Intelligence Dashboard</title>
    <style>
        body {{
            font-family: 'Outfit', 'Inter', sans-serif;
            background-color: #0b0f19;
            color: #f8fafc;
            margin: 0;
            padding: 20px;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #38bdf8;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .card {{
            background: #1e293b;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }}
        .card h3 {{ margin-top: 0; color: #38bdf8; }}
        .card .value {{ font-size: 2rem; font-weight: bold; margin: 10px 0; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
            background: #1e293b;
            border-radius: 8px;
            overflow: hidden;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #334155;
        }}
        th {{ background-color: #0f172a; color: #38bdf8; }}
        .note-card {{
            border-left: 4px solid #a855f7;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>👑 NEXA Intelligence Hub</h1>
        <div>Level {profile.get('level', 1)} • {profile.get('total_xp', 0)} XP</div>
    </div>
    
    <div class="grid">
        <div class="card">
            <h3>Daily Streak</h3>
            <div class="value">🔥 {stats.get('streak', 0)} Days</div>
        </div>
        <div class="card">
            <h3>Learned Facts</h3>
            <div class="value">📚 {len(knowledge.get('facts', []))}</div>
        </div>
        <div class="card">
            <h3>Bugs Corrected</h3>
            <div class="value">🐛 {len(mistakes)}</div>
        </div>
        <div class="card">
            <h3>Achievement Badges</h3>
            <div class="value">🏆 {len(badges)}</div>
        </div>
    </div>

    <h2>📚 Knowledge Base Table</h2>
    <table>
        <thead>
            <tr>
                <th>ID</th>
                <th>Topic</th>
                <th>Fact Content</th>
                <th>Times Used</th>
            </tr>
        </thead>
        <tbody>
            {facts_rows if facts_rows else '<tr><td colspan="4">No facts learned yet. Teach NEXA in chat!</td></tr>'}
        </tbody>
    </table>

    <h2>🐛 Mistake & Lesson Log</h2>
    <table>
        <thead>
            <tr>
                <th>Topic</th>
                <th>Error Title</th>
                <th>Lesson Learned</th>
            </tr>
        </thead>
        <tbody>
            {mistakes_rows if mistakes_rows else '<tr><td colspan="3">No mistakes logged yet. Fix bugs using NEXA Fix!</td></tr>'}
        </tbody>
    </table>

    <h2>📓 Personal Notes</h2>
    <div class="grid">
        {notes_cards if notes_cards else '<p>No saved notes found.</p>'}
    </div>
</body>
</html>"""
        return html_template

# ─── Live Preview Server ──────────────────────────────────────────────────────
class NexaPreviewHandler(BaseHTTPRequestHandler):
    last_rendered_code = "<h1>No code rendered yet. Run a preview command.</h1>"

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(NexaPreviewHandler.last_rendered_code.encode('utf-8'))

    @classmethod
    def update_code(cls, code: str):
        cls.last_rendered_code = code

def start_dashboard_server():
    server = HTTPServer(('localhost', 7749), NexaDashboardHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()

def start_preview_server():
    server = HTTPServer(('localhost', 7750), NexaPreviewHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()

def open_dashboard():
    start_dashboard_server()
    start_preview_server()
    webbrowser.open('http://localhost:7749')
