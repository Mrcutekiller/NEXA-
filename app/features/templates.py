# app/features/templates.py
import os
import json
from typing import Dict, List, Any

class TemplateManager:
    BUILT_IN_TEMPLATES = {
        "react-app": {
            "desc": "Full React app with routing, state, dark mode",
            "content": """// React App Template
import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';

function App() {
  const [theme, setTheme] = useState('dark');
  return (
    <Router>
      <div className={`app ${theme}`}>
        <nav>
          <Link to="/">Home</Link> | <Link to="/dashboard">Dashboard</Link>
          <button onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}>Toggle Theme</button>
        </nav>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </div>
    </Router>
  );
}
export default App;"""
        },
        "api-server": {
            "desc": "Python FastAPI server with auth + database",
            "content": """# FastAPI Server Template
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

app = FastAPI(title="Nexa Powered API")

class User(BaseModel):
    username: str
    email: str

@app.get("/")
def read_root():
    return {"message": "Welcome to Nexa REST API Server"}

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    return {"access_token": form_data.username + "_token", "token_type": "bearer"}"""
        },
        "landing-page": {
            "desc": "Marketing landing page with hero + pricing + CTA",
            "content": """<!-- HTML Landing Page Template -->
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Beautiful Landing Page</title>
  <style>
    body { font-family: 'Outfit', sans-serif; background: #0b0f19; color: #fff; margin: 0; }
    .hero { text-align: center; padding: 100px 20px; background: linear-gradient(135deg, #1e2640, #0b0f19); }
    .cta-btn { padding: 15px 30px; background: #38bdf8; border: none; border-radius: 8px; color: #000; font-weight: bold; cursor: pointer; }
  </style>
</head>
<body>
  <div class="hero">
    <h1>Transform Your Workflow with NEXA</h1>
    <p>The ultimate offline-first intelligence assistant running on your hardware.</p>
    <button class="cta-btn">Get Started Now</button>
  </div>
</body>
</html>"""
        },
        "dashboard": {
            "desc": "Admin dashboard with sidebar + charts + tables",
            "content": "<!-- Dashboard Template -->\n<div class='dashboard'>\n  <aside class='sidebar'>Sidebar Navigation</aside>\n  <main class='content'>Stats Grid</main>\n</div>"
        },
        "design-system": {
            "desc": "Full CSS design system with CSS custom property tokens",
            "content": """:root {
  --primary-color: #0ea5e9;
  --secondary-color: #f43f5e;
  --bg-color: #0f172a;
  --surface-color: #1e293b;
  --text-primary: #f8fafc;
  --font-family: 'Inter', sans-serif;
  --border-radius: 8px;
}"""
        }
    }

    def __init__(self, user_dir: str = "user/templates"):
        self.user_dir = user_dir
        os.makedirs(user_dir, exist_ok=True)

    def list_templates(self) -> str:
        lines = ["📋 AVAILABLE TEMPLATES:"]
        lines.append("\n[Built-in templates]")
        for name, data in self.BUILT_IN_TEMPLATES.items():
            lines.append(f"  - {name:15} | {data['desc']}")
            
        custom = self.list_custom_templates()
        if custom:
            lines.append("\n[Your Custom templates]")
            for c in custom:
                lines.append(f"  - {c}")
        return "\n".join(lines)

    def list_custom_templates(self) -> List[str]:
        if not os.path.exists(self.user_dir):
            return []
        return [f.replace(".txt", "") for f in os.listdir(self.user_dir) if f.endswith(".txt")]

    def get_template_content(self, name: str) -> str:
        # Check built-in first
        if name in self.BUILT_IN_TEMPLATES:
            return self.BUILT_IN_TEMPLATES[name]["content"]
            
        # Check custom
        custom_path = os.path.join(self.user_dir, f"{name}.txt")
        if os.path.exists(custom_path):
            with open(custom_path, "r", encoding="utf-8") as f:
                return f.read()
        raise FileNotFoundError(f"Template '{name}' not found.")

    def save_custom_template(self, name: str, content: str) -> str:
        custom_path = os.path.join(self.user_dir, f"{name}.txt")
        with open(custom_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Template '{name}' saved to your personal templates."

    def delete_template(self, name: str) -> str:
        custom_path = os.path.join(self.user_dir, f"{name}.txt")
        if os.path.exists(custom_path):
            os.remove(custom_path)
            return f"Personal template '{name}' deleted."
        return f"Personal template '{name}' not found."
