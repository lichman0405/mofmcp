# app/main.py
# This is the main entry point for the MCP Agent FastAPI application.
# It initializes the FastAPI app, includes the API routers, and defines startup/shutdown events.
# Author: Shibo Li
# Date: 2025-06-22
# Version: 1.0.0

from fastapi import FastAPI
from app.core.config import settings
from app.core.logger import console
from app.api import endpoints as api_router

# Initialize the FastAPI application with basic configuration
# This includes setting the title, description, version, and OpenAPI URL
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="A dynamic computational chemistry workflow orchestrator powered by LLM.",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# print startup message when the application starts
@app.on_event("startup")
def startup_event():
    console.rule(f"[bold green]Starting up {settings.PROJECT_NAME}[/bold green]")
    console.info(f"LLM Provider set to: [bold cyan]{settings.LLM_PROVIDER}[/bold cyan]")
    console.info(f"Task Workspace directory is: {settings.TASKS_DIR}")
    console.success("Application startup complete. Ready to accept requests.")

# api_router is imported from app/api/endpoints.py
app.include_router(api_router.router, prefix=settings.API_V1_STR, tags=["MCP Agent"])

# define a simple health check endpoint
# This endpoint can be used to verify that the API is running and accessible
@app.get("/", tags=["Health Check"])
def read_root():
    """A simple health check endpoint."""
    return {"status": "ok", "message": f"Welcome to {settings.PROJECT_NAME}! Visit /docs for API details."}

# print shutdown message when the application is stopped
@app.on_event("shutdown")
def shutdown_event():
    console.warning(f"--- Shutting down {settings.PROJECT_NAME} ---")