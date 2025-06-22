# app/schemas/dftb_api_schemas.py
# This module defines the Pydantic models that EXACTLY match the raw response
# from the external DFTB+ API. This acts as the first layer of validation
# for incoming external data.
# Author: Shibo Li
# Date: 2025-06-22
# Version: 1.0.0

from pydantic import BaseModel, Field
from typing import Dict, Any

class RawDFTBInputParameters(BaseModel):
    """Mirrors the 'input_parameters' object in the API response."""
    fmax_eV_A: float = Field(..., alias="fmax")
    method: str
    
    class Config:
        extra = 'allow'
        populate_by_name = True

class RawDFTBOptimizeResponse(BaseModel):
    """
    Mirrors the exact structure of the JSON response from the DFTB+ API.
    """
    status: str
    request_id: str
    input_parameters: RawDFTBInputParameters
    detailed_results: Dict[str, Any]
    optimized_structure_cif_b64: str
    
    class Config:
        extra = 'allow'