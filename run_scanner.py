#!/usr/bin/env python3
"""
Quick start script for Frontend Scanner.

Usage:
    python run_scanner.py <project_path>
    python run_scanner.py ./my-react-app
"""

import sys
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel

# Add parent directory to path to import frontend_scanner
sys.path.insert(0, str(Path(__file__).parent))

from frontend_scanner import ScannerConfig, create_scanner_workflow

console = Console()


def check_environment():
    """Check if environment is properly set up."""
    import os
    
    console.print("\n[bold cyan]🔍 Environment Check[/bold cyan]\n")
    
    checks = {
        "Python Version": sys.version_info >= (3, 10),
        "OPENAI_API_KEY": bool(os.getenv("OPENAI_API_KEY")),
    }
    
    all_passed = True
    for check, passed in checks.items():
        status = "[green]✓[/green]" if passed else "[red]✗[/red]"
        console.print(f"{status} {check}")
        if not passed:
            all_passed = False
    
    console.print()
    
    if not all_passed:
        console.print("[yellow]Warning: Some checks failed. Scanner may not work correctly.[/yellow]")
        console.print("[yellow]Tip: Set OPENAI_API_KEY in .env file[/yellow]\n")
        
        if not Confirm.ask("Continue anyway?"):
            sys.exit(1)
    
    return all_passed


def get_project_path():
    """Get project path from user."""
    if len(sys.argv) > 1:
        project_path = Path(sys.argv[1])
    else:
        path_input = Prompt.ask(
            "\n[cyan]Enter path to frontend project[/cyan]",
            default="./tests/fixtures/sample_react"
        )
        project_path = Path(path_input)
    
    if not project_path.exists():
        console.print(f"\n[red]Error: Path does not exist: {project_path}[/red]\n")
        sys.exit(1)
    
    return project_path


def main():
    """Main function."""
    console.print()
    console.print(Panel.fit(
        "[bold blue]🔍 Frontend Scanner[/bold blue]\n"
        "LangGraph-powered code analysis",
        border_style="blue"
    ))
    
    # Check environment
    check_environment()
    
    # Get project path
    project_path = get_project_path()
    
    # Get output directory
    output_dir = Prompt.ask(
        "[cyan]Output directory[/cyan]",
        default="./scan-output"
    )
    
    # Create config
    console.print("\n[yellow]Initializing scanner...[/yellow]\n")
    
    config = ScannerConfig(
        project_root=project_path,
        output_dir=Path(output_dir)
    )
    
    console.print(f"[cyan]Project:[/cyan] {config.project_root}")
    console.print(f"[cyan]Output:[/cyan] {config.output_dir}")
    console.print(f"[cyan]Embedding:[/cyan] {config.embedding.provider}")
    console.print(f"[cyan]Vector Store:[/cyan] {config.vector_store.backend}\n")
    
    # Confirm
    if not Confirm.ask("Start scan?", default=True):
        console.print("\n[yellow]Scan cancelled[/yellow]\n")
        return
    
    try:
        # Create and run workflow
        workflow = create_scanner_workflow(config)
        
        console.print("\n[bold yellow]Running scan...[/bold yellow]\n")
        
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
        
        # Success
        console.print()
        console.print(Panel.fit(
            "[bold green] Scan Complete![/bold green]",
            border_style="green"
        ))
        console.print()
        
        # Display summary
        if result.get("manifest"):
            manifest = result["manifest"]
            
            console.print("[bold]Summary:[/bold]")
            console.print(f"  • Files: {manifest.file_inventory.get('total_files', 0)}")
            console.print(f"  • Framework: {manifest.framework or 'Unknown'}")
            console.print(f"  • Components: {len(manifest.components)}")
            console.print(f"  • Routes: {len(manifest.routes)}")
            console.print(f"  • API Calls: {len(manifest.api_calls)}")
            console.print()
        
        console.print(f"[green] Results:[/green] {config.output_dir}")
        console.print(f"  • manifest.json")
        console.print(f"  • hierarchical_summaries.json")
        console.print(f"  • file_inventory.json")
        console.print(f"  • scan_logs.json")
        console.print()
        
        # Next steps
        console.print("[bold cyan]Next Steps:[/bold cyan]")
        console.print("  1. Check the manifest: cat scan-output/manifest.json")
        console.print("  2. Query the vector store: python examples/query_example.py")
        console.print("  3. Start the API: python -m frontend_scanner.api.rest_api")
        console.print()
    
    except Exception as e:
        console.print()
        console.print(Panel.fit(
            f"[bold red]  Error:[/bold red]\n{str(e)}",
            border_style="red"
        ))
        console.print()
        sys.exit(1)


if __name__ == "__main__":
    main()
