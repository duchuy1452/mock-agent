from pydantic import BaseModel
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid


class ProjectStatus(Enum):
    INITIALIZED = "initialized"
    AGENT_ANALYZING = "agent_analyzing"
    WAITING_FOR_USER = "waiting_for_user"
    SLIDE_PROCESSING = "slide_processing"
    PPT_UPDATING = "ppt_updating"
    COMPLETED = "completed"
    FAILED = "failed"


class SlideStatus(Enum):
    PENDING = "pending"
    AGENT_ANALYZED = "agent_analyzed"
    USER_MODIFIED = "user_modified"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class FieldItem(BaseModel):
    field_name: str
    description: Optional[str] = None
    type: str  # "numeric", "categorical", "date", etc.
    selected: bool = False
    rationale: Optional[str] = None


class SlideFieldSelection(BaseModel):
    row_label: str
    metric_fields: List[str]
    is_group_header: bool = False
    spans_all_columns: bool = False
    is_aggregate: bool = False
    filters: List[Dict] = []
    aggregation: str = "sum"
    rationale: Optional[str] = None
    component_rows: List[str] = []


class AgentAnalysisResult(BaseModel):
    slide_number: int
    slide_title: str
    selected_fields: List[SlideFieldSelection]
    rationale: str


class SlideRequest(BaseModel):
    slide_number: int
    user_modified_fields: List[SlideFieldSelection]


class ProjectCreateResponse(BaseModel):
    project_id: str
    websocket_url: str
    status: str


class TableRow(BaseModel):
    """
    Represents a row in the summary table for the slide.
    """

    cells: List[str]
    is_aggregate: bool = False
    spans_all_columns: bool = False
    if_total_what_row_labels: List[str] = []


class TableDefinition(BaseModel):
    """
    Represents the table structure for the slide, including headers and rows.
    """

    headers: List[str]
    rows: List[TableRow]
    position: str  # e.g. "top", "bottom"


class SlideCommentary(BaseModel):
    """
    Represents a commentary block for the slide.
    """

    text: str
    position: str  # e.g. "middle", "bottom"


class LLMSlideReader(BaseModel):
    """
    Data model for LLM-generated slide summary, including table and commentary.
    """

    slide_number: int
    slide_header: str
    tables: List[TableDefinition]
    commentary: List[SlideCommentary]
    complex_visuals: bool = False


class SlideAnalysisResponse(BaseModel):
    slide_number: int
    slide_title: str
    agent_selected_fields: List[SlideFieldSelection]
    all_available_fields: List[FieldItem]
    llm_slide_reader: LLMSlideReader
    status: str
