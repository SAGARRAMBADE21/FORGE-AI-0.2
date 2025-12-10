"""CLI interface for Frontend Scanner."""
import click
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import sys

from frontend_scanner.config import ScannerConfig
from frontend_scanner.workflows.scanner_graph import create_scanner_workflow

console = Console()


@click.command()
@click.option('--path', required=True, type=click.Path(exists=True),
              help='Path to frontend project root')
@click.option('--out', default='./scan-output', type=click.Path(),
              help='Output directory for scan results')
@click.option('--config', type=click.Path(exists=True),
              help='Path to scan-config.yaml')
@click.option('--incremental', is_flag=True,
              help='Perform incremental scan (not yet implemented)')
def main(path, out, config, incremental):
    """Frontend Scanner CLI - Scan and analyze frontend projects."""
    
    # Print header
    console.print()
    console.print(Panel.fit(
        "[bold blue]🔍 Frontend Scanner[/bold blue]\n"
        "LangGraph-powered code analysis for AI agents",
        border_style="blue"
    ))
    console.print()
    
    try:
        # Load config
        if config:
            scanner_config = ScannerConfig.from_yaml(config)
            scanner_config.project_root = Path(path)
            scanner_config.output_dir = Path(out)
        else:
            scanner_config = ScannerConfig(
                project_root=Path(path),
                output_dir=Path(out)
            )
        
        # Display config
        table = Table(show_header=False, box=None)
        table.add_column("", style="cyan")
        table.add_column("", style="white")
        
        table.add_row("📁 Project Root", str(scanner_config.project_root))
        table.add_row("💾 Output Dir", str(scanner_config.output_dir))
        table.add_row("🧠 Embedding", f"{scanner_config.embedding.provider} ({scanner_config.embedding.model})")
        table.add_row("📊 Vector Store", scanner_config.vector_store.backend)
        
        console.print(table)
        console.print()
        
        # Create and execute workflow
        console.print("[yellow]Starting scan...[/yellow]\n")
        
        workflow = create_scanner_workflow(scanner_config)
        
        result = workflow.invoke({
            "config": scanner_config,
            "file_inventory": None,
            "parsed_files": [],
            "chunks": [],
            "embeddings": [],
            "summaries": [],
            "manifest": None,
            "vector_index": None,
            "logs": []
        })
        
        # Display results
        console.print()
        console.print(Panel.fit(
            "[bold green]✅ Scan Complete![/bold green]",
            border_style="green"
        ))
        console.print()
        
        if result.get("manifest"):
            manifest = result["manifest"]
            
            results_table = Table(show_header=True, header_style="bold magenta")
            results_table.add_column("Metric", style="cyan")
            results_table.add_column("Value", style="white")
            
            results_table.add_row(
                "Total Files",
                str(manifest.file_inventory.get("total_files", 0))
            )
            results_table.add_row(
                "Framework",
                manifest.framework or "Unknown"
            )
            results_table.add_row(
                "Routes",
                str(len(manifest.routes))
            )
            results_table.add_row(
                "Components",
                str(len(manifest.components))
            )
            results_table.add_row(
                "API Calls",
                str(len(manifest.api_calls))
            )
            
            console.print(results_table)
            console.print()
        
        console.print(f"[green]📊 Results saved to:[/green] {scanner_config.output_dir}")
        console.print()
        
        # Display logs
        if result.get("logs"):
            console.print("[dim]Scan logs:[/dim]")
            for log in result["logs"]:
                console.print(f"  [dim]• {log}[/dim]")
        
        console.print()
        return 0
    
    except Exception as e:
        console.print()
        console.print(Panel.fit(
            f"[bold red]❌ Error: {str(e)}[/bold red]",
            border_style="red"
        ))
        console.print()
        return 1


if __name__ == '__main__':
    sys.exit(main())
