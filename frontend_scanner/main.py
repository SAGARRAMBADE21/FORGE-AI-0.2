"""Entry point for running scanner as a module."""
import sys
from frontend_scanner.api.cli import main

if __name__ == "__main__":
    sys.exit(main())
