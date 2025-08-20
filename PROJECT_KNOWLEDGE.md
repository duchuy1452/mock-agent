# Expert Sure - Project Knowledge Base

## 📋 Project Overview

**Expert Sure** là một Intelligent Reporting Agent system được thiết kế để **tự động hóa quy trình báo cáo tài chính từ đầu đến cuối**. Hệ thống nhận input là data files và tự động tạo ra PowerPoint presentation với analysis insights.

### 🎯 Business Context
- **Target**: Financial services firms
- **Use Case**: Automated reporting pipeline
- **Value Proposition**: Transform manual PowerPoint creation process (hours) → Automated AI-generated reports (minutes)
- **Migration**: From existing Streamlit app → Next.js + Tailwind CSS

---

## 🖥️ User Interface Flow (5 Screens)

### **Screen 1: Dashboard/Project Management**
```
Purpose: Project overview và management
Layout:
┌─────────────────────────────────────────────────┐
│ LOGO  Expert Sure                     [🔔] [👤] │
│       Intelligent Reporting Agents              │
├─────────────────────────────────────────────────┤
│ 📁Projects │ NAME     │ AUTO  │ LAST RUN │ STATUS │
│ 📋Settings │ IFRS     │ ON    │ 1-Sep-25 │RUNNING │
│(Collap.)   │ Claims   │ OFF   │ 1-Aug-25 │SUCCESS │
│            │ ...      │ OFF   │ 1-Jul-25 │FAILED  │
│            │          │       │          │[+ NEW] │
└─────────────────────────────────────────────────┘

Features:
- Project list với status tracking
- Auto-scheduling toggle
- Historical run dates
- Quick project creation
```

### **Screen 2: Project Setup & File Upload**
```
Purpose: New project configuration và file uploads
Layout:
┌─────────────────────────────────────────────────┐
│ NAME*: [Text Input: "IFRS RESERVING"          ] │
│ AUTO : [Radio: ON]/[OFF] - DEFAULT              │
│ DATA SOURCE*: [File Upload Button + Preview]    │
│ SCHEMA*: [File Upload Button + Preview]         │
│ TEMPLATE: [File Upload Button + Preview]        │
│                                    [NEXT >]     │
└─────────────────────────────────────────────────┘

Required Files:
- DATA SOURCE (CSV): Raw data for analysis
- SCHEMA (JSON): Field definitions và metadata
- TEMPLATE (PPTX): Optional PowerPoint template

Validation:
- File type validation
- Schema structure validation
- Field mapping preview
```

### **Screen 3 + 4: Processing & Results (Single Scrollable Screen)**
```
Purpose: Field selection, real-time processing, và results display

UPPER SECTION (Screen 3 - Field Selection):
┌─────────────────────────────────────────────────┐
│PROJECT: IFRS RESERVING           [BACK]         │
│AGENTIC LOG: [ON]/OFF                            │
│→SLIDE1|SLIDE2|...                (tabs)         │
├─────────────────────────────────────────────────┤
│┌─────────────────────────┐    Status Timeline:  │
││ FIELD SELECTION UI      │    • STARTING        │
││ ☑️ Field A             │    • AGENT 1         │
││ ☑️ Field C             │    • WAITING FOR     │
││ ☑️ Total               │      HUMAN          │
││     [PROCEED]          │    • PROCESSING      │
│└─────────────────────────┘    • DATA READY     │
│┌─────────────────────────┐    • PPT READY      │
││ CSV DATA PREVIEW TABLE  │                     │
│└─────────────────────────┘                     │
│FILE READY (hyperlink)                          │
│X─X SCROLL BELOW X─X                            │
└─────────────────────────────────────────────────┘

LOWER SECTION (Screen 4 - Analysis Results):
┌─────────────────────────────────────────────────┐
│X─X SCROLL UP X─X               ANALYSIS OF      │
│                                CHANGE READY     │
│┌─────────────────────────┐                      │
││                         │                      │
││  CONTENT FROM .MD       │                      │
││  FILE (Analysis Report) │                      │
││                         │                      │
│└─────────────────────────┘                      │
│          [CHAT]                                 │
└─────────────────────────────────────────────────┘

Key Features:
- Field selection với analysis type options
- Real-time status updates via WebSocket
- Progressive slide generation tabs
- Enhanced CSV table display
- Markdown analysis report
- Download links for generated files
```

