# app/services/tools/maceopt_tool.py
# Updated MACEOPT tool to align with the new API version.
# Author: Shibo Li
# Date: 2025-06-22
# Version: 0.1.0

import os
import uuid
from app.core.config import settings
from app.schemas.tool_schemas import MaceoptToolInput
from app.services.clients.maceopt_client import MaceoptClient
from app.core.logger import console


MACEOPT_TOOL_DEF = {
    "tool_name": "optimize_structure_with_mace",
    "description": "Performs geometry optimization on a crystal structure (CIF supported) using the MACE machine learning potential. This is an excellent first step for any new structure to get a relaxed, low-energy conformation.",
    "input_schema": MaceoptToolInput.model_json_schema()
}
 
class MaceoptTool:
    def __init__(self, task_id: str):
        self.task_dir = os.path.join(settings.TASKS_DIR, task_id)
        self.temp_dir = os.path.join(self.task_dir, "temp_files")
        os.makedirs(self.temp_dir, exist_ok=True)
        self.client = MaceoptClient(base_url=settings.MACEOPT_API_BASE_URL)

    def execute(self, tool_input: dict) -> dict:
        """
        Executes the MACE optimization tool using the updated client.
        """
        try:
            validated_input = MaceoptToolInput.model_validate(tool_input)
        except Exception as e:
            return {"status": "failed", "error": f"Invalid input parameters for MACEOPT tool: {e}"}

        optimize_response = self.client.optimize(
            input_path=validated_input.input_file_path,
            fmax=validated_input.fmax,
            device=validated_input.device
        )

        if not (optimize_response and optimize_response.success):
            return {"status": "failed", "error": "MACE optimization failed at the API level. Check logs."}

        download_link = optimize_response.download_links.cif
        optimized_content = self.client.download_file(download_link)

        if not optimized_content:
            return {"status": "failed", "error": "Failed to download the optimized CIF file from MACEOPT API."}

        input_basename, _ = os.path.splitext(os.path.basename(validated_input.input_file_path))
        new_filename = f"{input_basename}_maceopt.cif"
        output_path = os.path.join(self.temp_dir, new_filename)
        
        try:
            with open(output_path, "wb") as f:
                f.write(optimized_content)
            console.success(f"[MaceoptTool] Saved optimized structure to {output_path}")
            return {
                "status": "success",
                "output_file_path": output_path, 
                "energy": optimize_response.energy,
                "stress": optimize_response.stress
            }
        except Exception as e:
            return {"status": "failed", "error": f"Failed to save optimized file: {e}"}