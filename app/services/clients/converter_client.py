# app/services/clients/converter_client.py
# The module provides a low-level client for interacting with the File Type Converter API.
# It includes a method for converting files to a specified format and returns structured responses.
# Author: Shibo Li
# Date: 2025-06-17
# Version: 0.1.0


import httpx
import os
from typing import Optional

from app.core.logger import console

class ConverterClient:
    """A low-level client for the File Type Converter API."""

    def __init__(self, base_url: str):
        if not base_url:
            raise ValueError("Converter API base URL cannot be empty.")
        self.base_url = base_url
        self.client = httpx.Client(base_url=self.base_url, timeout=60.0)

    def convert_file(self, input_path: str) -> Optional[bytes]:
        """
        Calls the /convert/ endpoint and directly returns the binary content of the converted file.
        """
        console.info(f"[ConverterClient] Starting file conversion for {os.path.basename(input_path)}...")

        if not os.path.exists(input_path):
            console.error(f"[ConverterClient] Input file not found: {input_path}")
            return None

        try:
            with open(input_path, "rb") as f:
                files = {"file": (os.path.basename(input_path), f, "application/octet-stream")}
                
                console.info(f"[ConverterClient] Calling POST /convert/...")
                response = self.client.post("/convert/", files=files)
                response.raise_for_status()

                console.success(f"[ConverterClient] File conversion successful, received {len(response.content)} bytes.")
                return response.content

        except httpx.HTTPStatusError as e:
            console.error(f"[ConverterClient] HTTP error during conversion: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            console.exception(f"[ConverterClient] An unexpected error occurred: {e}")

        return None