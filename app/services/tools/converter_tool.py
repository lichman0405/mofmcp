# app/services/tools/converter_tool.py
# The module provides a high-level tool for converting crystal structure file formats.
# It defines the tool metadata, input schema, and the execution logic for the conversion task.
# Author: Shibo Li
# Date: 2025-06-18
# Version: 0.1.0

import os
from app.core.config import settings
from app.schemas.tool_schemas import FileConverterInput
from app.services.clients.converter_client import ConverterClient
from app.core.logger import console

# Tool description definition
CONVERTER_TOOL_DEF = {
    "tool_name": "convert_structure_file",
    "description": "Converts a crystal structure file from one format to another (e.g., from .cif to .xyz). This is a crucial preparatory step if a subsequent tool requires a specific file format.",
    "input_schema": FileConverterInput.model_json_schema()
}

# Executable tool class definition
class ConverterTool:
    def __init__(self, task_id: str):
        # task_id is not used here for now, but this interface is retained to ensure consistency across all tools
        self.task_id = task_id
        self.client = ConverterClient(base_url=settings.CONVERTER_API_BASE_URL)

    def execute(self, tool_input: dict) -> dict:
        """
        Executes the file conversion tool.
        It now accepts a dictionary and validates it internally.
        """
        # validate the input parameters using the Pydantic model
        try:
            validated_input = FileConverterInput.model_validate(tool_input)
        except Exception as e:
            error_message = f"Invalid input parameters for Converter tool: {e}"
            console.error(f"[ConverterTool] {error_message}")
            return {"status": "failed", "error": error_message}

        # Calls the underlying client to perform the actual conversion operation
        response_obj = self.client.convert_file(input_path=validated_input.input_file_path)

        if response_obj and response_obj.status == 'success':
            # Directly returns the dictionary received from the client, containing status and path
            # We can add a check here to ensure the output format matches the expectation
            if not response_obj.output_path.endswith(validated_input.target_format):
                console.warning(f"Converter API output path '{response_obj.output_path}' does not match target format '{validated_input.target_format}'.")
            
            return response_obj.model_dump()
        else:
            return {"status": "failed", "error": "File conversion failed in client. Check logs for details."}