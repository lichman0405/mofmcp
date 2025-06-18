# app/services/tools/converter_tool.py
# The module provides a high-level tool for converting crystal structure file formats.
# It defines the tool metadata, input schema, and the execution logic for the conversion task.
# Author: Shibo Li
# Date: 2025-06-18
# Version: 0.1.0

import os
import uuid
from app.core.config import settings
from app.schemas.tool_schemas import FileConverterInput
from app.services.clients.converter_client import ConverterClient
from app.core.logger import console

CONVERTER_TOOL_DEF = {
    "tool_name": "convert_structure_file",
    "description": "Converts a crystal structure file between .cif and .xyz formats. Use this if a subsequent tool requires a specific format.",
    "input_schema": FileConverterInput.model_json_schema()
}

class ConverterTool:
    def __init__(self, task_id: str):
        self.task_dir = os.path.join(settings.TASKS_DIR, task_id)
        self.temp_dir = os.path.join(self.task_dir, "temp_files")
        os.makedirs(self.temp_dir, exist_ok=True)
        self.client = ConverterClient(base_url=settings.CONVERTER_API_BASE_URL)

    def execute(self, tool_input: dict) -> dict:
        """
        Executes the file conversion tool. It receives the converted file content
        as bytes and saves it to a new file.
        """
        try:
            validated_input = FileConverterInput.model_validate(tool_input)
        except Exception as e:
            return {"status": "failed", "error": f"Invalid input parameters for Converter tool: {e}"}

        converted_content = self.client.convert_file(input_path=validated_input.input_file_path)

        if converted_content:
            filename = os.path.basename(validated_input.input_file_path)
            base, _ = os.path.splitext(filename)
            unique_id = str(uuid.uuid4())[:5]
            output_path = os.path.join(self.temp_dir, f"{base}_converted_{unique_id}.{validated_input.target_format}")

            try:
                with open(output_path, "wb") as f:
                    f.write(converted_content)
                return {"status": "success", "output_file_path": output_path}
            except Exception as e:
                return {"status": "failed", "error": f"Failed to save converted file: {e}"}
        else:
            return {"status": "failed", "error": "File conversion failed in client. Check logs for details."}