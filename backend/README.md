# Expert Sure Backend

Intelligent Reporting Agent Backend - Insurance Actuarial Analysis

## Features

- ✅ Project Management API
- ✅ File Upload (CSV, JSON, PPTX/PPTM)
- ✅ Real-time WebSocket Communication
- ✅ AI Agent Processing for Insurance Data
- ✅ Automatic Slide Generation
- ✅ PowerPoint File Creation (.pptm)
- ✅ Insurance Data Analysis with LoB filtering
- ✅ Reserve Analysis and OCL calculations
- ✅ RAG Chat Simulation

## Setup

1. **Install Dependencies**
```bash
cd backend
pip install -r requirements.txt
```

2. **Run the Server**
```bash
python main.py
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
  -F "data_source=@../sample_data.csv" \
  -F "schema=@../sample_schema.json" \
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
    "type": "slide_update",
    "slide_number": 1,
    "user_modified_fields": [
        {
            "row_label": "Property (LOB1)",
            "metric_fields": ["OCL"],
            "is_group_header": false,
            "aggregation": "sum",
            "filters": [{"field": "LoB_masked", "operator": "==", "value": 1}]
        }
    ]
}));
```

### 4. Monitor Real-time Updates
- Slide generation notifications
- Status updates
- PowerPoint file ready notifications
- Insurance data analysis results

## Insurance Data Structure

### Sample CSV Fields:
- **LoB_masked**: Line of Business (1-5)
- **AccidentYear**: Policy effective year
- **DevelopmentYear**: Years since accident
- **ActualIncurred**: Total incurred losses ($)
- **NominalReserves**: Nominal reserve value ($)
- **DiscountedReserves**: Present value reserves ($)
- **OCL**: Outstanding Claims Liability ($)
- **ChangeInOcl**: Change in OCL ($)
- **BusinessSegment**: Segment description

### Generated Analysis:
1. **Reserves Summary**: Total overview across all LoB
2. **Line of Business Breakdown**: Filtered analysis per LoB
3. **Reserve Development**: Detailed financial breakdown

### Features:
- Real actuarial calculations
- LoB filtering with operators
- Currency formatting for financial fields
- Group headers with spans_all_columns
- Professional PowerPoint generation

For production, replace mock processing with actual AI/ML services.