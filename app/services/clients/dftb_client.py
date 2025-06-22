# app/services/clients/dftb_client.py
# This module contains the low-level client for the new DFTB+ Automation Service API.
# It makes a single API call and validates the response against the raw API schema.
# Author: Shibo Li
# Date: 2025-06-22
# Version: 1.0.0

import httpx
import os
from typing import Optional

from app.core.logger import console
from app.schemas.dftb_api_schemas import RawDFTBOptimizeResponse

class DFTBClient:
    """A low-level client for the DFTB+ Automation Service."""

    def __init__(self, base_url: str):
        if not base_url:
            raise ValueError("DFTB+ API base URL cannot be empty.")
        self.base_url = f"{base_url.rstrip('/')}/api/v1"
        self.client = httpx.Client(base_url=self.base_url, timeout=600.0)

    def optimize(self, input_path: str, fmax: float, method: str) -> Optional[RawDFTBOptimizeResponse]:
        """
        Submits an optimization job and returns the raw, validated API response object.

        Args:
            input_path: The absolute path to the source CIF file.
            fmax: Force convergence threshold.
            method: GFN-xTB method to use.

        Returns:
            An instance of RawDFTBOptimizeResponse if successful, otherwise None.
        """
        console.info(f"[DFTBClient] Starting DFTB+ optimization for {os.path.basename(input_path)}...")
        try:
            if not os.path.exists(input_path):
                console.error(f"[DFTBClient] Input file not found: {input_path}")
                return None
            
            with open(input_path, "rb") as f:
                files = {"input_file": (os.path.basename(input_path), f)}
                data = {"fmax": str(fmax), "method": method}
                
                console.info(f"[DFTBClient] Calling POST /optimize/...")
                response = self.client.post("/optimize/", files=files, data=data)
                response.raise_for_status()

                # we expect the response to match the RawDFTBOptimizeResponse schema
                console.info(f"[DFTBClient] Received response with status code {response.status_code}. Validating response...")
                response_data = RawDFTBOptimizeResponse.model_validate(response.json())
                
                if response_data.status != "success":
                    console.error(f"[DFTBClient] API reported a failure: {response_data.detailed_results}")
                    return None

                console.success(f"[DFTBClient] Optimization API call successful. Request ID: {response_data.request_id}")
                return response_data

        except httpx.HTTPStatusError as e:
            console.error(f"[DFTBClient] HTTP error during optimization: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            console.exception(f"[DFTBClient] An unexpected error occurred in optimize(): {e}")
        
        return None