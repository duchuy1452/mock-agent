from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Form, HTTPException
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

from models import Project, ProjectStatus, FieldConfig, SlideInfo
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
app.mount("/downloads", StaticFiles(directory="downloads"), name="downloads")

# Global storage (in production, use database)
projects_db: Dict[str, Project] = {}
websocket_manager = WebSocketManager()

@app.get("/")
async def root():
    return {"message": "Expert Sure API is running"}

@app.get("/api/projects")
async def get_projects():
    """Get all projects for dashboard"""
    return {
        "projects": [
            {
                "id": project.id,
                "name": project.name,
                "auto": project.auto,
                "last_run": project.last_run,
                "status": project.status.value,
                "created_at": project.created_at
            }
            for project in projects_db.values()
        ]
    }

@app.post("/api/projects")
async def create_project(
    name: str = Form(...),
    auto: bool = Form(False),
    data_source: UploadFile = File(...),
    schema: UploadFile = File(...),
    template: Optional[UploadFile] = File(None)
):
    """Create new project with file uploads"""
    
    # Validate file types
    if not data_source.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Data source must be CSV file")
    
    if not schema.filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="Schema must be JSON file")
    
    if template and not template.filename.endswith(('.pptx', '.pptm')):
        raise HTTPException(status_code=400, detail="Template must be PowerPoint file")
    
    # Create project ID
    project_id = str(uuid.uuid4())
    
    # Create project directory
    project_dir = Path(f"uploads/{project_id}")
    project_dir.mkdir(parents=True, exist_ok=True)
    
    # Save uploaded files
    files_saved = {}
    
    # Save data source
    data_path = project_dir / data_source.filename
    with open(data_path, "wb") as f:
        content = await data_source.read()
        f.write(content)
    files_saved["data_source"] = str(data_path)
    
    # Save schema
    schema_path = project_dir / schema.filename
    with open(schema_path, "wb") as f:
        content = await schema.read()
        f.write(content)
    files_saved["schema"] = str(schema_path)
    
    # Save template if provided
    if template:
        template_path = project_dir / template.filename
        with open(template_path, "wb") as f:
            content = await template.read()
            f.write(content)
        files_saved["template"] = str(template_path)
    
    # Parse schema to get available fields
    try:
        with open(schema_path, 'r') as f:
            schema_data = json.load(f)
        available_fields = list(schema_data.keys())
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid schema file: {str(e)}")
    
    # Create project object
    project = Project(
        id=project_id,
        name=name,
        auto=auto,
        status=ProjectStatus.INITIALIZED,
        files=files_saved,
        available_fields=available_fields,
        created_at=datetime.now().isoformat(),
        last_run=None
    )
    
    # Store in database
    projects_db[project_id] = project
    
    return {
        "project_id": project_id,
        "status": "initialized",
        "available_fields": available_fields,
        "websocket_url": f"ws://localhost:8000/ws/{project_id}"
    }

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
        "outputs": project.outputs
    }

@app.websocket("/ws/{project_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: str):
    """WebSocket endpoint for real-time communication"""
    
    if project_id not in projects_db:
        await websocket.close(code=4004, reason="Project not found")
        return
    
    await websocket_manager.connect(websocket, project_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            # Handle different message types
            if data["type"] == "field_selection":
                await handle_field_selection(project_id, data, websocket)
            elif data["type"] == "proceed_processing":
                await handle_proceed_processing(project_id, websocket)
            elif data["type"] == "chat_query":
                await handle_chat_query(project_id, data, websocket)
                
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, project_id)

async def handle_field_selection(project_id: str, data: dict, websocket: WebSocket):
    """Handle field selection from client"""
    project = projects_db[project_id]
    
    # Store field configuration
    project.field_config = data.get("field_config", {})
    project.status = ProjectStatus.WAITING_FOR_HUMAN
    
    # Send confirmation
    await websocket.send_json({
        "type": "status_update",
        "status": "WAITING_FOR_HUMAN",
        "message": "Field selection received. Click PROCEED to start analysis.",
        "data_preview": await get_data_preview(project.files["data_source"])
    })

async def handle_proceed_processing(project_id: str, websocket: WebSocket):
    """Handle proceed processing command"""
    project = projects_db[project_id]
    project.status = ProjectStatus.PROCESSING
    project.last_run = datetime.now().isoformat()
    
    # Create and start analysis agent
    agent = AnalysisAgent(project_id, websocket_manager)
    await agent.start_analysis(project)

async def handle_chat_query(project_id: str, data: dict, websocket: WebSocket):
    """Handle chat queries for RAG"""
    project = projects_db[project_id]
    
    # Mock RAG response (in production, integrate with LLM)
    query = data.get("message", "")
    
    # Simulate processing time
    await asyncio.sleep(1)
    
    response = f"Based on your analysis of {project.name}, regarding '{query}': This is a mock response. In production, this would query the RAG system with your slide content and data."
    
    await websocket.send_json({
        "type": "chat_response",
        "message": response,
        "sources": ["slide_1", "original_data"],
        "suggested_actions": [
            "Generate deep-dive analysis",
            "Create additional slides",
            "Export findings to report"
        ]
    })

async def get_data_preview(file_path: str) -> List[Dict]:
    """Get preview of CSV data"""
    try:
        df = pd.read_csv(file_path)
        return df.head(5).to_dict('records')
    except Exception:
        return []

@app.get("/downloads/{project_id}/{filename}")
async def download_file(project_id: str, filename: str):
    """Download generated files"""
    file_path = Path(f"downloads/{project_id}/{filename}")
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/octet-stream'
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 