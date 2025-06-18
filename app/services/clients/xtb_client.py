# app/services/clients/xtb_client.py
# This module contains the low-level client for interacting with the xTB Geometry Optimization API.
# It handles the two-step process of submitting a job and downloading the results.
# Author: Shibo Li
# Date: 2025-06-18
# Version: 1.0.0

import httpx
import os
import io
import zipfile
from typing import Optional

from app.core.logger import console
from app.schemas.xtb_schemas import XTBOptimizeResponse

class XTBClient:
    """A low-level client for the xTB Geometry Optimization API."""

    def __init__(self, base_url: str):
        if not base_url:
            raise ValueError("xTB API base URL cannot be empty.")
        self.base_url = base_url
        self.client = httpx.Client(base_url=self.base_url, timeout=600.0)

    def optimize_and_unpack(self, input_path: str, output_dir: str, charge: int, uhf: int, gfn: int) -> Optional[str]:
        """
        Submits an optimization job, downloads the resulting ZIP archive,
        unpacks it, finds 'xtbopt.xyz', renames it, and returns the new path.
        """
        console.info(f"[XTBClient] Starting xTB optimization for {os.path.basename(input_path)}...")
        
        try:
            # upload the input file and submit the optimization job
            if not os.path.exists(input_path):
                console.error(f"[XTBClient] Input file not found: {input_path}")
                return None

            with open(input_path, "rb") as f:
                files = {"file": (os.path.basename(input_path), f, "application/octet-stream")}
                data = {"charge": str(charge), "uhf": str(uhf), "gfn": str(gfn)}
                
                optimize_response = self.client.post("/optimize", files=files, data=data)
                optimize_response.raise_for_status()

                response_data = XTBOptimizeResponse.model_validate(optimize_response.json())
                job_id = response_data.job_id
                console.success(f"[XTBClient] Optimization job submitted. Job ID: {job_id}")

            # download the results using the job ID
            download_url = f"/download/{job_id}"
            download_response = self.client.get(download_url)
            download_response.raise_for_status()

            # unzip the downloaded content
            os.makedirs(output_dir, exist_ok=True)
            zip_in_memory = io.BytesIO(download_response.content)
            with zipfile.ZipFile(zip_in_memory, 'r') as zip_ref:
                zip_ref.extractall(output_dir)
            console.success(f"[XTBClient] Unpacked results to: {output_dir}")

            # find and rename 'xtbopt.xyz'
            original_opt_file = os.path.join(output_dir, "xtbopt.xyz")
            if not os.path.exists(original_opt_file):
                console.error("[XTBClient] 'xtbopt.xyz' not found in the downloaded archive.")
                return None

            input_basename, _ = os.path.splitext(os.path.basename(input_path))
            new_filename = f"{input_basename}_xtbopt.xyz"
            new_opt_file_path = os.path.join(output_dir, new_filename)

            os.rename(original_opt_file, new_opt_file_path)
            
            console.success(f"[XTBClient] Renamed 'xtbopt.xyz' to '{new_filename}'")
            return new_opt_file_path

        except Exception as e:
            console.exception(f"[XTBClient] An unexpected error occurred: {e}")
        
        return None