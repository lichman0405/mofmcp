# app/schemas/zeo_schemas.py
# The module defines Pydantic models for the response schemas of various Zeo++ API endpoints.
# Author: Shibo Li
# Date: 2025-06-17
# Version: 0.1.0


from pydantic import BaseModel, Field
from typing import Dict, Any

class PoreDiameterResponse(BaseModel):
    """Defines the response schema for the /api/pore_diameter endpoint."""
    included_diameter: float = Field(..., description="Largest included sphere diameter (Df) in Angstroms.")
    free_diameter: float = Field(..., description="Largest free sphere diameter (Di) in Angstroms.")
    included_along_free: float = Field(..., description="Largest included sphere that can travel along the free sphere path in Angstroms.")
    cached: bool

class SurfaceAreaResponse(BaseModel):
    """Defines the response schema for the /api/surface_area endpoint."""
    asa_unitcell: float = Field(..., description="Accessible Surface Area in A^2/unitcell.")
    asa_volume: float = Field(..., description="Accessible Surface Area in m^2/cm^3.")
    asa_mass: float = Field(..., description="Accessible Surface Area in m^2/g.")
    nasa_unitcell: float = Field(..., description="Non-accessible Surface Area in A^2/unitcell.")
    nasa_volume: float = Field(..., description="Non-accessible Surface Area in m^2/cm^3.")
    nasa_mass: float = Field(..., description="Non-accessible Surface Area in m^2/g.")
    cached: bool

class AccessibleVolumeResponse(BaseModel):
    """Defines the response schema for the /api/accessible_volume endpoint."""
    unitcell_volume: float = Field(..., description="Unit cell volume in A^3.")
    density: float = Field(..., description="Framework density in g/cm^3.")
    av: Dict[str, Any] = Field(..., description="Accessible Volume details.")
    nav: Dict[str, Any] = Field(..., description="Non-accessible Volume details.")
    cached: bool

class ProbeVolumeResponse(BaseModel):
    """Defines the response schema for the /api/probe_volume endpoint."""
    poav_unitcell: float = Field(..., description="Probe-occupiable accessible volume in A^3/unitcell.")
    poav_fraction: float = Field(..., description="Probe-occupiable accessible volume fraction.")
    poav_mass: float = Field(..., description="Probe-occupiable accessible volume in cm^3/g.")
    ponav_unitcell: float = Field(..., description="Probe-occupiable non-accessible volume in A^3/unitcell.")
    ponav_fraction: float = Field(..., description="Probe-occupiable non-accessible volume fraction.")
    ponav_mass: float = Field(..., description="Probe-occupiable non-accessible volume in cm^3/g.")
    cached: bool

class ChannelAnalysisResponse(BaseModel):
    """Defines the response schema for the /api/channel_analysis endpoint."""
    dimension: int = Field(..., description="Dimensionality of the channel system (0, 1, 2, or 3).")
    included_diameter: float = Field(..., description="Largest included sphere diameter (Df) in Angstroms.")
    free_diameter: float = Field(..., description="Largest free sphere diameter (Di) in Angstroms.")
    included_along_free: float = Field(..., description="Largest included sphere that can travel along the free sphere path in Angstroms.")
    cached: bool