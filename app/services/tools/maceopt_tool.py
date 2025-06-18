# app/services/tools/maceopt_tool.py
# The module provides a high-level tool for performing geometry optimization on crystal structures using the MACE model.
# It defines the tool metadata, input schema, and the execution logic for the optimization task.
# Author: Shibo Li
# Date: 2025-06-18
# Version: 0.1.0

import os
import uuid
from app.core.config import settings
from app.schemas.tool_schemas import MaceoptToolInput
from app.services.clients.maceopt_client import MaceoptClient
from app.core.logger import console

# Tool description definition
MACEOPT_TOOL_DEF = {
    "tool_name": "optimize_structure_with_mace",
    "description": "Performs geometry optimization on a crystal structure using the MACE machine learning potential. This is an excellent first step for any new structure to get a relaxed, low-energy conformation before further analysis. It is generally faster than xTB for similar accuracy. The input file should be an .xyz file.",
    "input_schema": MaceoptToolInput.model_json_schema()
}

# Executable tool class definition
class MaceoptTool:
    def __init__(self, task_id: str):
        self.task_dir = os.path.join(settings.TASKS_DIR, task_id)
        # Create a unique directory for temporary files for this task
        unique_id = str(uuid.uuid4())[:5]
        self.temp_dir = os.path.join(self.task_dir, "temp_files", f"maceopt_output_{unique_id}")
        os.makedirs(self.temp_dir, exist_ok=True)
        
        self.client = MaceoptClient(base_url=settings.MACEOPT_API_BASE_URL)

    def execute(self, tool_input: dict) -> dict:
        """
        Executes the MACE optimization tool.
        It now accepts a dictionary and validates it internally.
        """
        # validate the input parameters using the Pydantic model
        try:
            validated_input = MaceoptToolInput.model_validate(tool_input)
        except Exception as e:
            error_message = f"Invalid input parameters for MACEOPT tool: {e}"
            console.error(f"[MaceoptTool] {error_message}")
            return {"status": "failed", "error": error_message}

        # Generate a unique output path for the optimized file
        filename = os.path.basename(validated_input.input_file_path)
        base, ext = os.path.splitext(filename)
        output_path = os.path.join(self.temp_dir, f"{base}_maceopt{ext}")

        # Call the underlying client to perform the actual operation
        success = self.client.optimize_and_save(
            input_path=validated_input.input_file_path,
            output_path=output_path,
            fmax=validated_input.fmax,
            device=validated_input.device
        )

        # Return the result
        if success:
            return {"status": "success", "optimized_file_path": output_path}
        else:
            return {"status": "failed", "error": "MACE optimization failed in client. Check logs for details."}