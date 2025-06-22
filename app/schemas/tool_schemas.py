# app/schemas/tool_schemas.py
# The module defines Pydantic models for input parameters of various tools in the application.
# Author: Shibo Li
# Date: 2025-06-17
# Version: 0.1.0

from pydantic import BaseModel, Field
from typing import Literal

# MACEOPT Optimization Tool Input Schema
class MaceoptToolInput(BaseModel):
    """
    Defines the input parameters for the MACEOPT optimization tool.
    """
    input_file_path: str = Field(..., description="The absolute path to the source structure file (e.g., .cif) to be optimized.")
    fmax: float = Field(0.1, description="Force tolerance for the BFGS optimizer.")
    device: str = Field("cpu", description="Device to run MACE on, can be 'cpu' or 'cuda'.")


# Zeo++ Analysis Tool Input Schemas
class ZeoPoreDiameterInput(BaseModel):
    input_file_path: str = Field(..., description="The absolute path to the structure file.")
    ha: bool = Field(True, description="Enable high accuracy mode.")

class ZeoSurfaceAreaInput(BaseModel):
    input_file_path: str = Field(..., description="The absolute path to the structure file.")
    chan_radius: float = Field(..., description="Channel radius in Angstroms.")
    probe_radius: float = Field(..., description="Radius of the probe molecule in Angstroms.")
    samples: int = Field(..., description="Number of Monte Carlo samples for integration.")
    ha: bool = Field(True, description="Enable high accuracy mode.")

class ZeoAccessibleVolumeInput(BaseModel):
    input_file_path: str = Field(..., description="The absolute path to the structure file.")
    chan_radius: float = Field(..., description="Channel radius in Angstroms.")
    probe_radius: float = Field(..., description="Radius of the probe molecule in Angstroms.")
    samples: int = Field(..., description="Number of Monte Carlo samples for integration.")
    ha: bool = Field(True, description="Enable high accuracy mode.")

class ZeoProbeVolumeInput(BaseModel):
    input_file_path: str = Field(..., description="The absolute path to the structure file.")
    chan_radius: float = Field(..., description="Channel radius in Angstroms.")
    probe_radius: float = Field(..., description="Radius of the probe molecule in Angstroms.")
    samples: int = Field(..., description="Number of Monte Carlo samples for integration.")
    ha: bool = Field(True, description="Enable high accuracy mode.")
    
class ZeoChannelAnalysisInput(BaseModel):
    input_file_path: str = Field(..., description="The absolute path to the structure file.")
    probe_radius: float = Field(..., description="Radius of the probe molecule in Angstroms.")
    ha: bool = Field(True, description="Enable high accuracy mode.")

class DFTBToolInput(BaseModel):
    """
    Defines the input parameters for the DFTB+ geometry optimization tool.
    """
    input_file_path: str = Field(..., description="The absolute path to the source CIF file.")
    fmax: float = Field(0.1, description="Force convergence threshold in eV/Angstrom.")
    method: Literal["GFN1-xTB", "GFN2-xTB"] = Field("GFN2-xTB", description="GFN-xTB method to use.")