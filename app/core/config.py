# app/core/config.py
# The module provides application settings using Pydantic's BaseSettings.
# It loads configuration from environment variables and a .env file.
# The settings include API keys, model configurations, and workspace directories.
# Author: Shibo Li
# Date: 2025-06-17
# Version: 0.1.0

import os
from pydantic_settings import BaseSettings
from typing import Literal


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Settings(BaseSettings):
    """
    Application settings are loaded from environment variables and .env file.
    This class only DECLARES the settings. Secrets and environment-specific
    values MUST be provided in the .env file or the environment.
    """
    PROJECT_NAME: str = "MCP Agent"
    API_V1_STR: str = "/api/v1"

    # LLM PROVIDER
    LLM_PROVIDER: Literal[
        "DEEPSEEK_CHAT", "GEMINI", "CHATGPT", "CLAUDE", "DEEPSEEK_REASONER"
    ] = "DEEPSEEK_CHAT"

    # CHATGPT
    CHATGPT_API_KEY: str
    CHATGPT_MODEL: str
    CHATGPT_BASE_URL: str

    # CLAUDE
    CLAUDE_API_KEY: str
    CLAUDE_MODEL: str
    CLAUDE_BASE_URL: str
    # GEMINI
    GEMINI_API_KEY: str
    GEMINI_MODEL: str
    GEMINI_BASE_URL: str

    # DEEPSEEK_CHAT
    DEEPSEEK_CHAT_API_KEY: str
    DEEPSEEK_CHAT_MODEL: str
    DEEPSEEK_CHAT_BASE_URL: str

    # DEEPSEEK_REASONER
    DEEPSEEK_REASONER_API_KEY: str
    DEEPSEEK_REASONER_MODEL: str
    DEEPSEEK_REASONER_BASE_URL: str


    # Base line apr urls
    ZEO_API_BASE_URL: str
    MACEOPT_API_BASE_URL: str
    XTB_API_BASE_URL: str
    CONVERTER_API_BASE_URL: str

    # workspace settings, with default values
    WORKSPACE_DIR: str = os.path.join(ROOT_DIR, "workspace")
    TASKS_DIR: str = os.path.join(WORKSPACE_DIR, "tasks")

    class Config:
        env_file = os.path.join(ROOT_DIR, ".env")
        env_file_encoding = 'utf-8'
        case_sensitive = False 

settings = Settings() # type: ignore
