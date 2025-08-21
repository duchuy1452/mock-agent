# WebSocket Messages - Expert Sure API

## 🔄 **Enhanced Flow:**

1. **Client creates a project** → Receives WebSocket URL
2. **Client connects to WebSocket** → Agent auto-analyzes data
3. **Agent generates complete PowerPoint** → Client receives download URL
4. **Client edits fields** → Client sends slide update
5. **Agent regenerates entire PowerPoint** → Client gets updated file with all slides

---

## 📤 **Messages from Client to Backend**

### 1. Slide Update (When the user edits fields for a slide)
```json
{
  "type": "slide_update",
  "slide_number": 1,
  "user_modified_fields": [
    {
      "row_label": "Total Revenue",
      "metric_fields": ["sales_amount"],
      "is_group_header": false,
      "aggregation": "sum",
      "rationale": "Primary metric for measuring revenue"
    },
    {
      "row_label": "Revenue by Region", 
      "metric_fields": ["sales_amount", "region"],
      "is_group_header": true,
      "aggregation": "sum",
      "rationale": "Analyze geographic distribution"
    }
  ]
}
```

### 2. Chat Query (RAG)
```json
{
  "type": "chat_query",
  "message": "Which region has the best sales trend?",
  "context": "slide_analysis"
}
```

---

## 📥 **Messages from Backend to Client**

### 1. Connection Established
```json
{
  "type": "connection_established",
  "project_id": "uuid-here",
  "message": "WebSocket connection established"
}
```

### 2. Agent Analysis Status
```json
{
  "type": "status_update",
  "status": "AGENT_ANALYZING",
  "message": "Agent is analyzing your data...",
  "progress": 30
}
```

### 3. Slide Analysis Results (Agent sends results for each slide)
```json
{
  "type": "slide_analysis",
  "slide_number": 1,
  "slide_title": "Executive Summary",
  "agent_selected_fields": [
    {
      "row_label": "Total Revenue",
      "metric_fields": ["sales_amount"],
      "is_group_header": false,
      "aggregation": "sum",
      "rationale": "Key metric for the overview"
    }
  ],
  "all_available_fields": [
    {
      "field_name": "sales_amount",
      "description": "Total sales revenue",
      "type": "numeric"
    },
    {
      "field_name": "region",
      "description": "Sales region",
      "type": "categorical"
    }
  ],
  "rationale": "Overview slide showing key KPIs",
  "status": "agent_analyzed"
}
```

### 4. PowerPoint Generation Status
```json
{
  "type": "status_update",
  "status": "GENERATING_POWERPOINT",
  "message": "Generating PowerPoint presentation...",
  "progress": 80
}
```

### 5. PowerPoint Ready
```json
{
  "type": "powerpoint_ready",
  "download_url": "/downloads/project-id/analysis_report.pptm",
  "message": "Complete PowerPoint presentation is ready for download"
}
```

### 6. Waiting for User
```json
{
  "type": "status_update", 
  "status": "WAITING_FOR_USER",
  "message": "Analysis complete. PowerPoint ready. Please review and modify slides as needed.",
  "progress": 100
}
```

### 7. Slide Processing
```json
{
  "type": "status_update",
  "status": "SLIDE_PROCESSING", 
  "message": "Processing slide 1...",
  "progress": 50
}
```

### 8. PowerPoint Update Status
```json
{
  "type": "status_update",
  "status": "UPDATING_POWERPOINT",
  "message": "Updating complete PowerPoint presentation...",
  "progress": 70
}
```

### 9. Slide Completed
```json
{
  "type": "slide_completed",
  "slide_number": 1,
  "status": "completed",
  "download_url": "/downloads/project-id/analysis_report.pptm",
  "message": "Complete PowerPoint presentation updated with all slides including slide 1 changes"
}
```

### 10. Chat Response (RAG)
```json
{
  "type": "chat_response",
  "message": "Based on the analysis:\n\n**North region** leads with $8,750 (32%)\n**West region** follows with $7,300 (26%)\n\nNorth region shows the highest growth potential.",
  "sources": ["slide_2_regional_analysis", "original_data"],
  "suggested_actions": [
    "Create detailed slide for North region analysis",
    "Compare performance by month",
    "Generate detailed report"
  ]
}
```

### 11. Error Messages
```json
{
  "type": "error",
  "message": "Slide processing error: Field 'sales_amount' not found in data"
}
```

---

## 🎯 **System Status States:**

- **`initialized`** - Project just created
- **`agent_analyzing`** - Agent is analyzing data
- **`generating_powerpoint`** - Generating complete PowerPoint presentation
- **`waiting_for_user`** - Waiting for user to edit fields
- **`slide_processing`** - Processing a specific slide
- **`updating_powerpoint`** - Updating complete PowerPoint with all slides
- **`completed`** - Slide processing completed

---

## 💡 **Usage Steps:**

1. **Create a project** via REST API → Receive WebSocket URL
2. **Connect to WebSocket** → Agent automatically analyzes data and generates complete PowerPoint
3. **Download initial PowerPoint** → Complete presentation ready with all slides
4. **Edit fields** → Send `slide_update` message for any slide
5. **Download updated PowerPoint** → Complete presentation regenerated with all slides updated

That's it! 🚀

## ✨ **Key Features:**

- **Complete PowerPoint Generation**: Initial analysis creates full presentation with all slides
- **Full Regeneration**: Any slide update regenerates the entire PowerPoint with all slides
- **Real-time Updates**: WebSocket provides live status updates during generation
- **Template Support**: Uses uploaded template or creates new presentation

## 📊 **Slide Table Structure:**

Each slide contains a table with the following structure:
- **Group Headers**: Rows that span all columns (like section titles)
- **Data Rows**: Rows with labels and calculated values
- **Values**: Aggregated data (sum, average, count) formatted appropriately

Example table content:
```json
{
  "slide_number": 1,
  "table_rows": [
    {
      "label": "Revenue Analysis",
      "is_group_header": true,
      "spans_all_columns": true,
      "values": {"header": "Revenue Analysis"}
    },
    {
      "label": "Total Revenue",
      "is_group_header": false,
      "values": {"sales_amount": "$27,750.00"}
    },
    {
      "label": "Total Units",
      "is_group_header": false,
      "values": {"units_sold": "439"}
    }
  ]
}
```

---

## 🌐 **WebSocket Connection Example:**

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/project-id');

ws.onopen = () => console.log('WebSocket connection opened');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};

// Send slide update
const slideUpdate = {
  type: "slide_update",
  slide_number: 1,
  user_modified_fields: [...]    
};
ws.send(JSON.stringify(slideUpdate));
```

---

## 🔧 **API Endpoints:**

### Create Project
```http
POST /api/projects
Content-Type: multipart/form-data

name: "Q1 Sales Analysis"
auto: false
data_source: sales_data.csv
schema: schema.json
template: template.pptm (optional)
```

### Response:
```json
{
  "project_id": "uuid-here",
  "websocket_url": "ws://localhost:8000/ws/uuid-here",
  "status": "initialized"
}
```

### List Projects
```http
GET /api/projects
```

### Download File
```http
GET /downloads/{project_id}/analysis_report.pptm
``` 