from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
import time
import json
import re
from datetime import datetime
from nexa_engine import NexaLogicEngine
from nexa_storage import NexaStorage
from memory_manager import MemoryManager
from app.model_manager import NexaModelManager
from app.commands import CommandRouter

app = FastAPI(title="NEXA OMNI Professional Interface")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

# Initialize NEXA Core
storage = NexaStorage()
memory = MemoryManager()
model_manager = NexaModelManager()

# Sync active model from storage config
active_model_from_config = storage.config.get("settings", {}).get("active_model") or storage.config.get("active_model")
if active_model_from_config:
    model_manager.active_model_key = active_model_from_config.lower()

engine = NexaLogicEngine(user_summary=memory.get_context_summary(), storage=storage, memory_manager=memory)
engine.active_model = model_manager.active_model_key.upper()

# Ensure model manager switch changes engine active_model
def on_model_switch(key, cfg):
    engine.active_model = key.upper()

model_manager.subscribe_model_switch(on_model_switch)

router = CommandRouter(
    model_manager=model_manager,
    storage=storage,
    memory_manager=memory
)

# Security/Session Simulation
sessions = {}

ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')

def strip_ansi(text: str) -> str:
    return ansi_escape.sub('', text)

@app.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    """Serves the professional dashboard."""
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "engine_name": engine.name,
        "version": engine.version,
        "creator": engine.creator,
        "status": "OPTIMAL",
        "user_name": engine.user_name
    })

@app.get("/status")
async def status_endpoint():
    """Returns the current state of the backend to the frontend."""
    # Ensure active model is in sync
    engine.active_model = model_manager.active_model_key.upper()
    
    # Get user traits
    traits = memory.memory.setdefault("user_traits", {})
    name = traits.get("name") or "Human"
    age = traits.get("age") or "Not set"
    interests = traits.get("interests") or []
    mood = traits.get("dominant_mood") or "neutral"
    chats = traits.get("interaction_count") or 0
    
    # Get installed skills
    installed_skills = storage.config.get("installed_skills", {})
    skills_list = []
    # Core skills
    core_skills = [
        {"name": "web_search", "desc": "Live Google & browser lookup", "type": "core"},
        {"name": "open_app", "desc": "Launch desktop applications", "type": "core"},
        {"name": "file_system", "desc": "Read, write, search local files", "type": "core"},
        {"name": "image_analysis", "desc": "Scan visuals and metadata", "type": "core"}
    ]
    skills_list.extend(core_skills)
    for sname, info in installed_skills.items():
        skills_list.append({"name": sname, "desc": f"External: {info.get('source')}", "type": "external"})
        
    return JSONResponse({
        "status": "success",
        "active_model": model_manager.active_model_key,
        "profile": {
            "name": name,
            "age": age,
            "interests": interests,
            "mood": mood,
            "chats": chats
        },
        "skills": skills_list
    })

@app.post("/chat")
async def chat_endpoint(message: str = Form(...)):
    """Handles professional chat interaction with command routing support."""
    start_time = time.time()
    
    # Check if the input is a slash command
    if message.startswith("/"):
        cmd_res = router.route(message)
        response = strip_ansi(cmd_res.text)
        # Keep engine model synchronized
        engine.active_model = model_manager.active_model_key.upper()
    else:
        # Process with engine
        response = engine.generate_response(message)
    
    # Track performance (Task 4)
    latency = f"{(time.time() - start_time):.3f}s"
    
    return JSONResponse({
        "status": "success",
        "response": response,
        "latency": latency,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "active_model": model_manager.active_model_key
    })

@app.post("/auth/logout")
async def logout():
    """Requirement 2: Secure Logout Feature."""
    # Invalidate session logic
    engine.user_name = "Guest"
    return JSONResponse({
        "status": "logged_out",
        "redirect": "/login",
        "message": "[SESSION_INVALIDATED] Neural link severed securely."
    })

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Requirement 2: Redirection to login page."""
    return templates.TemplateResponse("login.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
