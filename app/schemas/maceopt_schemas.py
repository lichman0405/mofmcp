# app/schemas/maceopt_schemas.py
# This module defines the Pydantic models for the MACEOPT API responses.
# Updated to match the new detailed JSON response.
# Author: Shibo Li
# Date: 2025-06-22
# Version: 0.1.0

from pydantic import BaseModel, Field
from typing import List, Optional

class DownloadLinks(BaseModel):
    cif: str
    extxyz: str

class Properties(BaseModel):
    numbers: str
    positions: str
    spacegroup_kinds: Optional[str] = None

class MaceoptOptimizeResponse(BaseModel):
    """
    Defines the successful response from the MACEOPT /optimize endpoint.
    """
    success: bool
    n_atoms: int = Field(..., alias="n_atoms")
    input_file: str
    output_file: str
    output_extxyz: str
    fmax: float
    device: str
    energy: float
    free_energy: float
    stress: List[float]
    pbc: List[bool]
    properties: Properties
    session: str
    download_links: DownloadLinks