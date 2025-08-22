from fastapi import (
    FastAPI,
    WebSocket,
    WebSocketDisconnect,
    UploadFile,
    File,
    Form,
    HTTPException,
    Depends,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import asyncio
import json
import uuid
import os
from datetime import datetime
from typing import List, Dict, Optional
import pandas as pd
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models import ProjectCreateResponse, SlideRequest, SlideFieldSelection
from database import get_db, init_database, Project, Slide, ProjectOutput, async_session, wait_for_database
from services.agent import AnalysisAgent
from services.websocket_manager import WebSocketManager

# Create FastAPI app
app = FastAPI(title="Expert Sure - Intelligent Reporting Agent", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for downloads
os.makedirs("downloads", exist_ok=True)
os.makedirs("uploads", exist_ok=True)
app.mount("/downloads", StaticFiles(directory="downloads"), name="downloads")

# WebSocket manager
websocket_manager = WebSocketManager()


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    print("Waiting for database to be ready...")
    if await wait_for_database():
        await init_database()
    else:
        raise Exception("Database failed to become ready")


@app.get("/")
async def root():
    return {"message": "Expert Sure API is running"}


@app.get("/api/projects")
async def get_projects(db: AsyncSession = Depends(get_db)):
    """Get all projects for dashboard"""
    result = await db.execute(select(Project))
    projects = result.scalars().all()

    return {
        "projects": [
            {
                "id": str(project.id),
                "name": project.name,
                "auto_mode": project.auto_mode,
                "status": project.status,
                "created_at": project.created_at.isoformat(),
                "updated_at": project.updated_at.isoformat(),
            }
            for project in projects
        ]
    }


@app.post("/api/projects")
async def create_project(
    name: str = Form(...),
    auto: bool = Form(False),
    data_source: UploadFile = File(...),
    schema: UploadFile = File(...),
    template: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
) -> ProjectCreateResponse:
    """Create new project with file uploads"""

    # Validate file types
    if not data_source.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Data source must be CSV file")

    if not schema.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="Schema must be JSON file")

    if template and not template.filename.endswith((".pptx", ".pptm")):
        raise HTTPException(status_code=400, detail="Template must be PowerPoint file")

    # Create project directory
    project_dir = Path(f"uploads/{uuid.uuid4()}")
    project_dir.mkdir(parents=True, exist_ok=True)

    # Save uploaded files
    data_path = project_dir / data_source.filename
    with open(data_path, "wb") as f:
        content = await data_source.read()
        f.write(content)

    schema_path = project_dir / schema.filename
    with open(schema_path, "wb") as f:
        content = await schema.read()
        f.write(content)

    template_path = None
    if template:
        template_path = project_dir / template.filename
        with open(template_path, "wb") as f:
            content = await template.read()
            f.write(content)

    # Parse schema to get available fields
    try:
        with open(schema_path, "r") as f:
            schema_data = json.load(f)
        available_fields = list(schema_data.keys())
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid schema file: {str(e)}")

    # Create project in database
    project = Project(
        name=name,
        auto_mode=auto,
        status="initialized",
        data_source_path=str(data_path),
        schema_path=str(schema_path),
        template_path=str(template_path) if template_path else None,
        available_fields=available_fields,
    )

    db.add(project)
    await db.commit()
    await db.refresh(project)

    return ProjectCreateResponse(
        project_id=str(project.id),
        websocket_url=f"ws://localhost:8000/ws/{project.id}",
        status="initialized",
    )


@app.get("/api/projects/{project_id}")
async def get_project(project_id: str):
    """Get specific project details"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects_db[project_id]
    return {
        "id": project.id,
        "name": project.name,
        "auto": project.auto,
        "status": project.status.value,
        "available_fields": project.available_fields,
        "slides": project.slides,
        "outputs": project.outputs,
    }


@app.websocket("/ws/{project_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: str):
    """WebSocket endpoint for real-time communication"""

    # Verify project exists
    async with websocket_manager.get_db_session() as db:
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()

        if not project:
            await websocket.close(code=4004, reason="Project not found")
            return

    await websocket_manager.connect(websocket, project_id)

    # Start agent analysis when connection is established
    agent = AnalysisAgent(project_id, websocket_manager)
    await agent.start_initial_analysis()

    try:
        while True:
            # Receive message from client
            try:
                message = await websocket.receive_text()
                data = json.loads(message)
            except json.JSONDecodeError as e:
                await websocket.send_json(
                    {"type": "error", "message": f"Invalid JSON format: {str(e)}"}
                )
                continue
            except Exception as e:
                await websocket.send_json(
                    {"type": "error", "message": f"Error receiving message: {str(e)}"}
                )
                continue

            # Handle different message types
            try:
                if data.get("type") == "slide_update":
                    await handle_slide_update(project_id, data, agent)
                elif data.get("type") == "chat_query":
                    await handle_chat_query(project_id, data, websocket)
                else:
                    await websocket.send_json(
                        {
                            "type": "error",
                            "message": f"Unknown message type: {data.get('type', 'missing')}",
                        }
                    )
            except Exception as e:
                await websocket.send_json(
                    {"type": "error", "message": f"Error processing message: {str(e)}"}
                )

    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, project_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        websocket_manager.disconnect(websocket, project_id)


async def handle_slide_update(project_id: str, data: dict, agent: AnalysisAgent):
    """Handle slide update from client"""
    try:
        slide_number = data.get("slide_number")
        user_fields_data = data.get("user_modified_fields", [])

        # Convert to SlideFieldSelection objects
        user_fields = [SlideFieldSelection(**field) for field in user_fields_data]

        # Process the slide update through agent
        await agent.process_slide_update(slide_number, user_fields)

    except Exception as e:
        await websocket_manager.send_to_project(
            project_id,
            {"type": "error", "message": f"Failed to process slide update: {str(e)}"},
        )


async def handle_chat_query(project_id: str, data: dict, websocket: WebSocket):
    """Handle chat queries for RAG"""
    try:
        async with async_session() as session:
            # Get project from database
            result = await session.execute(select(Project).where(Project.id == project_id))
            project = result.scalar_one_or_none()
            
            if not project:
                await websocket.send_json({
                    "type": "error",
                    "message": "Project not found"
                })
                return

            # Mock RAG response (in production, integrate with LLM)
            query = data.get("message", "")

            # Simulate processing time
            await asyncio.sleep(1)

            response = f"Based on your analysis of {project.name}, regarding '{query}': This is a mock response. In production, this would query the RAG system with your slide content and data."

            await websocket.send_json(
                {
                    "type": "chat_response",
                    "message": response,
                    "sources": ["slide_1", "original_data"],
                    "suggested_actions": [
                        "Generate deep-dive analysis",
                        "Create additional slides",
                        "Export findings to report",
                    ],
                }
            )
    except Exception as e:
        await websocket.send_json({
            "type": "error", 
            "message": f"Failed to process chat query: {str(e)}"
        })


async def get_data_preview(file_path: str) -> List[Dict]:
    """Get preview of CSV data"""
    try:
        df = pd.read_csv(file_path)
        return df.head(5).to_dict("records")
    except Exception:
        return []


@app.get("/downloads/{project_id}/{filename}")
async def download_file(project_id: str, filename: str):
    """Download generated files"""
    file_path = Path(f"downloads/{project_id}/{filename}")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path, filename=filename, media_type="application/octet-stream"
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
