# app/services/clients/zeo_client.py
# The module provides a low-level client for interacting with the Zeo++ Analysis API.
# It includes methods for calculating pore diameter, surface area, accessible volume,
# probe volume, and channel analysis using the Zeo++ API endpoints.
# Author: Shibo Li
# Date: 2025-06-17
# Version: 0.1.0


import httpx
import os
from typing import Optional, Dict, Any
from app.schemas.zeo_schemas import (
    PoreDiameterResponse, SurfaceAreaResponse, AccessibleVolumeResponse,
    ProbeVolumeResponse, ChannelAnalysisResponse
)
from app.core.logger import console

class ZeoPlusPlusClient:
    """
    A low-level client for interacting with the Zeo++ Analysis API.
    Attributes:
        base_url (str): The base URL for the Zeo++ API.
        client (httpx.Client): The HTTP client for making requests to the API.
    """

    def __init__(self, base_url: str):
        if not base_url:
            raise ValueError("Zeo++ API base URL cannot be empty.")
            console.error("Zeo++ API base URL cannot be empty.")
        self.base_url = base_url
        self.client = httpx.Client(base_url=self.base_url, timeout=300.0)

    def _call_api(self, endpoint: str, file_path: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Generic method to call a multipart/form-data endpoint."""
        if not os.path.exists(file_path):
            console.error(f"[ZeoClient] File not found at path: {file_path}")
            return None

        try:
            with open(file_path, "rb") as f:
                files = {"structure_file": (os.path.basename(file_path), f, "application/octet-stream")}
                data = {k: str(v) for k, v in params.items() if v is not None} if params else None
                
                console.info(f"[ZeoClient] Calling endpoint: {self.base_url}{endpoint} for file: {os.path.basename(file_path)}")
                response = self.client.post(endpoint, files=files, data=data)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            console.error(f"[ZeoClient] HTTP error for {endpoint}: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            console.exception(f"[ZeoClient] An unexpected error in _call_api for {endpoint}: {e}")
            return None

    def calculate_pore_diameter(self, input_file_path: str, ha: bool) -> Optional[PoreDiameterResponse]:
        console.info(f"[ZeoClient] Calculating pore diameter for file: {input_file_path} with ha={ha}")
        params = {"ha": ha}
        response_data = self._call_api("/api/pore_diameter", input_file_path, params)
        console.info(f"[ZeoClient] Pore diameter calculation response: {response_data}")
        return PoreDiameterResponse.model_validate(response_data) if response_data else None

    def calculate_surface_area(self, input_file_path: str, chan_radius: float, probe_radius: float, samples: int, ha: bool) -> Optional[SurfaceAreaResponse]:
        console.info(f"[ZeoClient] Calculating surface area for file: {input_file_path} with chan_radius={chan_radius}, probe_radius={probe_radius}, samples={samples}, ha={ha}")
        params = {"chan_radius": chan_radius, "probe_radius": probe_radius, "samples": samples, "ha": ha}
        response_data = self._call_api("/api/surface_area", input_file_path, params)
        console.info(f"[ZeoClient] Surface area calculation response: {response_data}")
        return SurfaceAreaResponse.model_validate(response_data) if response_data else None

    def calculate_accessible_volume(self, input_file_path: str, chan_radius: float, probe_radius: float, samples: int, ha: bool) -> Optional[AccessibleVolumeResponse]:
        console.info(f"[ZeoClient] Calculating accessible volume for file: {input_file_path} with chan_radius={chan_radius}, probe_radius={probe_radius}, samples={samples}, ha={ha}")
        params = {"chan_radius": chan_radius, "probe_radius": probe_radius, "samples": samples, "ha": ha}
        response_data = self._call_api("/api/accessible_volume", input_file_path, params)
        console.info(f"[ZeoClient] Accessible volume calculation response: {response_data}")
        return AccessibleVolumeResponse.model_validate(response_data) if response_data else None

    def calculate_probe_volume(self, input_file_path: str, chan_radius: float, probe_radius: float, samples: int, ha: bool) -> Optional[ProbeVolumeResponse]:
        console.info(f"[ZeoClient] Calculating probe volume for file: {input_file_path} with chan_radius={chan_radius}, probe_radius={probe_radius}, samples={samples}, ha={ha}")
        params = {"chan_radius": chan_radius, "probe_radius": probe_radius, "samples": samples, "ha": ha}
        response_data = self._call_api("/api/probe_volume", input_file_path, params)
        console.info(f"[ZeoClient] Probe volume calculation response: {response_data}")
        return ProbeVolumeResponse.model_validate(response_data) if response_data else None

    def analyze_channels(self, input_file_path: str, probe_radius: float, ha: bool) -> Optional[ChannelAnalysisResponse]:
        console.info(f"[ZeoClient] Analyzing channels for file: {input_file_path} with probe_radius={probe_radius}, ha={ha}")
        params = {"probe_radius": probe_radius, "ha": ha}
        response_data = self._call_api("/api/channel_analysis", input_file_path, params)
        console.info(f"[ZeoClient] Channel analysis response: {response_data}")
        return ChannelAnalysisResponse.model_validate(response_data) if response_data else None