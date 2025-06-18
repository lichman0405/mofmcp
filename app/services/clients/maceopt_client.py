# app/services/clients/maceopt_client.py
# The module provides a low-level client for interacting with the MACEOPT Geometry Optimization API.
# It includes methods for performing geometry optimization and downloading the optimized structure.
# Author: Shibo Li
# Date: 2025-06-17
# Version: 0.1.0


import httpx
import os

from app.core.logger import console
from app.schemas.maceopt_schemas import MaceoptOptimizeResponse

class MaceoptClient:
    """A low-level client for the MACEOPT Geometry Optimization API."""

    def __init__(self, base_url: str):
        if not base_url:
            raise ValueError("MACEOPT API base URL cannot be empty.")
        self.base_url = base_url
        self.client = httpx.Client(base_url=self.base_url, timeout=600.0) 

    def optimize_and_save(self, input_path: str, output_path: str, fmax: float, device: str) -> bool:
        """
        Performs geometry optimization by calling /optimize and then /download.
        Saves the optimized structure to the specified output_path.

        Returns:
            bool: True if the entire process was successful, False otherwise.
        """
        console.info(f"[MaceoptClient] Starting optimization for {os.path.basename(input_path)}...")
        
        try:
            # check if input file exists
            if not os.path.exists(input_path):
                console.error(f"[MaceoptClient] Input file not found: {input_path}")
                return False

            with open(input_path, "rb") as f:
                files = {"structure_file": (os.path.basename(input_path), f, "application/octet-stream")}
                data = {"fmax": str(fmax), "device": device}
                
                console.info(f"[MaceoptClient] Calling POST /optimize...")
                optimize_response = self.client.post("/optimize", files=files, data=data)
                optimize_response.raise_for_status()

                # parse the response, feedback the path of optimized structure
                console.info("[MaceoptClient] Parsing optimization response...")
                path_data = MaceoptOptimizeResponse.model_validate(optimize_response.json())
                server_path = path_data.output_path
                
                if not server_path:
                    console.error("[MaceoptClient] /optimize did not return a valid output path.")
                    return False
                
                console.success(f"[MaceoptClient] Optimization task completed. Server path: {server_path}")

            # download the optimized structure from the server
            console.info(f"[MaceoptClient] Calling GET /download for path: {server_path}...")
            params = {"path": server_path}
            download_response = self.client.get("/download", params=params)
            download_response.raise_for_status()

            # save the downloaded content to the specified output path, temperately.
            with open(output_path, "wb") as f_out:
                f_out.write(download_response.content)
            
            console.success(f"[MaceoptClient] Optimized structure saved to: {output_path}")
            return True

        except httpx.HTTPStatusError as e:
            console.error(f"[MaceoptClient] HTTP error during optimization: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            console.exception(f"[MaceoptClient] An unexpected error occurred: {e}")
        
        return False