### **Screen 5: Interactive Chat với RAG**
```
Purpose: Interactive analysis với RAG system
Layout:
┌─────────────────────────────────────────────────┐
│PROJECT: IFRS RESERVING                    [⚙️]  │
│┌─────────────────────────┐    ┌─────────────────┐│
││                         │    │ Slide Preview   ││
││  CONTENT FROM           │    │ Navigator       ││
││  .MD FILE               │    │                 ││
││                         │    │ ▬▬▬▬▬▬▬▬▬▬▬    ││
│└─────────────────────────┘    │ ▬▬▬▬▬▬▬▬▬▬▬    ││
│          [CHAT] →              │ ▬▬▬▬▬▬▬▬▬▬▬    ││
│                                │        🎯       ││
└─────────────────────────────────────────────────┘

Features:
- Split layout: Content + Slide navigator
- Interactive chat interface
- RAG-powered Q&A về analysis
- Slide thumbnail previews
- Context-aware responses
```

---

## 🤖 Agent Architecture & Behavior

### **Analysis Agent Workflow**
```python
class AnalysisAgent:
    def start_analysis():
        1. Load data (CSV) + schema (JSON)
        2. Analyze field configuration from user selection
        3. Determine slide plan (intelligent logic)
        4. Generate slides incrementally
        5. Compile PowerPoint file
        6. Generate additional outputs (CSV, Markdown)
        7. Enable RAG chat capability
```

### **Slide Generation Logic**
**NOT 1 field = 1 slide**. Agent intelligently determines slide count based on:

```
Input: Selected fields + Analysis context
Agent Logic:
├── Always: Executive Summary slide
├── Per Field: Detailed analysis (if complex)
├── Cross-Field: Correlation analysis (if multiple fields)
├── Business: Risk assessment, recommendations
└── Total: 4-12 slides depending on data complexity

Examples:
Simple case (2 fields, 4 data points) → 4-6 slides
Complex case (5 fields, 100+ data points) → 8-12 slides
Financial context (IFRS) → Specialized compliance slides
```

### **Real-time Processing Flow**
```
Field Selection → [PROCEED] → Agent starts:
├── PROCESSING: "Starting analysis agent..."
├── PROCESSING: "Planning complete. Generating 6 slides..."
├── SLIDE_1_READY: "Executive Summary"
├── SLIDE_2_READY: "Field A Analysis"
├── SLIDE_3_READY: "Correlation Analysis"
├── DATA_READY: "Analysis complete. Generating outputs..."
├── PPT_READY: "PowerPoint compilation complete"
└── Download link available
```

---

## 🧠 RAG System Integration

### **RAG Architecture**
```
Generated Content → Vector Database:
├── Slide content (text, insights)
├── Original data (CSV)
├── Analysis metadata
├── Business context
└── Statistical results

Query Process:
User Question → RAG retrieval → Context + LLM → Response
```

### **RAG Capabilities**
```javascript
// Chat Examples:
"Explain the trend in slide 3" 
→ RAG analyzes slide 3 content + original data

"Why is Field C showing high risk?"
→ RAG correlates risk factors from analysis

"Generate additional slides for competitor analysis"
→ RAG suggests new analysis directions

"Create deep-dive analysis for outliers"
→ RAG identifies data patterns and recommends actions
```

### **RAG Data Sources**
1. **Generated slides** - Content và insights
2. **Original data** - Raw CSV data
3. **Analysis metadata** - Statistical results
4. **Business context** - Domain-specific knowledge
5. **External knowledge** - Industry benchmarks (potential)

---

## 🔄 Input/Output Flow

### **Input Requirements**
```
Required Files:
├── data.csv (Sample: A,B,C,Total with 4 rows)
├── field.json (Sample: {"A": "Field A", "B": "Field B"...})
└── Template.pptm (Optional PowerPoint template)

User Selections:
├── Project name
├── Field selection (which columns to analyze)
├── Analysis type (comprehensive, focused, etc.)
└── Processing confirmation
```

