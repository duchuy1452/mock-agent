#!/usr/bin/env python3
"""
Expert Sure Backend - Startup Script
Run this to start the FastAPI server
"""

import uvicorn
import os

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("downloads", exist_ok=True)

    print("🚀 Starting Expert Sure Backend...")
    print("📊 Dashboard will be available at: http://localhost:8000")
    print("📡 WebSocket endpoint: ws://localhost:8000/ws/{project_id}")
    print("📁 API docs: http://localhost:8000/docs")

    # Run the FastAPI server
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
