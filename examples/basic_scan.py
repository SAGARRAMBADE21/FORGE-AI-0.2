"""Basic example of using Frontend Scanner."""
from pathlib import Path
from frontend_scanner import ScannerConfig, create_scanner_workflow
from rich.console import Console

console = Console()


def main():
    """Run a basic scan."""
    console.print("\n[bold blue]🔍 Frontend Scanner - Basic Example[/bold blue]\n")
    
    # Configure scanner
    config = ScannerConfig(
        project_root=Path("./tests/fixtures/sample_react"),
        output_dir=Path("./scan-output")
    )
    
    console.print(f"📁 Project: {config.project_root}")
    console.print(f"💾 Output: {config.output_dir}\n")
    
    # Create workflow
    console.print("[yellow]Creating workflow...[/yellow]")
    workflow = create_scanner_workflow(config)
    
    # Execute scan
    console.print("[yellow]Starting scan...[/yellow]\n")
    
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
    
    # Print results
    console.print("\n[bold green]✅ Scan Complete![/bold green]\n")
    
    if result.get("manifest"):
        manifest = result["manifest"]
        console.print(f"[cyan]📊 Total Files:[/cyan] {manifest.file_inventory['total_files']}")
        console.print(f"[cyan]🎯 Framework:[/cyan] {manifest.framework}")
        console.print(f"[cyan]🛣️  Routes:[/cyan] {len(manifest.routes)}")
        console.print(f"[cyan]📦 Components:[/cyan] {len(manifest.components)}")
        console.print(f"[cyan]🔌 API Calls:[/cyan] {len(manifest.api_calls)}")
        
        if manifest.suggested_backend_endpoints:
            console.print(f"\n[cyan]💡 Suggested Backend Endpoints:[/cyan]")
            for endpoint in manifest.suggested_backend_endpoints:
                console.print(f"   • {endpoint}")
    
    console.print(f"\n[green]Results saved to:[/green] {config.output_dir}\n")


if __name__ == "__main__":
    main()
