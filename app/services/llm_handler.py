# app/services/llm_handler.py
# This module is the "brain" of the agent, responsible for planning.
# It dynamically communicates with the configured LLM to generate an execution plan.
# Author: Shibo Li
# Date: 2025-06-18
# Version: 0.1.0

import os
import json
from jinja2 import Environment, FileSystemLoader
from openai import OpenAI

from app.core.config import settings
from app.core.logger import console
from app.services.tools.maceopt_tool import MACEOPT_TOOL_DEF
from app.services.tools.xtb_tool import XTB_TOOL_DEF
from app.services.tools.converter_tool import CONVERTER_TOOL_DEF
from app.services.tools.zeo_tool import ZEO_TOOL_DEFS

# Define all tool definitions in a single list for easy management
ALL_TOOL_DEFS = [
    MACEOPT_TOOL_DEF,
    XTB_TOOL_DEF,
    CONVERTER_TOOL_DEF,
    *ZEO_TOOL_DEFS
]

# Initialize Jinja2 environment for rendering prompts
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'templates')
jinja_env = Environment(loader=FileSystemLoader(template_dir))

def _query_llm(prompt: str) -> str:
    """
    Dynamically queries the correct LLM provider based on the .env configuration.
    This function contains all provider-specific logic.
    """
    provider = settings.LLM_PROVIDER
    console.info(f"[LLM Handler] Using LLM Provider: {provider}")

    try:
        # Static providers
        if provider in ["DEEPSEEK_CHAT", "DEEPSEEK_REASONER", "CHATGPT", "CLAUDE", "GEMINI"]:

            api_key = getattr(settings, f"{provider}_API_KEY")
            base_url = getattr(settings, f"{provider}_BASE_URL")
            model = getattr(settings, f"{provider}_MODEL")
            client = OpenAI(api_key=api_key, base_url=base_url)
            # get response from the LLM
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            if content is None:
                console.error("[LLM Handler] LLM returned empty response.")
                raise ValueError("LLM returned empty response")
            return content

        else:
            console.error(f"[LLM Handler] Unsupported LLM Provider: {provider}")
            raise NotImplementedError(f"LLM Provider '{provider}' is not implemented in llm_handler.")

    except Exception as e:
        console.exception(f"[LLM Handler] Failed to query LLM. Error: {e}")
        raise 

def create_execution_plan(user_query: str, initial_file_path: str) -> dict:
    """
    Generates a step-by-step execution plan by querying the LLM.
    This function is now decoupled from the specific LLM client.
    """
    console.rule("[Planner] Generating Execution Plan", style="bold yellow")
    
    try:
        # prepare the template with all tool definitions
        tools_json_string = json.dumps(ALL_TOOL_DEFS, indent=2)
        template = jinja_env.get_template("planner_prompt.jinja2")
        prompt = template.render(
            tools_json_string=tools_json_string,
            user_query=user_query,
            initial_file_path=initial_file_path
        )
        
        console.info("Sending request to LLM for planning...")

        plan_str = _query_llm(prompt)
        
        console.success("Received plan from LLM.")
        
        if plan_str.strip().startswith("```json"):
            plan_str = plan_str.strip()[7:-3].strip()
            
        plan_json = json.loads(plan_str)
        return plan_json

    except Exception as e:
        console.exception("Failed to generate and parse execution plan.")
        return {"status": "error", "message": f"Failed to create execution plan: {e}"}