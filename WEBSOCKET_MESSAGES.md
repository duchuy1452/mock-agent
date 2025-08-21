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
      "row_label": "Total",
      "metric_fields": ["ActualIncurred", "NominalReserves", "DiscountedReserves"],
      "is_group_header": true,
      "spans_all_columns": true,
      "aggregation": "sum",
      "rationale": "Total reserves across all lines of business"
    },
    {
      "row_label": "Property (LOB1)", 
      "metric_fields": ["OCL"],
      "is_group_header": false,
      "aggregation": "sum",
      "filters": [{"field": "LoB_masked", "operator": "==", "value": 1}],
      "rationale": "Outstanding claims for Property line of business"
    }
  ]
}
```

### 2. Chat Query (RAG)
```json
{
  "type": "chat_query",
  "message": "Which line of business has the highest reserve development?",
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
  "slide_title": "Reserves Summary",
  "agent_selected_fields": [
    {
      "row_label": "Total",
      "metric_fields": ["ActualIncurred", "NominalReserves", "DiscountedReserves"],
      "is_group_header": true,
      "spans_all_columns": true,
      "is_aggregate": false,
      "filters": [],
      "aggregation": "sum",
      "rationale": "User override applied via HITL interface.",
      "component_rows": []
    },
    {
      "row_label": "Total Loss Component",
      "metric_fields": ["OCL"],
      "is_group_header": false,
      "spans_all_columns": false,
      "is_aggregate": true,
      "filters": [],
      "aggregation": "sum",
      "rationale": "User override applied via HITL interface.",
      "component_rows": ["LOB1", "LOB2", "LOB3", "LOB4", "LOB5"]
    }
  ],
  "all_available_fields": [
    {
      "field_name": "ActualIncurred",
      "description": "Total actual incurred losses",
      "type": "numeric"
    },
    {
      "field_name": "LoB_masked",
      "description": "Line of Business identifier",
      "type": "categorical"
    }
  ],
  "rationale": "High-level overview of reserve positions and claims liability",
  "status": "agent_analyzed",
  "data_preview": [
    {
      "LoB_masked": 1,
      "AccidentYear": 2019,
      "DevelopmentYear": 1,
      "ActualIncurred": 1250000,
      "NominalReserves": 980000,
      "DiscountedReserves": 950000,
      "OCL": 180000,
      "ChangeInOcl": 25000,
      "BusinessSegment": "Property"
    }
  ]
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
  "message": "Based on the analysis:\n\n**Casualty (LOB2)** leads with $1,050,000 OCL (32%)\n**Reinsurance (LOB5)** follows with $1,050,000 OCL (32%)\n\nCasualty shows the highest reserve volatility.",
  "sources": ["slide_2_lob_analysis", "original_data"],
  "suggested_actions": [
    "Create detailed slide for Casualty analysis",
    "Compare reserve development by accident year",
    "Generate detailed actuarial report"
  ]
}
```

### 11. Error Messages
```json
{
  "type": "error",
  "message": "Slide processing error: Field 'ActualIncurred' not found in data"
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
- **Data Preview**: Each slide includes calculated table preview with real data
- **Smart Formatting**: Automatic currency, percentage, and number formatting
- **Live Table Preview**: See exactly how the table will look before downloading

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
      "label": "Total",
      "is_group_header": true,
      "spans_all_columns": true,
      "values": {"header": "Total"}
    },
    {
      "label": "Outstanding Claims Liability",
      "is_group_header": false,
      "values": {"OCL": "$3,285,000"}
    },
    {
      "label": "Change in OCL",
      "is_group_header": false,
      "values": {"ChangeInOcl": "$615,000"}
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

name: "IFRS RESERVING"
auto: false
data_source: insurance_data.csv
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