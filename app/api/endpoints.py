# app/api/endpoints.py
# This module defines the API endpoints for interacting with the MCP Agent.
# It handles task creation and status retrieval using an asynchronous background task model.
# Author: Shibo Li
# Date: 2025-06-18
# Version: 1.0.0

import os
import shutil
import json
import uuid
from typing import List, Dict

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks

from app.core.config import settings
from app.core.logger import console
from app.schemas.api_schemas import TaskCreationResponse, TaskStatusResponse
from app.services.llm_handler import create_execution_plan
from app.services.agent_executor import AgentExecutor

router = APIRouter()

def _save_json(filepath: str, data: Dict):
    """Helper function to save a dictionary to a JSON file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def _run_agent_task(task_id: str, query: str, initial_file_path: str):
    """
    This is the main workhorse function that runs in the background.
    It orchestrates the entire agent process: planning and execution.
    """
    task_dir = os.path.join(settings.TASKS_DIR, task_id)
    status_file = os.path.join(task_dir, "_status.json")
    plan_file = os.path.join(task_dir, "_llm_plan.json")
    log_file = os.path.join(task_dir, "_execution_log.json")

    try:
        # planning
        _save_json(status_file, {"status": "planning", "details": "Asking LLM to create a plan..."})
        plan = create_execution_plan(user_query=query, initial_file_path=initial_file_path)
        _save_json(plan_file, plan)

        if plan.get("status") == "error":
            raise ValueError(f"LLM planning failed: {plan.get('message')}")

        # executing
        _save_json(status_file, {"status": "executing", "details": "Executing the generated plan..."})
        executor = AgentExecutor(task_id=task_id)
        initial_context = {"initial_file_path": initial_file_path}
        execution_log = executor.execute_plan(plan, initial_context)
        _save_json(log_file, execution_log)

        # finishing
        final_status = execution_log.get("final_status", {})
        if final_status.get("status") != "completed":
             raise RuntimeError(f"Plan execution failed. Last status: {final_status}")

        _save_json(status_file, {"status": "completed", "details": "Task finished successfully."})
        console.success(f"Task {task_id} completed successfully.")

    except Exception as e:
        console.exception(f"Task {task_id} failed.")
        error_details = {"status": "failed", "error": str(e)}
        _save_json(status_file, error_details)


@router.post("/agent/execute", response_model=TaskCreationResponse, status_code=202)
async def execute_agent(
    background_tasks: BackgroundTasks,
    query: str = Form(..., description="The user's request in natural language."),
    files: List[UploadFile] = File(..., description="One or more initial structure files.")
):
    """
    Accepts a user query and files, starts the agent as a background task,
    and immediately returns a task ID for status tracking.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files were uploaded.")

    task_id = str(uuid.uuid4())
    task_dir = os.path.join(settings.TASKS_DIR, task_id)
    input_dir = os.path.join(task_dir, "input")
    os.makedirs(input_dir, exist_ok=True)

    # upload and save files
    saved_file_paths = []
    for file in files:
        if file.filename is None:
            console.error(f"File upload error: {file.filename} has no filename.")
            raise HTTPException(status_code=400, detail="Uploaded file must have a filename.")
        file_path = os.path.join(input_dir, file.filename)
        with open(file_path, "wb") as buffer:
            console.info(f"Saving uploaded file {file.filename} to {file_path}")
            shutil.copyfileobj(file.file, buffer)
        saved_file_paths.append(file_path)
    
    console.info(f"Created task {task_id} for query: '{query}'")
    # Save initial task status
    initial_file_path = saved_file_paths[0]

    # 
    background_tasks.add_task(_run_agent_task, task_id, query, initial_file_path)

    return {
        "message": "Agent task accepted and is now running in the background.",
        "task_id": task_id
    }


@router.get("/agent/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """
    Retrieves the status, plan, and execution log for a given task ID.
    """
    task_dir = os.path.join(settings.TASKS_DIR, task_id)
    if not os.path.isdir(task_dir):
        raise HTTPException(status_code=404, detail="Task not found.")

    response = {"task_id": task_id, "status": "unknown"}

    def _read_json_file(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    status_data = _read_json_file(os.path.join(task_dir, "_status.json"))
    if status_data:
        response.update(status_data)

    response["llm_plan"] = _read_json_file(os.path.join(task_dir, "_llm_plan.json")) # type: ignore
    response["execution_log"] = _read_json_file(os.path.join(task_dir, "_execution_log.json")) # type: ignore

    return response