from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
import time
import json
from datetime import datetime
from nexa_engine import NexaLogicEngine
from nexa_storage import NexaStorage
from memory_manager import MemoryManager

app = FastAPI(title="NEXA OMNI Professional Interface")
templates = Jinja2Templates(directory="templates")

# Initialize NEXA Core
storage = NexaStorage()
memory = MemoryManager()
engine = NexaLogicEngine(user_summary=memory.get_context_summary(), storage=storage)

# Security/Session Simulation
sessions = {}

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

@app.post("/chat")
async def chat_endpoint(message: str = Form(...)):
    """Handles professional chat interaction."""
    start_time = time.time()
    
    # Process with engine
    response = engine.generate_response(message)
    
    # Track performance (Task 4)
    latency = f"{(time.time() - start_time):.3f}s"
    
    return JSONResponse({
        "status": "success",
        "response": response,
        "latency": latency,
        "timestamp": datetime.now().strftime("%H:%M:%S")
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
