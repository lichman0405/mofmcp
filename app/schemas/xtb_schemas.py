# app/schemas/xtb_schemas.py
# The module defines Pydantic models for the xTB optimization tool's input and output schemas.
# Author: Shibo Li
# Date: 2025-06-17
# Version: 0.1.0

from pydantic import BaseModel
from typing import Optional

class XTBJobListResponse(BaseModel):
    job_ids: list[str]
    errors: list[str]


class XTBOptimizeResponse(BaseModel):
    """
    Defines the JSON response from the xTB /optimize endpoint.
    It returns a job_id for tracking the optimization task.
    """
    job_id: str
    message: Optional[str] = None