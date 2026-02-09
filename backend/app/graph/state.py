from typing import TypedDict, List, Dict, Any, Optional, Annotated
from operator import add

class GraphState(TypedDict):
    """
    Standardizes the state passed between LangGraph nodes.
    """
    # Inputs
    job_id: int
    source_path: str
    user_request: Dict[str, Any]  # {pacing, mood, ratio}
    
    # Analysis
    keyframe_data: Dict[str, Any]
    
    # Planning
    director_plan: Dict[str, Any]
    
    # Assets (Stage 1 & 2 Results)
    cuts: List[Dict[str, Any]]
    visual_effects: List[Dict[str, Any]]
    
    # Audio (Stage 3 Result)
    audio_tracks: List[Dict[str, Any]]
    
    # Metadata
    title: Optional[str]
    description: Optional[str]
    
    # Validation & QC
    validation_result: Optional[Dict[str, Any]]
    qc_result: Optional[Dict[str, Any]]
    retry_count: int
    
    # Execution
    errors: Annotated[List[str], add]
    tier: str  # "pro" or "standard"

