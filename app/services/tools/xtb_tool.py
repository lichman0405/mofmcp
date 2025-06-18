# app/services/tools/xtb_tool.py
# This module provides the high-level tool for xTB optimization,
# updated to work with the simplified single-call client.
# Author: Shibo Li
# Date: 2025-06-18
# Version: 0.2.0

import os
import uuid
from app.core.config import settings
from app.schemas.tool_schemas import XTBToolInput
from app.services.clients.xtb_client import XTBClient
from app.core.logger import console

# Define the tool's metadata and input schema
XTB_TOOL_DEF = {
    "tool_name": "optimize_structure_with_xtb",
    "description": "Performs geometry optimization on a crystal structure using the semi-empirical GFN-xTB method. This tool REQUIRES an .xyz file as input. It is a good, fast alternative to MACE for geometry relaxation.",
    "input_schema": XTBToolInput.model_json_schema()
}

# Excute the tool definition
class XTBTool:
    def __init__(self, task_id: str):
        self.task_dir = os.path.join(settings.TASKS_DIR, task_id)
        self.temp_dir = os.path.join(self.task_dir, "temp_files")
        os.makedirs(self.temp_dir, exist_ok=True)
        
        self.client = XTBClient(base_url=settings.XTB_API_BASE_URL)

    def execute(self, tool_input: dict) -> dict:
        """
        Executes the xTB optimization tool.
        It receives the optimized file content as bytes and saves it to a new file.
        """
        try:
            validated_input = XTBToolInput.model_validate(tool_input)
        except Exception as e:
            error_message = f"Invalid input parameters for xTB tool: {e}"
            return {"status": "failed", "error": error_message}

        # Call the xTB client to perform optimization
        optimized_content = self.client.optimize(
            input_path=validated_input.input_file_path,
            charge=validated_input.charge,
            uhf=validated_input.uhf,
            gfn=validated_input.gfn
        )

        if optimized_content:
            input_basename, _ = os.path.splitext(os.path.basename(validated_input.input_file_path))
            new_filename = f"{input_basename}_xtbopt.xyz"
            output_path = os.path.join(self.temp_dir, new_filename)
            
            try:
                with open(output_path, "wb") as f:
                    f.write(optimized_content)
                
                console.success(f"[XTBTool] Saved optimized structure to {output_path}")
                return {"status": "success", "output_file_path": output_path}
            except Exception as e:
                return {"status": "failed", "error": f"Failed to save optimized file: {e}"}
        else:
            return {"status": "failed", "error": "xTB optimization failed in client. Check logs for details."}