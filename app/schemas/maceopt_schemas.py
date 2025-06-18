# app/schemas/maceopt_schemas.py
from pydantic import BaseModel
from typing import Optional

class MaceoptOptimizeResponse(BaseModel):
    """
    Defines the JSON response from the MACEOPT /optimize endpoint.
    We assume it returns a JSON object containing the path to the output file.
    """
    output_path: str
    message: Optional[str] = None