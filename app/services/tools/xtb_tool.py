# app/services/tools/xtb_tool.py
# The module provides a high-level tool for performing geometry optimization on crystal structures using the xTB method.
# It defines the tool metadata, input schema, and the execution logic for the optimization task.
# Author: Shibo Li
# Date: 2025-06-18
# Version: 0.1.0

import os
import uuid
from app.core.config import settings
from app.schemas.tool_schemas import XTBToolInput
from app.services.clients.xtb_client import XTBClient
from app.core.logger import console

# Define the tool metadata for xTB optimization
XTB_TOOL_DEF = {
    "tool_name": "optimize_structure_with_xtb",
    "description": "Performs geometry optimization on a crystal structure using the semi-empirical GFN-xTB method. This tool REQUIRES an .xyz file as input. It is a good, fast alternative to MACE for geometry relaxation. The input file should be an .xyz file.",
    "input_schema": XTBToolInput.model_json_schema()
}

# Type definition for the tool input
class XTBTool:
    def __init__(self, task_id: str):
        self.task_dir = os.path.join(settings.TASKS_DIR, task_id)
        unique_id = str(uuid.uuid4())[:5]
        self.output_dir = os.path.join(self.task_dir, "temp_files", f"xtb_output_{unique_id}")
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.client = XTBClient(base_url=settings.XTB_API_BASE_URL)

    def execute(self, tool_input: dict) -> dict:
        """
        Executes the xTB optimization tool.
        It now accepts a dictionary and validates it internally.
        """
        # validate the input parameters using the Pydantic model
        try:
            validated_input = XTBToolInput.model_validate(tool_input)
        except Exception as e:
            error_message = f"Invalid input parameters for xTB tool: {e}"
            console.error(f"[XTBTool] {error_message}")
            return {"status": "failed", "error": error_message}

        # check if the input file exists
        if not validated_input.input_file_path.lower().endswith('.xyz'):
            error_message = f"Invalid file format for xTB tool. Expected .xyz, but got {os.path.basename(validated_input.input_file_path)}."
            console.error(f"[XTBTool] {error_message}")
            return {"status": "failed", "error": error_message}

        # call low-level client to perform optimization and unpack the results
        optimized_file_path = self.client.optimize_and_unpack(
            input_path=validated_input.input_file_path,
            output_dir=self.output_dir,
            charge=validated_input.charge,
            uhf=validated_input.uhf,
            gfn=validated_input.gfn
        )

        # feed back the result
        if optimized_file_path:
            return {
                "status": "success", 
                "output_file_path": optimized_file_path, 
                "output_directory": self.output_dir 
            }
        else:
            return {"status": "failed", "error": "xTB optimization failed in client. Check logs for details."}
