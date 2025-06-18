# app/schemas/tool_schemas.py
# The module defines Pydantic models for input parameters of various tools in the application.
# Author: Shibo Li
# Date: 2025-06-17
# Version: 0.1.0

from pydantic import BaseModel, Field
from typing import Literal

# MACEOPT Optimization Tool Input Schema
class MaceoptToolInput(BaseModel):
    input_file_path: str = Field(..., description="The absolute path to the source structure file that needs to be optimized.")
    fmax: float = Field(0.1, description="Force tolerance for the BFGS optimizer.")
    device: str = Field("cpu", description="The device to run MACE on, can be 'cpu' or 'cuda'.")

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

# File Converter Tool Input Schema
class FileConverterInput(BaseModel):
    input_file_path: str = Field(..., description="The absolute path to the source structure file that needs to be converted.")
    target_format: Literal["xyz", "cif"] = Field(..., description="The desired output file format. Can be 'xyz' or 'cif'.")

# xTB Tool Input Schema
class XTBToolInput(BaseModel):
    """
    Defines the input parameters for the xTB geometry optimization tool.
    Note: This tool strictly requires an .xyz file as input.
    """
    input_file_path: str = Field(..., description="The absolute path to the .xyz structure file.")
    charge: int = Field(0, description="Total charge of the system.")
    uhf: int = Field(0, description="Number of unpaired electrons for unrestricted Hartree-Fock calculations.")
    gfn: Literal[0, 1, 2] = Field(2, description="The GFN-xTB version to use (0, 1, or 2).")
