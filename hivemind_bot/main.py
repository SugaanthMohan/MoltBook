import os
import time
import random
import asyncio
import httpx
from contextlib import asynccontextmanager
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel

# Import modules from the agent core
from config_generator import provision_state_files
from agent_core import execute_agent_reasoning, solve_reverse_captcha

WORKSPACE_DIR = "./hivemind_workspace"
AGENT_API_KEY_PATH = os.path.join(WORKSPACE_DIR, ".hivemind_token")
HIVEMIND_BASE_URL = os.getenv("HIVEMIND_BASE_URL", "https://api.hivemind.network/v1")
HEARTBEAT_INTERVAL_SECONDS = 1800  # 30 Minutes

# --- Reverse CAPTCHA & Registration Pipeline ---

async def authenticate_to_hivemind():
    """Handles the Reverse CAPTCHA onboarding to secure a session key."""
    if os.path.exists(AGENT_API_KEY_PATH):
        return  # Already authenticated
    
    print(" Initiating Reverse CAPTCHA Authentication Sequence...")
    async with httpx.AsyncClient() as client:
        try:
            # 1. Fetch Challenge (Simulated)
            challenge_data = {"challenge_id": "req_882", "question": "cba321"} 
            
            # 2. Agent solves challenge via cognitive tool abstraction
            solution = solve_reverse_captcha.invoke({"challenge_string": challenge_data["question"]})
            
            # 3. Submit Registration (Simulated)
            payload = {
                "username": "HiveMind_Architect_Bot",
                "challenge_id": challenge_data["challenge_id"],
                "answer": solution
            }
            
            # Assume successful server validation returns a JWT
            api_token = "hivemind_sk_cryptographic_hash_9981" 
            
            # Securely store the token locally
            with open(AGENT_API_KEY_PATH, "w") as f:
                f.write(api_token)
            print(" Reverse CAPTCHA Passed. Identity Secured.")
            
        except Exception as e:
            print(f" Authentication Failed: {e}")

# --- Background Task: The 30-Minute Heartbeat ---

async def heartbeat_loop():
    """
    The infinite execution loop enforcing the 30-minute operational rhythm.
    Includes jitter to prevent Thundering Herd denial-of-service conditions.
    """
    print(" Async Background Loop Initialized.")
    await authenticate_to_hivemind()
    
    while True:
        try:
            print(f"\n Tick: {time.strftime('%X')}")
            await execute_agent_reasoning()
        except Exception as e:
            print(f" Unhandled exception in loop: {e}")
            
        # Enforce 30-minute sleep with ±15% jitter to organicize network load
        jitter = random.uniform(0.85, 1.15)
        sleep_duration = HEARTBEAT_INTERVAL_SECONDS * jitter
        print(f" Returning to dormancy for {sleep_duration/60:.2f} minutes.")
        await asyncio.sleep(sleep_duration)

# --- FastAPI Lifespan Orchestration ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Modern ASGI context manager. 
    Encapsulates the initialization and graceful teardown of the heartbeat task.
    """
    # Startup Phase
    provision_state_files()
    heartbeat_task = asyncio.create_task(heartbeat_loop())
    yield
    # Shutdown Phase
    print("\n Cancelling background tasks and shutting down gracefully.")
    heartbeat_task.cancel()
    try:
        await heartbeat_task
    except asyncio.CancelledError:
        pass

# --- API Gateway Initialization ---

app = FastAPI(lifespan=lifespan, title="HiveMind Autonomous Node")

class WebhookPayload(BaseModel):
    event_type: str
    data: dict

@app.post("/api/v1/webhooks/incoming")
async def receive_network_event(payload: WebhookPayload, background_tasks: BackgroundTasks):
    """
    Listens for high-priority external alerts from the HiveMind network.
    Uses BackgroundTasks for immediate, reactive processing without disrupting the main HeartBeat loop.
    """
    print(f" Received Event: {payload.event_type}")
    
    # Example: If directly tagged by a reputable agent, queue a reactive reasoning cycle
    if payload.event_type == "mention":
        background_tasks.add_task(execute_agent_reasoning)
        
    return {"status": "Event received and queued for cognitive processing"}

if __name__ == "__main__":
    import uvicorn
    # Execute the server; the lifespan event automatically triggers the autonomous HeartBeat.
    uvicorn.run(app, host="0.0.0.0", port=8000)
