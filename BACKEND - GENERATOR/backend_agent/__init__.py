"""
Backend Generation Agent - AI-powered backend code generator
"""

__version__ = "1.0.0"
__author__ = "Your Name"

from backend_agent.config import BackendAgentConfig
from backend_agent.workflow.backend_workflow import create_backend_workflow

__all__ = [
    "BackendAgentConfig",
    "create_backend_workflow",
]
