# app/schemas/dftb_schemas.py
# Defines Pydantic models for the DFTB+ Automation Service API response.
# Author: Shibo Li
# Date: 2025-06-22
# Version: 0.1.0

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class DFTBInputParameters(BaseModel):
    fmax: float
    method: str

class DFTBSummary(BaseModel):
    calculation_status: str
    convergence_status: str
    warnings: List[str]
    error: Optional[str] = None

class DFTBConvergenceInfo(BaseModel):
    scc_converged: bool

class DFTBDipoleMoment(BaseModel):
    x: float
    y: float
    z: float

class DFTBElectronicProperties(BaseModel):
    fermi_level_eV: float
    total_charge: float
    dipole_moment_debye: DFTBDipoleMoment

class DFTBOptimizeResponse(BaseModel):
    """
    Defines the successful response from the DFTB+ /api/v1/optimize/ endpoint.
    """
    status: str
    request_id: str
    input_parameters: DFTBInputParameters
    detailed_results: Dict[str, Any] 
    optimized_structure_cif_b64: str = Field(..., description="The optimized CIF file content, Base64 encoded.")