# app/services/clients/xtb_client.py
# This module contains the simplified low-level client for the xTB API.
# It makes a single call to get the optimized structure content directly.
# Author: Shibo Li
# Date: 2025-06-18
# Version: 0.2.0

import httpx
import os
from typing import Optional

from app.core.logger import console

class XTBClient:
    """A low-level client for the xTB Geometry Optimization API."""

    def __init__(self, base_url: str):
        if not base_url:
            raise ValueError("xTB API base URL cannot be empty.")
        self.base_url = base_url
        self.client = httpx.Client(base_url=self.base_url, timeout=600.0)

    def optimize(self, input_path: str, charge: int, uhf: int, gfn: int) -> Optional[bytes]:
        """
        Submits an optimization job to /optimize and returns the binary content
        of the optimized structure file directly from the response.

        Args:
            input_path (str): Path to the source .xyz file.
            ... (other params)

        Returns:
            Optional[bytes]: The binary content of the optimized .xyz file, or None on failure.
        """
        console.info(f"[XTBClient] Starting xTB optimization for {os.path.basename(input_path)}...")
        
        try:
            if not os.path.exists(input_path):
                console.error(f"[XTBClient] Input file not found: {input_path}")
                return None

            with open(input_path, "rb") as f:
                files = {"file": (os.path.basename(input_path), f, "application/octet-stream")}
                data = {"charge": str(charge), "uhf": str(uhf), "gfn": str(gfn)}
                
                console.info(f"[XTBClient] Calling POST /optimize...")
                response = self.client.post("/optimize", files=files, data=data)
                response.raise_for_status()

                console.success(f"[XTBClient] Optimization successful. Received {len(response.content)} bytes.")
                return response.content

        except Exception as e:
            console.exception(f"[XTBClient] An unexpected error occurred: {e}")
        
        return None