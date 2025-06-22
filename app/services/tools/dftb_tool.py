# app/services/tools/dftb_tool.py
# The module provides the high-level tool for DFTB+ optimization,
# implementing the adapter pattern to decouple internal logic from the raw API response.
# Author: Shibo Li
# Date: 2025-06-22
# Version: 1.0.0

import os
import base64
from app.core.config import settings
from app.schemas.tool_schemas import DFTBToolInput
from app.services.clients.dftb_client import DFTBClient
from app.schemas.dftb_api_schemas import RawDFTBOptimizeResponse
from app.schemas.dftb_domain_schemas import DFTBResult
from app.core.logger import console

# Description of the DFTB+ optimization tool
DFTB_TOOL_DEF = {
    "tool_name": "optimize_structure_with_dftb_xtb",
    "description": "Performs geometry optimization on a crystal structure (CIF input) using the GFN-xTB method via the DFTB+ engine. Returns detailed results and the optimized structure.",
    "input_schema": DFTBToolInput.model_json_schema()
}


def _map_api_response_to_domain_model(response: RawDFTBOptimizeResponse, saved_path: str) -> DFTBResult:
    """
    Adapter function: Maps the raw API response object to our clean internal domain model.
    """
    summary = response.detailed_results.get("summary", {})
    energies = response.detailed_results.get("energies_eV", {})
    
    return DFTBResult(
        status="success",
        output_file_path=saved_path,
        is_converged="YES" in summary.get("convergence_status", ""),
        final_energy_eV=energies.get("Total"),
        detailed_results=response.detailed_results
    )

# Executable tool class for DFTB+ optimization
class DFTBTool:
    def __init__(self, task_id: str):
        self.task_dir = os.path.join(settings.TASKS_DIR, task_id)
        self.temp_dir = os.path.join(self.task_dir, "temp_files")
        os.makedirs(self.temp_dir, exist_ok=True)
        self.client = DFTBClient(base_url=settings.XTB_API_BASE_URL)

    def execute(self, tool_input: dict) -> dict:
        """
        Executes the DFTB+ optimization tool using the adapter pattern.
        """
        try:
            validated_input = DFTBToolInput.model_validate(tool_input)
        except Exception as e:
            error_message = f"Invalid input parameters for DFTB+ tool: {e}"
            return {"status": "failed", "error": error_message}

        api_response = self.client.optimize(
            input_path=validated_input.input_file_path,
            fmax=validated_input.fmax,
            method=validated_input.method
        )

        if api_response and api_response.status == "success":
            try:
                decoded_content = base64.b64decode(api_response.optimized_structure_cif_b64)
                
                input_basename, _ = os.path.splitext(os.path.basename(validated_input.input_file_path))
                new_filename = f"{input_basename}_dftbopt.cif"
                output_path = os.path.join(self.temp_dir, new_filename)

                with open(output_path, "wb") as f:
                    f.write(decoded_content)
                console.success(f"[DFTBTool] Saved optimized structure to {output_path}")

                clean_result = _map_api_response_to_domain_model(api_response, output_path)
                return clean_result.model_dump() 

            except Exception as e:
                 return {"status": "failed", "error": f"Failed to decode or save file: {e}"}
        else:
            error_msg = getattr(api_response, 'detailed_results', {}).get("summary", {}).get("error", "Unknown error in client.")
            return {"status": "failed", "error": f"DFTB+ optimization failed. Details: {error_msg}"}