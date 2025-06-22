# app/services/clients/dftb_client.py
# This module contains the low-level client for the DFTB+ Automation Service API.
# Author: Shibo Li
# Date: 2025-06-22
# Version: 1.0.0

import httpx
import os
from typing import Optional

from app.core.logger import console
from app.schemas.dftb_schemas import DFTBOptimizeResponse

class DFTBClient:
    """A low-level client for the DFTB+ Automation Service."""

    def __init__(self, base_url: str):
        if not base_url:
            raise ValueError("DFTB+ API base URL cannot be empty.")
        self.base_url = f"{base_url.rstrip('/')}/api/v1"
        self.client = httpx.Client(base_url=self.base_url, timeout=600.0)

    def optimize(self, input_path: str, fmax: float, method: str) -> Optional[DFTBOptimizeResponse]:
        """
        Submits an optimization job and returns the full JSON response containing
        all results and the Base64-encoded optimized structure.
        """
        console.info(f"[DFTBClient] Starting DFTB+ optimization for {os.path.basename(input_path)}...")
        try:
            with open(input_path, "rb") as f:
                files = {"input_file": (os.path.basename(input_path), f)}
                data = {"fmax": str(fmax), "method": method}
                
                console.info(f"[DFTBClient] Calling POST /optimize/...")
                response = self.client.post("/optimize/", files=files, data=data)
                response.raise_for_status()

                response_data = DFTBOptimizeResponse.model_validate(response.json())
                console.success(f"[DFTBClient] Optimization successful. Request ID: {response_data.request_id}")
                return response_data

        except Exception as e:
            console.exception(f"[DFTBClient] An unexpected error occurred: {e}")
        return None