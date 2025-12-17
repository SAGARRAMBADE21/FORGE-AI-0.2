#!/usr/bin/env python3
"""
FORGE AI - Complete Pipeline
Scan frontend → Generate backend

Usage:
    python forge_pipeline.py <frontend_project_path> [--requirements "Custom backend requirements"]
    python forge_pipeline.py ./my-react-app
    python forge_pipeline.py ./my-react-app --requirements "Create REST API with authentication"
"""

import sys
import json
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.panel import Panel
from rich.table import Table
import click

# Add to path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "BACKEND - GENERATOR"))

from frontend_scanner.config import ScannerConfig
from frontend_scanner.workflows.scanner_graph import create_scanner_workflow

console = Console()


def scan_frontend(project_path: str, output_dir: str = "./scanner_output") -> dict:
    """
    Step 1: Scan frontend project
    Returns manifest data
    """
    console.print("\n[bold cyan]📡 STEP 1: Scanning Frontend Project[/bold cyan]\n")
    
    # Create config
    config = ScannerConfig(
        project_root=project_path,
        output_dir=output_dir
    )
    
    # Create and run workflow
    workflow = create_scanner_workflow(config)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console
    ) as progress:
        task = progress.add_task("Scanning files...", total=None)
        
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
        
        progress.update(task, completed=100)
    
    # Load manifest
    manifest_path = Path(output_dir) / "manifest.json"
    if manifest_path.exists():
        with open(manifest_path) as f:
            manifest = json.load(f)
        
        console.print(f"[green]✓[/green] Frontend scan complete!")
        console.print(f"  → Framework: {manifest.get('framework', 'unknown')}")
        console.print(f"  → Components: {len(manifest.get('components', []))}")
        console.print(f"  → Routes: {len(manifest.get('routes', []))}")
        console.print(f"  → API Calls: {len(manifest.get('api_calls', []))}")
        console.print(f"  → Output: {manifest_path.absolute()}\n")
        
        return manifest
    else:
        console.print("[red]✗[/red] Failed to generate manifest\n")
        return {}


def generate_backend(manifest: dict, requirements: str, output_dir: str = "./generated-backend") -> dict:
    """
    Step 2: Generate backend from manifest
    """
    console.print("[bold cyan]⚙️  STEP 2: Generating Backend Code[/bold cyan]\n")
    
    try:
        from backend_agent.config import BackendAgentConfig
        from backend_agent.workflow.backend_workflow import create_backend_workflow
        
        # Create config
        config = BackendAgentConfig()
        config.project.output_dir = Path(output_dir)
        
        # Detect stack from frontend
        framework = manifest.get('framework', '').lower()
        if 'react' in framework or 'vue' in framework or 'angular' in framework:
            console.print(f"[dim]Detected frontend: {framework}[/dim]")
        
        console.print(f"[dim]Requirements: {requirements[:100]}...[/dim]\n")
        
        # Create workflow
        workflow = create_backend_workflow()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Generating backend...", total=None)
            
            # Initial state
            initial_state = {
                "frontend_manifest": manifest,
                "user_requirements": requirements,
                "config": config.model_dump(),
                "existing_backend": None,
                "parsed_requirements": {},
                "required_endpoints": [],
                "data_models": [],
                "selected_stack": {},
                "architecture_plan": {},
                "database_schema": {},
                "orm_models": {},
                "migrations": [],
                "api_routes": {},
                "controllers": {},
                "validation_schemas": {},
                "auth_system": {},
                "services": {},
                "tests": {},
                "docker_config": {},
                "cicd_config": {},
                "integrated_code": {},
                "frontend_client": "",
                "documentation": "",
                "project_structure": {},
                "dependencies": {},
                "env_variables": {},
                "logs": [],
                "errors": [],
                "workflow_stage": "init",
                "timestamp": ""
            }
            
            result = workflow.invoke(initial_state)
            progress.update(task, completed=100)
        
        console.print(f"[green]✓[/green] Backend generation complete!")
        console.print(f"  → Language: {result.get('selected_stack', {}).get('language', 'N/A')}")
        console.print(f"  → Framework: {result.get('selected_stack', {}).get('framework', 'N/A')}")
        console.print(f"  → Database: {result.get('selected_stack', {}).get('database', 'N/A')}")
        console.print(f"  → Output: {output_dir}\n")
        
        return result
        
    except ImportError as e:
        console.print(f"[red]✗[/red] Backend generator not available: {e}")
        console.print("[yellow]Make sure backend dependencies are installed:[/yellow]")
        console.print("[yellow]  cd 'BACKEND - GENERATOR' && pip install -r requirements.txt[/yellow]\n")
        return {}


