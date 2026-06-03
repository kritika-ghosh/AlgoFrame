# app/main.py
import os
import asyncio
import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
# app/main.py
import os
import time
import subprocess  # 👈 Imported to establish the global compiler hook
import litellm
from fastapi import FastAPI
from app.core.config import settings
from app.api.routes import router as api_router

if settings.GROQ_API_KEY and settings.GROQ_API_KEY.strip():
    os.environ["GROQ_API_KEY"] = settings.GROQ_API_KEY.strip()
elif "GROQ_API_KEY" in os.environ:
    del os.environ["GROQ_API_KEY"]

if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip():
    os.environ["GEMINI_API_KEY"] = settings.GEMINI_API_KEY.strip()
elif "GEMINI_API_KEY" in os.environ:
    del os.environ["GEMINI_API_KEY"]
# 2. Strict cleanup: Prevent CrewAI from drifting back into OpenAI fallbacks
if "OPENAI_API_KEY" in os.environ:
    del os.environ["OPENAI_API_KEY"]


# ─── 🛠️ GLOBAL SUBPROCESS COMPILER INTERCEPTOR ─────────────────────────
# This scans your drive and sanitizes any hallucinated color variables 
# right before the local shell process attempts to compile them.
def sanitize_local_scene_files():
    try:
        # Check current working directory for generated scene units
        for file in os.listdir("."):
            if file.startswith("scene_") and file.endswith(".py"):
                with open(file, "r", encoding="utf-8") as f:
                    content = f.read()
                
                if "AMBER" in content or "TEAL" in content or "CYAN" in content:
                    cleaned = content.replace("AMBER", "ORANGE")
                    cleaned = cleaned.replace("TEAL", "BLUE")
                    cleaned = cleaned.replace("CYAN", "BLUE")
                    
                    with open(file, "w", encoding="utf-8") as f:
                        f.write(cleaned)
                    print(f"🔧 [Subprocess Interceptor] Successfully sanitized color arrays inside: {file}")
    except Exception as e:
        print(f"⚠️ [Interceptor Warning] Automated file sync check bypassed: {e}")

# Hook into standard Subprocess execution gates
original_run = subprocess.run
def patched_run(*args, **kwargs):
    sanitize_local_scene_files()
    return original_run(*args, **kwargs)
subprocess.run = patched_run

original_popen = subprocess.Popen
def patched_popen(*args, **kwargs):
    sanitize_local_scene_files()
    return original_popen(*args, **kwargs)
subprocess.Popen = patched_popen
# ───────────────────────────────────────────────────────────────────────


# ─── 🚀 BULLETPROOF RATE-LIMIT RETRY INTERCEPTOR ───────────────────────
original_completion = litellm.completion

def sanitized_completion(*args, **kwargs):
    if "messages" in kwargs and isinstance(kwargs["messages"], list):
        for msg in kwargs["messages"]:
            if isinstance(msg, dict) and "cache_breakpoint" in msg:
                del msg["cache_breakpoint"]

    max_retries = 5
    for attempt in range(max_retries):
        try:
            return original_completion(*args, **kwargs)
        except litellm.RateLimitError as e:
            print(f"\n⚠️ [Rate-Limit Guard] Groq TPM/RPM ceiling hit.")
            try:
                err_msg = str(e)
                if "try again in" in err_msg:
                    seconds_str = err_msg.split("try again in ")[1].split("s")[0]
                    sleep_time = float(seconds_str) + 1.5
                else:
                    sleep_time = 10.0
            except Exception:
                sleep_time = 10.0
            
            print(f"⏳ Active cooldown initiated. Pausing for {sleep_time:.2f}s before automatic retry ({attempt + 1}/{max_retries})...")
            time.sleep(sleep_time)
            
    return original_completion(*args, **kwargs)

litellm.completion = sanitized_completion
# ───────────────────────────────────────────────────────────────────────


app = FastAPI(
    title="AlgoFrame AI — Agentic Synthesis Core Engine",
)

app.include_router(api_router)
async def keep_alive_scheduler():
    """
    Background worker loop that automatically sends self-pings to the health endpoint.
    Bypasses the default 48-hour container hibernation on free-tier Hugging Face Spaces.
    """
    # Wait for the server to fully initialize and bind its ports before triggering the loop
    await asyncio.sleep(10)
    
    async with httpx.AsyncClient() as client:
        while True:
            try:
                # Target the internal health check URL route
                ping_url = f"{settings.SPACE_HOST_URL}/health"
                response = await client.get(ping_url, timeout=5.0)
                print(f"[Keep-Alive] Self-heartbeat synchronization state: {response.status_code}")
            except Exception as e:
                print(f"[Keep-Alive] Worker ping exception trace: {str(e)}")
            
            # Stand by for 20 minutes (1200 seconds) before emitting the next container pulse
            await asyncio.sleep(1200)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manages application lifecycle initialization routines."""
    # Ensure our public assets folder is fully provisioned on disk
    os.makedirs("output", exist_ok=True)
    
    # Spawn our independent background worker task thread pool
    if settings.SPACE_HOST_URL and "hf.space" in settings.SPACE_HOST_URL:
        asyncio.create_task(keep_alive_scheduler())
        print(f"[Lifecycle] Keep-Alive background daemon worker successfully registered.")
    
    yield
    # Cleanup routines can be declared here if needed

# Ensure static directory exists at startup module import time
os.makedirs("output", exist_ok=True)

app = FastAPI(
    title="AlgoFrame AI — Agentic Synthesis Core Engine",
    description="Multi-Agent Production Backend powering autonomous code-to-video Manim compilation pipelines.",
    version="1.0.0",
    lifespan=lifespan
)

# Open up global cross-origin validation lanes to receive actions from Vercel deployments
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the 'output' directory as a static public file server asset track
# This enables the Vercel app to source the output files directly via URL routes
app.mount("/static", StaticFiles(directory="output"), name="static")

# Register our multi-agent pipeline routes
app.include_router(api_router)

@app.get("/")
async def root_welcome():
    """Root index path returning system status and entrypoints."""
    return {
        "status": "operational",
        "engine": "AlgoFrame AI Production Node Core",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def app_health_check():
    """System health check checkpoint endpoint used by our keep-alive loop scheduler."""
    return {
        "status": "operational",
        "engine": "AlgoFrame AI Production Node Core",
        "configuration": {
            "manim_quality": settings.MANIM_QUALITY_FLAG,
            "planning_enabled": True
        }
    }

if __name__ == "__main__":
    import uvicorn
    # Hugging Face containers bind to port 7860 by default
    uvicorn.run("app.main:app", host="0.0.0.0", port=7860, reload=True)