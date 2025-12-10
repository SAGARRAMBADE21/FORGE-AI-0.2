#!/usr/bin/env python3
"""Quick scan script - Just provide your project path."""
import sys
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from frontend_scanner import ScannerConfig, create_scanner_workflow

def scan_project(project_path: str, output_dir: str = "./scan-output"):
    """Scan a frontend project."""
    project = Path(project_path)
    
    if not project.exists():
        print(f"Error: Project path does not exist: {project_path}")
        return 1
    
    print(f"Scanning Frontend Project\n")
    print(f"Project: {project.absolute()}")
    print(f"Output: {output_dir}\n")
    
    try:
        # Create configuration
        config = ScannerConfig(
            project_root=project,
            output_dir=Path(output_dir),
        )
        
        # Create and run workflow
        print("Creating scanner workflow...")
        workflow = create_scanner_workflow(config)
        
        print("✓ Starting scan...\n")
        result = workflow.invoke({
            "config": config,
            "file_inventory": None,
            "parsed_files": [],
            "chunks": [],
            "embeddings": [],
            "summaries": [],
            "manifest": None,
            "vector_index": None,
            "logs": []
        })
        
        print(f"\nScan completed!")
        print(f"\nResults saved to: {output_dir}")
        print(f"   - manifest.json (project metadata)")
        print(f"   - file_inventory.json (all scanned files)")
        print(f"   - hierarchical_summaries.json (code summaries)")
        print(f"   - scan_logs.json (scan details)")
        
    except Exception as e:
        print(f"\nError during scan: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scan_project.py <project_path> [output_dir]")
        print("\nExample:")
        print("  python scan_project.py C:\\projects\\my-react-app")
        print("  python scan_project.py ./my-nextjs-project ./results")
        sys.exit(1)
    
    project_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "./scan-output"
    
    sys.exit(scan_project(project_path, output_dir))
