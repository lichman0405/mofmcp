# app/schemas/api_schemas.py
# This module defines the Pydantic models for the public-facing API endpoints.
# It ensures the data returned to the client is structured and validated.
# Author: Shibo Li
# Date: 2025-06-18
# Version: 1.0.0

from pydantic import BaseModel
from typing import Optional, Dict, Any

class TaskCreationResponse(BaseModel):
    """
    The response returned to the user immediately after submitting a task.
    """
    message: str
    task_id: str

class TaskStatusResponse(BaseModel):
    """
    The detailed response when a user queries the status of a task.
    """
    task_id: str
    status: str
    llm_plan: Optional[Dict[str, Any]] = None
    execution_log: Optional[Dict[str, Any]] = None