### **Output Deliverables**
```
1. PowerPoint File (.pptx)
   ├── File size: 2-5MB
   ├── Slides: 4-12 slides dynamically generated
   ├── Content: Analysis, charts, recommendations
   └── Download: Direct link

2. Enhanced CSV Table
   ├── Original data + analysis columns
   ├── Trend indicators (↗ Growing, etc.)
   ├── Risk levels (Low, Medium, High)
   └── Statistical enhancements

3. Markdown Analysis Report
   ├── Executive summary
   ├── Statistical insights
   ├── Risk assessment
   ├── Strategic recommendations
   └── Technical details

4. Interactive Elements
   ├── Real-time status updates
   ├── Slide preview tabs
   ├── RAG chat interface
   └── Download management
```

---

## 🛠️ Technical Implementation

### **Backend Architecture (FastAPI)**
```
backend/
├── main.py                 # FastAPI app với CORS
├── models.py               # Pydantic data models
├── services/
│   ├── agent.py           # Mock AI agent logic
│   └── websocket_manager.py # WebSocket handling
├── uploads/               # User file storage
└── downloads/             # Generated outputs
```

### **API Endpoints**
```
REST APIs:
├── POST /api/projects      # Create project với file uploads
├── GET /api/projects       # List all projects
├── GET /api/projects/{id}  # Get project details
└── GET /downloads/{id}/{file} # Download generated files

WebSocket:
└── WS /ws/{project_id}     # Real-time bi-directional communication
```

### **WebSocket Message Types**
```
Client → Server:
├── field_selection: Field configuration
├── proceed_processing: Start analysis command
└── chat_query: RAG questions

Server → Client:
├── status_update: Processing progress
├── slide_generated: Individual slide ready
├── outputs_ready: Data/markdown complete
├── file_ready: PowerPoint download available
└── chat_response: RAG answers với suggestions
```

### **Data Flow**
```
1. File Upload → Validation → Project Creation
2. Field Selection → Agent Planning → Slide Generation
3. Real-time Updates → Progressive Results → Final Compilation
4. Multiple Outputs → Download Links → RAG Indexing
5. Interactive Chat → Context Retrieval → Intelligent Responses
```

---

## 🎯 Key Features & Innovations

### **Intelligent Slide Generation**
- Dynamic slide count based on data complexity
- Business context awareness (IFRS, Claims, etc.)
- Cross-field correlation analysis
- Professional presentation structure

### **Real-time Processing**
- WebSocket-based status updates
- Progressive slide preview
- Human-in-the-loop confirmation
- Async processing với visual feedback

### **Multi-format Outputs**
- PowerPoint for presentations
- Enhanced CSV for data analysis
- Markdown for detailed reporting
- Interactive chat for exploration

### **RAG-powered Insights**
- Context-aware question answering
- Slide content retrieval
- Additional analysis suggestions
- Business intelligence recommendations

---

## 🔧 Technical Stack

```
Frontend (Planned): Next.js + Tailwind CSS + WebSocket client
Backend (Implemented): FastAPI + WebSocket + Python-PPTX
Data Processing: Pandas + JSON schema validation
File Handling: Multipart uploads + Static file serving
Real-time: WebSocket bi-directional communication
AI/RAG (Mock): Simulated với expansion points for real LLM integration
```

---

## 🚀 Current Status

✅ **Backend Complete**: Full FastAPI implementation  
✅ **Mock Agent**: Realistic slide generation simulation  
✅ **WebSocket**: Real-time bi-directional communication  
✅ **File Processing**: Upload/download handling  
✅ **RAG Simulation**: Chat interface với mock responses  

🔄 **Next Phase**: Frontend development với Next.js  
🔄 **Future**: Real AI/LLM integration replacing mock agent  

---

## 💡 Business Value Proposition

**Traditional Process:**
```
Data → Manual Analysis (hours) → Manual PowerPoint Creation (hours) → Review → Delivery
```

**Expert Sure Process:**
```
Data Upload → Field Selection → Automated Analysis (minutes) → Generated Presentation → Interactive Q&A
```

**ROI Impact:**
- **Time Reduction**: Hours → Minutes
- **Consistency**: Standardized analysis methodology
- **Scalability**: Handle multiple reports simultaneously
- **Intelligence**: AI-powered insights beyond manual analysis
- **Interactivity**: RAG-enabled exploration của results

---

*This document serves as comprehensive context for further AI analysis and development planning.* 