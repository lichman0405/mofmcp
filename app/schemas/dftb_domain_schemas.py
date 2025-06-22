# app/schemas/dftb_domain_schemas.py
# Defines the clean, internal "domain" models for DFTB+ results.
# This is the data structure our agent's other components will interact with.
# Author: Shibo Li
# Date: 2025-06-22
# Version: 1.0.0

from pydantic import BaseModel
from typing import Dict, Any, Optional

class DFTBResult(BaseModel):
    """
    A clean, internal representation of a successful DFTB+ optimization result.
    This is the object that the DFTBTool will return to the AgentExecutor.
    """
    status: str
    output_file_path: str
    
    final_energy_eV: Optional[float] = None
    is_converged: Optional[bool] = None
    
    detailed_results: Dict[str, Any]