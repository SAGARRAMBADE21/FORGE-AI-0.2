"""
Command Line Interface for Backend Agent
"""

import click
import json
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from backend_agent.config import BackendAgentConfig
from backend_agent.workflow.backend_workflow import create_backend_workflow

console = Console()


@click.group()
def cli():
    """Backend Generation Agent CLI"""
    pass


@cli.command()
@click.option('--frontend-manifest', '-f', type=click.Path(exists=True), 
              help='Path to frontend scanner manifest.json')
@click.option('--requirements', '-r', type=str, 
              help='Natural language requirements for backend')
@click.option('--output', '-o', type=click.Path(), default='./generated-backend',
              help='Output directory for generated code')
@click.option('--language', type=click.Choice(['auto', 'node', 'python']), default='auto',
              help='Backend language')
@click.option('--framework', type=click.Choice(['auto', 'express', 'fastapi', 'nestjs']), default='auto',
              help='Backend framework')
@click.option('--database', type=click.Choice(['auto', 'postgresql', 'mongodb', 'mysql']), default='auto',
              help='Database type')
@click.option('--config', '-c', type=click.Path(exists=True),
              help='Path to backend-config.yaml')
def generate(frontend_manifest, requirements, output, language, framework, database, config):
    """Generate backend code from frontend manifest and requirements."""
    
    console.print("[bold blue]🚀 Backend Generation Agent[/bold blue]")
    console.print()
    
    # Load configuration
    if config:
        import yaml
        with open(config) as f:
            config_data = yaml.safe_load(f)
        agent_config = BackendAgentConfig(**config_data)
    else:
        agent_config = BackendAgentConfig()
    
    # Override with CLI options
    agent_config.project.output_dir = Path(output)
    if language != 'auto':
        agent_config.stack.language = language
    if framework != 'auto':
        agent_config.stack.framework = framework
    if database != 'auto':
        agent_config.stack.database = database
    
    # Load frontend manifest
    if frontend_manifest:
        with open(frontend_manifest) as f:
            manifest = json.load(f)
        console.print(f"✓ Loaded frontend manifest: {frontend_manifest}")
    else:
        console.print("[yellow]⚠ No frontend manifest provided, using empty manifest[/yellow]")
        manifest = {"routes": [], "api_calls": [], "components": []}
    
    # Requirements
    if not requirements:
        requirements = "Generate a REST API backend"
    
    console.print(f"✓ Requirements: {requirements[:100]}...")
    console.print()
    
    # Create workflow
    workflow = create_backend_workflow()
    
    # Initial state
    initial_state = {
        "frontend_manifest": manifest,
        "user_requirements": requirements,
        "config": agent_config.model_dump(),
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
        "workflow_stage": "initialized",
        "timestamp": ""
    }
    
    # Execute with progress
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Generating backend...", total=None)
        
        try:
            result = workflow.invoke(initial_state)
            progress.update(task, completed=True)
        except Exception as e:
            console.print(f"[bold red]✗ Error: {e}[/bold red]")
            raise
    
    # Display results
    console.print()
    console.print("[bold green]✅ Backend Generation Complete![/bold green]")
    console.print()
    
    # Summary table
    table = Table(title="Generation Summary")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Output Directory", str(result['config']['project']['output_dir']))
    table.add_row("Language", result['selected_stack']['language'])
    table.add_row("Framework", result['selected_stack']['framework'])
    table.add_row("Database", result['selected_stack']['database'])
    table.add_row("Files Generated", str(len(result['integrated_code'])))
    table.add_row("Endpoints", str(len(result['required_endpoints'])))
    table.add_row("Data Models", str(len(result['data_models'])))
    
    console.print(table)
    console.print()
    
    # Next steps
    console.print("[bold]Next Steps:[/bold]")
    console.print("1. cd " + str(result['config']['project']['output_dir']))
    
    if result['selected_stack']['language'] == 'node':
        console.print("2. npm install")
        console.print("3. cp .env.example .env  (and configure)")
        console.print("4. npm run dev")
    else:
        console.print("2. pip install -r requirements.txt")
        console.print("3. cp .env.example .env  (and configure)")
        console.print("4. uvicorn app.main:app --reload")
    
    console.print()


@cli.command()
@click.option('--output', '-o', type=click.Path(), default='./backend-config.yaml',
              help='Output path for config file')
def init(output):
    """Initialize backend-config.yaml"""
    
    config = BackendAgentConfig()
    
    import yaml
    with open(output, 'w') as f:
        yaml.dump(config.model_dump(), f, default_flow_style=False)
    
    console.print(f"[green]✓ Created configuration file: {output}[/green]")
    console.print("Edit this file to customize your backend generation.")


@cli.command()
def version():
    """Show version information"""
    from backend_agent import __version__
    console.print(f"Backend Agent v{__version__}")


def main():
    """Entry point for CLI."""
    cli()


if __name__ == "__main__":
    main()
