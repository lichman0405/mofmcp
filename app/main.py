# app/main.py
# This is the main entry point for the MCP Agent FastAPI application.
# It initializes the FastAPI app, includes the API routers, and defines startup/shutdown events.
# Author: Shibo Li
# Date: 2025-06-18
# Version: 1.0.0

from fastapi import FastAPI
from app.core.config import settings
from app.core.logger import console
from app.api import endpoints as api_router

# Initialize the FastAPI application and use the project name from the config as the title.
# The title and openapi_url will be displayed in the automatically generated API documentation (e.g., /docs).
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Print a log message when the application starts to confirm the configuration was successfully loaded.
@app.on_event("startup")
def startup_event():
    console.rule(f"[bold green]Starting up {settings.PROJECT_NAME}[/bold green]")
    console.info(f"LLM Provider set to: [bold cyan]{settings.LLM_PROVIDER}[/bold cyan]")
    console.info(f"Workspace directory is: {settings.TASKS_DIR}")
    console.success("Application startup complete.")

# Include all API routes defined in app/api/endpoints.py.
# The prefix will add a uniform prefix to all route URLs in this file.
# Tags will group these routes in the API documentation for easier viewing.
app.include_router(api_router.router, prefix=settings.API_V1_STR, tags=["Agent Endpoints"])

# Define a root route at /, primarily for a simple health check.
# You can confirm the service is running by visiting http://localhost:8000/.
@app.get("/", tags=["Health Check"])
def read_root():
    """
    A simple health check endpoint to confirm the service is running.
    """
    return {"status": "ok", "message": f"Welcome to {settings.PROJECT_NAME}! Visit /docs for API details."}

# Print a log message when the application shuts down.
@app.on_event("shutdown")
def shutdown_event():
    console.warning(f"--- Shutting down {settings.PROJECT_NAME} ---")