# app/api/endpoints.py
# This module defines the API endpoints for interacting with the MCP Agent.
# It handles task creation and status retrieval using an asynchronous background task model.
# Author: Shibo Li
# Date: 2025-06-22
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
    """This utility function saves a dictionary to a JSON file.
    Args:
        filepath (str): The path where the JSON file will be saved.
        data (Dict): The dictionary data to save.
    Raises:
        Exception: If the file cannot be written, an error is logged.
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        console.error(f"Failed to save JSON to {filepath}: {e}")

def _run_agent_task(task_id: str, query: str, initial_file_path: str):
    """
    This function runs the agent task in the background.
    It performs the following steps:
    1. Planning: Uses the LLM to create an execution plan based on the user's query and initial file.
    2. Execution: Executes the generated plan using the AgentExecutor.
    3. Completion: Saves the final status and execution log.
    Args:
        task_id (str): Unique identifier for the task.
        query (str): User's natural language request.
        initial_file_path (str): Path to the initial file that will be used in the execution plan.
    Raises:
        ValueError: If the LLM planning fails or returns an invalid plan.
        RuntimeError: If the plan execution does not complete successfully.
        Exception: For any other errors during the task execution.
    """
    task_dir = os.path.join(settings.TASKS_DIR, task_id)
    status_file = os.path.join(task_dir, "_status.json")
    plan_file = os.path.join(task_dir, "_llm_plan.json")
    log_file = os.path.join(task_dir, "_execution_log.json")

    try:
        # 1. planning 
        _save_json(status_file, {"status": "planning", "details": "Asking LLM to create a plan..."})
        plan = create_execution_plan(user_query=query, initial_file_path=initial_file_path)
        _save_json(plan_file, plan)

        if plan.get("status") == "error" or "plan" not in plan:
            raise ValueError(f"LLM planning failed: {plan.get('message', 'No valid plan returned.')}")

        # 2. execution
        _save_json(status_file, {"status": "executing", "details": "Executing the generated plan..."})
        executor = AgentExecutor(task_id=task_id)
        initial_context = {"initial_file_path": initial_file_path}
        execution_log = executor.execute_plan(plan, initial_context)
        _save_json(log_file, execution_log)

        # 3. completion
        final_status = execution_log.get("final_status", {})
        if final_status.get("status") != "completed":
             raise RuntimeError(f"Plan execution did not complete successfully. Check execution log for details.")

        _save_json(status_file, {"status": "completed", "details": "Task finished successfully."})
        console.success(f"Task {task_id} completed successfully.")

    except Exception as e:
        console.exception(f"Task {task_id} failed during execution.")
        error_details = {"status": "failed", "error": str(e)}
        _save_json(status_file, error_details)


@router.post("/agent/execute", response_model=TaskCreationResponse, status_code=202)
async def execute_agent(
    background_tasks: BackgroundTasks,
    query: str = Form(..., description="The user's request in natural language."),
    files: List[UploadFile] = File(..., description="One or more initial structure files.")
):
    """
    Accepts a user's query and one or more files, creates a unique task ID,
    and starts processing the request in the background.
    The files are saved in a dedicated directory for this task.
    Args:
        background_tasks (BackgroundTasks): FastAPI's background task manager.
        query (str): The user's natural language request.
        files (List[UploadFile]): One or more files uploaded by the user.
    Returns:
        TaskCreationResponse: Contains the task ID and a message indicating that the task has been accepted
    Raises:
        HTTPException: If no files are uploaded or if there is an error saving the files.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files were uploaded.")

    task_id = str(uuid.uuid4())
    task_dir = os.path.join(settings.TASKS_DIR, task_id)
    input_dir = os.path.join(task_dir, "input")
    os.makedirs(input_dir, exist_ok=True)

    # save uploaded files to the task's input directory
    saved_file_paths = []
    for file in files:
        safe_filename = os.path.basename(file.filename) # type: ignore[no-untyped-call]
        file_path = os.path.join(input_dir, safe_filename)
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            saved_file_paths.append(file_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Could not save file: {e}")
    
    console.info(f"Created task {task_id} for query: '{query}'")

    #  Ensure at least one file was saved successfully
    initial_file_path = saved_file_paths[0]

    #  Save initial task metadata
    background_tasks.add_task(_run_agent_task, task_id, query, initial_file_path)

    return {"message": "Agent task accepted. Processing in the background.", "task_id": task_id}


@router.get("/agent/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """
    Retrieves the status of a specific task by its ID.
    Args:
        task_id (str): The unique identifier of the task.
    Returns:
        TaskStatusResponse: Contains the task ID, status, LLM plan, and execution log.
    Raises:
        HTTPException: If the task ID does not exist or if there is an error reading the task files.
    """
    task_dir = os.path.join(settings.TASKS_DIR, task_id)
    if not os.path.isdir(task_dir):
        raise HTTPException(status_code=404, detail=f"Task with ID '{task_id}' not found.")

    response_data = {"task_id": task_id, "status": "unknown"}

    def _read_json_file(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    status_data = _read_json_file(os.path.join(task_dir, "_status.json"))
    if status_data:
        response_data.update(status_data)

    response_data["llm_plan"] = _read_json_file(os.path.join(task_dir, "_llm_plan.json")) # type: ignore[no-untyped-call]
    response_data["execution_log"] = _read_json_file(os.path.join(task_dir, "_execution_log.json")) # type: ignore[no-untyped-call]

    return response_data