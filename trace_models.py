# trace_models.py
from pydantic import BaseModel
from typing import Any, List, Optional
from uuid import uuid4
from datetime import datetime

class TraceStep(BaseModel):
    index: int
    timestamp: datetime
    step_type: str
    input: Optional[Any] = None
    output: Optional[Any] = None
    error: Optional[str] = None
    meta: Optional[dict] = None

class AgentRun(BaseModel):
    run_id: str
    agent_type: str
    started_at: datetime
    user_id: str
    env_snapshot: dict
    steps: List[TraceStep]
