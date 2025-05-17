import sys
import asyncio
import os
from fastapi import FastAPI
from dotenv import load_dotenv

from app.api import router as api_router

# Set Windows-specific event loop policy
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Load environment variables from .env
load_dotenv()

UNIBET_USERNAME = os.getenv("UNIBET_USERNAME")
UNIBET_PASSWORD = os.getenv("UNIBET_PASSWORD")

if not UNIBET_USERNAME or not UNIBET_PASSWORD:
    print("❌ UNIBET_USERNAME or UNIBET_PASSWORD is not set in your .env file")
else:
    print(f"✅ UNIBET_USERNAME: {UNIBET_USERNAME}")
    print(f"✅ UNIBET_PASSWORD: {UNIBET_PASSWORD}")

# Initialize FastAPI app
app = FastAPI()

# Mount API routes
app.include_router(api_router, prefix="")

@app.on_event("startup")
async def startup_event():
    print("🚀 Server started and ready to receive requests.")