def display_summary(manifest: dict, backend_result: dict):
    """Display final summary"""
    console.print("\n[bold green]✅ Pipeline Complete![/bold green]\n")
    
    table = Table(title="Generation Summary", show_header=True, header_style="bold magenta")
    table.add_column("Stage", style="cyan")
    table.add_column("Output", style="green")
    table.add_column("Details")
    
    # Frontend scan
    table.add_row(
        "Frontend Scan",
        "✓ Complete",
        f"{len(manifest.get('components', []))} components, {len(manifest.get('routes', []))} routes"
    )
    
    # Backend generation
    if backend_result:
        stack = backend_result.get('selected_stack', {})
        table.add_row(
            "Backend Generation",
            "✓ Complete",
            f"{stack.get('framework', 'N/A')} + {stack.get('database', 'N/A')}"
        )
    else:
        table.add_row(
            "Backend Generation",
            "⚠ Skipped",
            "Backend generator not run"
        )
    
    console.print(table)
    console.print()


@click.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.option('--requirements', '-r', default="Create a complete REST API backend with authentication",
              help='Backend requirements in natural language')
@click.option('--scan-output', default='./scanner_output',
              help='Frontend scan output directory')
@click.option('--backend-output', default='./generated-backend',
              help='Backend code output directory')
@click.option('--scan-only', is_flag=True,
              help='Only scan frontend, skip backend generation')
def main(project_path, requirements, scan_output, backend_output, scan_only):
    """
    FORGE AI Pipeline - Scan frontend and generate backend
    
    Examples:
        forge_pipeline.py ./my-react-app
        forge_pipeline.py ./my-vue-app --requirements "Create GraphQL API"
        forge_pipeline.py ./frontend --scan-only
    """
    console.print(Panel.fit(
        "[bold blue]🔥 FORGE AI - Full Stack Generator[/bold blue]\n"
        "Scan Frontend → Generate Backend",
        border_style="blue"
    ))
    
    # Validate project path
    project = Path(project_path)
    if not project.exists():
        console.print(f"[red]Error:[/red] Project path does not exist: {project_path}")
        sys.exit(1)
    
    console.print(f"\n[bold]Project:[/bold] {project.absolute()}")
    console.print(f"[bold]Requirements:[/bold] {requirements}\n")
    
    # Step 1: Scan Frontend
    manifest = scan_frontend(str(project), scan_output)
    
    if not manifest:
        console.print("[red]Frontend scan failed. Exiting.[/red]")
        sys.exit(1)
    
    # Step 2: Generate Backend (unless scan-only)
    backend_result = {}
    if not scan_only:
        backend_result = generate_backend(manifest, requirements, backend_output)
    else:
        console.print("[yellow]⚠ Backend generation skipped (--scan-only flag)[/yellow]\n")
    
    # Display summary
    display_summary(manifest, backend_result)
    
    # Next steps
    console.print("[bold cyan]📝 Next Steps:[/bold cyan]\n")
    console.print(f"1. Review scanned frontend: {scan_output}/manifest.json")
    if backend_result:
        console.print(f"2. Review generated backend: {backend_output}/")
        console.print(f"3. Install dependencies and run backend")
        console.print(f"4. Connect frontend to backend API\n")
    else:
        console.print(f"2. Generate backend: python forge_pipeline.py {project_path} (without --scan-only)\n")


if __name__ == "__main__":
    main()
