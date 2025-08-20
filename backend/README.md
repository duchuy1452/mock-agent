# Expert Sure Backend

Intelligent Reporting Agent Backend - Mock Implementation

## Features

- ✅ Project Management API
- ✅ File Upload (CSV, JSON, PPTX)
- ✅ Real-time WebSocket Communication
- ✅ Mock AI Agent Processing
- ✅ Automatic Slide Generation
- ✅ PowerPoint File Creation
- ✅ Enhanced Data Analysis
- ✅ Markdown Report Generation
- ✅ RAG Chat Simulation

## Setup

1. **Install Dependencies**
```bash
cd backend
pip install -r requirements.txt
```

2. **Run the Server**
```bash
python run.py
```

3. **Access API Documentation**
- Open browser: http://localhost:8000/docs
- Interactive API docs with test interface

## API Endpoints

### Projects
- `GET /api/projects` - List all projects
- `POST /api/projects` - Create new project with file uploads
- `GET /api/projects/{project_id}` - Get project details

### WebSocket
- `WS /ws/{project_id}` - Real-time communication

### Downloads
- `GET /downloads/{project_id}/{filename}` - Download generated files

## Usage Flow

### 1. Create Project
```bash
curl -X POST "http://localhost:8000/api/projects" \
  -F "name=IFRS RESERVING" \
  -F "auto=false" \
  -F "data_source=@../data.csv" \
  -F "schema=@../field.json" \
  -F "template=@../Template.pptm"
```

### 2. Connect WebSocket
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/{project_id}');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Status:', data.status, data.message);
};
```

### 3. Send Field Selection
```javascript
ws.send(JSON.stringify({
    "type": "field_selection",
    "field_config": {
        "A": {"selected": true, "analysis_type": "trend"},
        "C": {"selected": true, "analysis_type": "risk"}
    }
}));
```

### 4. Proceed with Processing
```javascript
ws.send(JSON.stringify({
    "type": "proceed_processing",
    "confirmed": true
}));
```

### 5. Monitor Real-time Updates
- Slide generation notifications
- Status updates
- File ready notifications
- Data analysis results

## Mock Agent Behavior

The agent simulates real processing with:
- **Field-based slide generation**
- **Cross-field correlation analysis**
- **Business intelligence insights**
- **Risk assessment**
- **Strategic recommendations**

## File Structure

```
backend/
├── main.py              # FastAPI application
├── models.py            # Data models
├── requirements.txt     # Dependencies
├── run.py              # Startup script
├── services/
│   ├── __init__.py
│   ├── agent.py        # Analysis agent
│   └── websocket_manager.py
├── uploads/            # User uploaded files
└── downloads/          # Generated outputs
```

## WebSocket Message Types

### From Client:
- `field_selection` - Field configuration
- `proceed_processing` - Start analysis
- `chat_query` - RAG questions

### From Server:
- `status_update` - Processing status
- `slide_generated` - Individual slide ready
- `outputs_ready` - Data/markdown ready
- `file_ready` - PowerPoint download
- `chat_response` - RAG answers

## Integration Notes

This backend is designed to integrate with:
- **Next.js Frontend** (CORS enabled)
- **Any WebSocket client**
- **File upload interfaces**
- **Real-time dashboards**

For production, replace mock processing with actual AI/ML services.

## Testing

Use the interactive API docs at http://localhost:8000/docs to test all endpoints.

---
*Built with FastAPI, WebSockets, and Python-PPTX* 