#!/usr/bin/env python3
"""
Quick start script for Backend Generation Agent.
"""

import sys
from pathlib import Path

# Add backend_agent to path
sys.path.insert(0, str(Path(__file__).parent))

from backend_agent.api.cli import main

if __name__ == "__main__":
    main()
