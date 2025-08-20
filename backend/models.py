from pydantic import BaseModel
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime

class ProjectStatus(Enum):
    INITIALIZED = "initialized"
    WAITING_FOR_HUMAN = "waiting_for_human"
    PROCESSING = "processing"
    DATA_READY = "data_ready"
    PPT_READY = "ppt_ready"
    COMPLETED = "completed"
    FAILED = "failed"

class FieldConfig(BaseModel):
    field_name: str
    selected: bool
    analysis_type: Optional[str] = "basic"
    chart_type: Optional[str] = "auto"
    focus: Optional[str] = None

class SlideInfo(BaseModel):
    slide_number: int
    slide_title: str
    slide_content: Optional[str] = None
    fields_included: List[str]
    analysis_type: str
    thumbnail_url: Optional[str] = None
    generated_at: str

class ProjectOutput(BaseModel):
    output_type: str  # "file", "table", "markdown"
    content: Any
    url: Optional[str] = None
    generated_at: str

class Project(BaseModel):
    id: str
    name: str
    auto: bool
    status: ProjectStatus
    files: Dict[str, str]  # file paths
    available_fields: List[str]
    field_config: Optional[Dict[str, FieldConfig]] = None
    slides: List[SlideInfo] = []
    outputs: List[ProjectOutput] = []
    created_at: str
    last_run: Optional[str] = None
    
    class Config:
        use_enum_values = True 