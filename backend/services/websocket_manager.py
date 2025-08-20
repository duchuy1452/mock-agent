from fastapi import WebSocket
from typing import Dict, List
import json

class WebSocketManager:
    def __init__(self):
        # Store active connections per project
        self.connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, project_id: str):
        """Accept a new WebSocket connection for a project"""
        await websocket.accept()
        
        if project_id not in self.connections:
            self.connections[project_id] = []
        
        self.connections[project_id].append(websocket)
        
        # Send welcome message
        await websocket.send_json({
            "type": "connection_established",
            "project_id": project_id,
            "message": "WebSocket connection established"
        })
    
    def disconnect(self, websocket: WebSocket, project_id: str):
        """Remove a WebSocket connection"""
        if project_id in self.connections:
            if websocket in self.connections[project_id]:
                self.connections[project_id].remove(websocket)
            
            # Clean up empty project connections
            if not self.connections[project_id]:
                del self.connections[project_id]
    
    async def send_to_project(self, project_id: str, message: dict):
        """Send message to all connections for a specific project"""
        if project_id in self.connections:
            disconnected = []
            
            for websocket in self.connections[project_id]:
                try:
                    await websocket.send_json(message)
                except:
                    # Connection is dead, mark for removal
                    disconnected.append(websocket)
            
            # Clean up dead connections
            for ws in disconnected:
                self.disconnect(ws, project_id)
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        for project_id in self.connections:
            await self.send_to_project(project_id, message) 