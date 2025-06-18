# app/schemas/converter_schemas.py
# The module defines Pydantic models for the File Converter API responses.
# Author: Shibo Li
# Date: 2025-06-17
# Version: 0.1.0

from pydantic import BaseModel
from typing import Optional

class ConverterResponse(BaseModel):
    """
    Defines the JSON response from the File Converter API.
    It returns the status and the path to the newly created file.
    """
    status: str
    output_path: str
    message: Optional[str] = None