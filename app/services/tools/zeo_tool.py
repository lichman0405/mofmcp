# app/services/tools/zeo_tool.py
# The module provides a suite of high-level tools for analyzing crystal structures using Zeo++.
# It defines tool metadata, input schemas, and execution logic for various Zeo++ calculations.
# Author: Shibo Li
# Date: 2025-06-18
# Version: 1.2.0 (Version updated to be complete)

from app.core.config import settings
from app.schemas.tool_schemas import (
    ZeoPoreDiameterInput, ZeoSurfaceAreaInput, ZeoAccessibleVolumeInput,
    ZeoProbeVolumeInput, ZeoChannelAnalysisInput
)
from app.services.clients.zeo_client import ZeoPlusPlusClient
from app.core.logger import console

# Define the tool metadata for Zeo++ analysis tools

ZEO_TOOL_DEFS = [
    {
        "tool_name": "calculate_pore_diameter",
        "description": "Calculates the largest free sphere (Di) and largest included sphere (Df) of a crystal structure. This is essential for understanding the pore size. The input file should be a CIF file.",
        "input_schema": ZeoPoreDiameterInput.model_json_schema()
    },
    {
        "tool_name": "calculate_surface_area",
        "description": "Calculates the accessible surface area (ASA) of a framework using Monte Carlo sampling. Useful for gas adsorption applications. The input file should be a CIF file.",
        "input_schema": ZeoSurfaceAreaInput.model_json_schema()
    },
    {
        "tool_name": "calculate_accessible_volume",
        "description": "Calculates the accessible volume (AV) of a framework and its density. Key metrics for material porosity. The input file should be a CIF file.",
        "input_schema": ZeoAccessibleVolumeInput.model_json_schema()
    },
    {
        "tool_name": "calculate_probe_volume",
        "description": "Computes the probe-occupiable volume (POAV) of a framework, which is the volume that can be occupied by a probe molecule. The input file should be a CIF file.",
        "input_schema": ZeoProbeVolumeInput.model_json_schema()
    },
    {
        "tool_name": "analyze_channels",
        "description": "Analyzes the dimensionality of the channel system (0D for cages, 1D for channels, 2D for layers, 3D for connected networks). Also provides pore diameters. The input file should be a CIF file.",
        "input_schema": ZeoChannelAnalysisInput.model_json_schema()
    }
]


class ZeoTool:
    def __init__(self):
        self.client = ZeoPlusPlusClient(base_url=settings.ZEO_API_BASE_URL)

    def calculate_pore_diameter(self, tool_input: dict) -> dict:
        """Executes the pore diameter calculation tool."""
        try:
            validated_input = ZeoPoreDiameterInput.model_validate(tool_input)
            response = self.client.calculate_pore_diameter(**validated_input.model_dump())
            if response:
                return {"status": "success", **response.model_dump()}
        except Exception as e:
            console.error(f"[ZeoTool] Error in calculate_pore_diameter: {e}")
        return {"status": "failed", "error": "Zeo++ calculate_pore_diameter failed. Check logs."}

    def calculate_surface_area(self, tool_input: dict) -> dict:
        """Executes the surface area calculation tool."""
        try:
            validated_input = ZeoSurfaceAreaInput.model_validate(tool_input)
            response = self.client.calculate_surface_area(**validated_input.model_dump())
            if response:
                return {"status": "success", **response.model_dump()}
        except Exception as e:
            console.error(f"[ZeoTool] Error in calculate_surface_area: {e}")
        return {"status": "failed", "error": "Zeo++ calculate_surface_area failed. Check logs."}

    def calculate_accessible_volume(self, tool_input: dict) -> dict:
        """Executes the accessible volume calculation tool."""
        try:
            validated_input = ZeoAccessibleVolumeInput.model_validate(tool_input)
            response = self.client.calculate_accessible_volume(**validated_input.model_dump())
            if response:
                return {"status": "success", **response.model_dump()}
        except Exception as e:
            console.error(f"[ZeoTool] Error in calculate_accessible_volume: {e}")
        return {"status": "failed", "error": "Zeo++ calculate_accessible_volume failed. Check logs."}

    def calculate_probe_volume(self, tool_input: dict) -> dict:
        """Executes the probe-occupiable volume calculation tool."""
        try:
            validated_input = ZeoProbeVolumeInput.model_validate(tool_input)
            response = self.client.calculate_probe_volume(**validated_input.model_dump())
            if response:
                return {"status": "success", **response.model_dump()}
        except Exception as e:
            console.error(f"[ZeoTool] Error in calculate_probe_volume: {e}")
        return {"status": "failed", "error": "Zeo++ calculate_probe_volume failed. Check logs."}

    def analyze_channels(self, tool_input: dict) -> dict:
        """Executes the channel analysis tool."""
        try:
            validated_input = ZeoChannelAnalysisInput.model_validate(tool_input)
            response = self.client.analyze_channels(**validated_input.model_dump())
            if response:
                return {"status": "success", **response.model_dump()}
        except Exception as e:
            console.error(f"[ZeoTool] Error in analyze_channels: {e}")
        return {"status": "failed", "error": "Zeo++ analyze_channels failed. Check logs."}