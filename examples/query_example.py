"""Example of querying the vector store."""
import os
from pathlib import Path
from frontend_scanner.config import ScannerConfig
from frontend_scanner.storage.vector_store import VectorStoreFactory
from rich.console import Console
from rich.table import Table

console = Console()


def main():
    """Query the vector store for semantic search."""
    console.print("\n[bold blue]🔍 Vector Store Query Example[/bold blue]\n")
    
    # Check if OPENAI_API_KEY is set
    if not os.getenv("OPENAI_API_KEY"):
        console.print("[red]Error: OPENAI_API_KEY not set[/red]")
        console.print("Set it in .env file or environment variables\n")
        return
    
    # Configure
    config = ScannerConfig(
        project_root=Path("."),
        output_dir=Path("./scan-output")
    )
    
    try:
        # Load vector store
        console.print("[yellow]Loading vector store...[/yellow]")
        vector_store = VectorStoreFactory.create(config)
        
        # Get embeddings
        from langchain_openai import OpenAIEmbeddings
        embedder = OpenAIEmbeddings()
        
        # Query
        query = "Which components fetch API data?"
        console.print(f"\n[cyan]Query:[/cyan] {query}\n")
        
        query_embedding = embedder.embed_query(query)
        results = vector_store.query(query_embedding, k=5)
        
        if not results:
            console.print("[yellow]No results found. Make sure you've run a scan first.[/yellow]\n")
            return
        
        # Display results
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("File", style="cyan", width=40)
        table.add_column("Lines", style="white", width=10)
        table.add_column("Type", style="green", width=15)
        table.add_column("Distance", style="yellow", width=10)
        
        for result in results:
            metadata = result.get("metadata", {})
            file_path = Path(metadata.get("file_path", "unknown")).name
            lines = metadata.get("lines", "")
            chunk_type = metadata.get("chunk_type", "")
            distance = f"{result.get('distance', 0):.3f}"
            
            table.add_row(file_path, lines, chunk_type, distance)
        
        console.print(table)
        console.print()
        
        # Show first result content
        if results:
            console.print("[cyan]Top Result Content:[/cyan]")
            console.print(f"[dim]{results[0]['content'][:300]}...[/dim]\n")
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]\n")


if __name__ == "__main__":
    main()
