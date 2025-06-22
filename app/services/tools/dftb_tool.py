# app/services/tools/dftb_tool.py
# The module provides the high-level tool for DFTB+ optimization.
# Author: Shibo Li
# Date: 2025-06-22
# Version: 1.0.0

import os
import uuid
import base64
from app.core.config import settings
from app.schemas.tool_schemas import DFTBToolInput
from app.services.clients.dftb_client import DFTBClient
from app.core.logger import console

DFTB_TOOL_DEF = {
    "tool_name": "optimize_structure_with_dftb_xtb",
    "description": "Performs geometry optimization on a crystal structure (CIF input) using the GFN-xTB method via the DFTB+ engine. Returns detailed results and the optimized structure.",
    "input_schema": DFTBToolInput.model_json_schema()
}

class DFTBTool:
    def __init__(self, task_id: str):
        self.task_dir = os.path.join(settings.TASKS_DIR, task_id)
        self.temp_dir = os.path.join(self.task_dir, "temp_files")
        os.makedirs(self.temp_dir, exist_ok=True)
        self.client = DFTBClient(base_url=settings.XTB_API_BASE_URL)

    def execute(self, tool_input: dict) -> dict:
        """
        Executes the DFTB+ optimization tool.
        """
        try:
            validated_input = DFTBToolInput.model_validate(tool_input)
        except Exception as e:
            return {"status": "failed", "error": f"Invalid input parameters for DFTB+ tool: {e}"}

        response_obj = self.client.optimize(
            input_path=validated_input.input_file_path,
            fmax=validated_input.fmax,
            method=validated_input.method
        )

        if response_obj and response_obj.status == "success":
            try:
                cif_content_b64 = response_obj.optimized_structure_cif_b64
                decoded_content = base64.b64decode(cif_content_b64)
            except Exception as e:
                return {"status": "failed", "error": f"Failed to decode Base64 structure: {e}"}

            input_basename, _ = os.path.splitext(os.path.basename(validated_input.input_file_path))
            new_filename = f"{input_basename}_dftbopt.cif"
            output_path = os.path.join(self.temp_dir, new_filename)

            with open(output_path, "wb") as f:
                f.write(decoded_content)
            
            console.success(f"[DFTBTool] Saved optimized structure to {output_path}")

            return {
                "status": "success",
                "output_file_path": output_path, 
                "detailed_results": response_obj.detailed_results
            }
        else:
            error_msg = response_obj.detailed_results.get("summary", {}).get("error") if response_obj else "Check logs."
            return {"status": "failed", "error": f"DFTB+ optimization failed in client. Details: {error_msg}"}