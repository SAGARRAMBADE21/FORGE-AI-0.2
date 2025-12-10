"""
Frontend Scanner - LangGraph-powered code analysis for AI agents.

A production-ready scanner for analyzing frontend codebases using LangChain,
LangGraph, and tree-sitter AST parsing.
"""

__version__ = "1.0.0"
__author__ = "Engineering Team"

from frontend_scanner.config import ScannerConfig
from frontend_scanner.workflows.scanner_graph import create_scanner_workflow

__all__ = [
    "ScannerConfig",
    "create_scanner_workflow",
    "__version__",
]
