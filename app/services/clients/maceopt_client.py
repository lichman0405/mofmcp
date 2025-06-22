# app/services/clients/maceopt_client.py
# This module contains the updated low-level client for the MACEOPT API.
# It now handles the structured JSON response from the /optimize endpoint.
# Author: Shibo Li
# Date: 2025-06-22
# Version: 0.7.0

import httpx
import os
from typing import Optional

from app.core.logger import console
from app.schemas.maceopt_schemas import MaceoptOptimizeResponse

class MaceoptClient:
    """A low-level client for the updated MACEOPT Geometry Optimization API."""

    def __init__(self, base_url: str):
        if not base_url:
            raise ValueError("MACEOPT API base URL cannot be empty.")
        self.base_url = base_url
        self.client = httpx.Client(base_url=self.base_url, timeout=600.0)

    def optimize(self, input_path: str, fmax: float, device: str) -> Optional[MaceoptOptimizeResponse]:
        """
        Calls the /optimize endpoint and returns the full structured JSON response.
        """
        console.info(f"[MaceoptClient] Submitting optimization for {os.path.basename(input_path)}...")
        try:
            with open(input_path, "rb") as f:
                files = {"structure_file": (os.path.basename(input_path), f)}
                data = {"fmax": str(fmax), "device": device}
                
                response = self.client.post("/optimize", files=files, data=data)
                response.raise_for_status()
                
                response_data = MaceoptOptimizeResponse.model_validate(response.json())
                console.success("[MaceoptClient] Optimization task submitted and processed successfully.")
                return response_data
        except httpx.HTTPStatusError as e:
            console.error(f"[MaceoptClient] HTTP error during optimization submission: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            console.exception(f"[MaceoptClient] An unexpected error occurred in optimize(): {e}")
        return None

    def download_file(self, download_link: str) -> Optional[bytes]:
        """
        Downloads a file from a given path (e.g., from the download_links).
        """
        console.info(f"[MaceoptClient] Downloading file from link: {download_link}...")
        try:
            full_url = httpx.URL(self.base_url).join(download_link)
            response = self.client.get(full_url)
            response.raise_for_status()
            console.success(f"[MaceoptClient] File downloaded successfully ({len(response.content)} bytes).")
            return response.content
        except httpx.HTTPStatusError as e:
            console.error(f"[MaceoptClient] HTTP error during file download: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            console.exception(f"[MaceoptClient] An unexpected error occurred in download_file(): {e}")
        return None