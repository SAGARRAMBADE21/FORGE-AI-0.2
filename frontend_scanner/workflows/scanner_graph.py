"""LangGraph workflow orchestrating all scanner agents."""
from typing import TypedDict, Annotated, Any, List
import operator

try:
    from langgraph.graph import StateGraph, END, START
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    print("Error: LangGraph not available. Install: pip install langgraph")

from frontend_scanner.agents.filewalker import FileWalkerAgent
from frontend_scanner.agents.parser import ParserAgent
from frontend_scanner.agents.chunker import ChunkerAgent
from frontend_scanner.agents.embedder import EmbedderAgent
from frontend_scanner.agents.summarizer import SummarizerAgent
from frontend_scanner.agents.indexer import IndexerAgent
from frontend_scanner.agents.redactor import RedactorAgent
from frontend_scanner.agents.exporter import ExporterAgent


class ScannerState(TypedDict):
    """Global state for scanner workflow."""
    config: Any
    file_inventory: Any
    parsed_files: Annotated[List, operator.add]
    chunks: Annotated[List, operator.add]
    embeddings: Annotated[List, operator.add]
    summaries: Annotated[List, operator.add]
    manifest: Any
    vector_index: Any
    logs: Annotated[List, operator.add]


def create_scanner_workflow(config):
    """Create the LangGraph workflow for frontend scanning."""
    
    if not LANGGRAPH_AVAILABLE:
        raise ImportError("LangGraph is required. Install: pip install langgraph")
    
    # Ensure directories exist
    config.ensure_directories()
    
    # Initialize agents
    filewalker = FileWalkerAgent(config)
    parser = ParserAgent(config)
    chunker = ChunkerAgent(config)
    redactor = RedactorAgent(config)
    embedder = EmbedderAgent(config)
    summarizer = SummarizerAgent(config)
    indexer = IndexerAgent(config)
    exporter = ExporterAgent(config)
    
    # Node functions
    def filewalker_node(state: ScannerState) -> dict:
        """Walk directory tree and collect file inventory."""
        print("\n" + "="*60)
        print("🚶 STEP 1: FileWalker - Scanning project directory")
        print("="*60)
        
        inventory = filewalker.scan()
        
        print(f"\n✓ Scanned {inventory.total_files} files")
        print(f"✓ Total size: {inventory.total_size_bytes / 1024 / 1024:.2f} MB")
        
        if inventory.errors:
            print(f"⚠ {len(inventory.errors)} errors encountered")
        
        return {
            "file_inventory": inventory,
            "logs": [f"Scanned {inventory.total_files} files"]
        }
    
    def parser_chunker_node(state: ScannerState) -> dict:
        """Parse and chunk all files (combined node)."""
        print("\n" + "="*60)
        print("🔍 STEP 2: Parser & Chunker - Analyzing files")
        print("="*60)
        
        parsed_files = []
        all_chunks = []
        
        file_count = 0
        for file_meta in state["file_inventory"].files:
            if file_meta.is_binary:
                continue
            
            try:
                # Read file
                with open(file_meta.path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Parse
                parsed = parser.parse(file_meta.path, content)
                parsed_files.append(parsed)
                
                # Chunk
                chunks = chunker.chunk(parsed, content)
                all_chunks.extend(chunks)
                
                file_count += 1
                if file_count % 10 == 0:
                    print(f"  Processed {file_count}/{len(state['file_inventory'].files)} files")
            
            except Exception as e:
                print(f"  Error processing {file_meta.path}: {e}")
                continue
        
        print(f"\n✓ Parsed {len(parsed_files)} files")
        print(f"✓ Generated {len(all_chunks)} chunks")
        
        return {
            "parsed_files": parsed_files,
            "chunks": all_chunks,
            "logs": [
                f"Parsed {len(parsed_files)} files",
                f"Generated {len(all_chunks)} chunks"
            ]
        }
    
    def redactor_node(state: ScannerState) -> dict:
        """Redact secrets from chunks."""
        print("\n" + "="*60)
        print("🔒 STEP 3: Redactor - Sanitizing sensitive data")
        print("="*60)
        
        redacted_chunks = []
        
        for chunk in state["chunks"]:
            redacted = redactor.redact(chunk)
            redacted_chunks.append(redacted)
        
        print(f"✓ Redacted {len(redacted_chunks)} chunks")
        
        return {
            "chunks": redacted_chunks,
            "logs": [f"Redacted {len(redacted_chunks)} chunks"]
        }
    
    def embedder_node(state: ScannerState) -> dict:
        """Generate embeddings for chunks."""
        print("\n" + "="*60)
        print("🧠 STEP 4: Embedder - Generating vector embeddings")
        print("="*60)
        
        embeddings = embedder.embed_chunks(state["chunks"])
        
        return {
            "embeddings": embeddings,
            "logs": [f"Generated {len(embeddings)} embeddings"]
        }
    
    def summarizer_node(state: ScannerState) -> dict:
        """Generate hierarchical summaries."""
        print("\n" + "="*60)
        print("📝 STEP 5: Summarizer - Creating summaries")
        print("="*60)
        
        summaries = summarizer.generate_summaries(
            state["parsed_files"],
            state["chunks"]
        )
        
        return {
            "summaries": [summaries],
            "logs": [
                f"Generated {len(summaries.get('file_summaries', []))} file summaries"
            ]
        }
    
    def indexer_node(state: ScannerState) -> dict:
        """Build vector index."""
        print("\n" + "="*60)
        print("📊 STEP 6: Indexer - Building vector index & manifest")
        print("="*60)
        
        # Get summaries (take the first one since it's a list with one item)
        summaries = state["summaries"][0] if state["summaries"] else {}
        
        vector_index = indexer.build_index(
            state["chunks"],
            state["embeddings"],
            summaries
        )
        
        manifest = indexer.build_manifest(
            state["file_inventory"],
            state["parsed_files"],
            summaries
        )
        
        return {
            "vector_index": vector_index,
            "manifest": manifest,
            "logs": ["Vector index built", "Manifest generated"]
        }
    
    def exporter_node(state: ScannerState) -> dict:
        """Export results."""
        print("\n" + "="*60)
        print("💾 STEP 7: Exporter - Saving results")
        print("="*60)
        
        summaries = state["summaries"][0] if state["summaries"] else {}
        
        exporter.export(
            state["manifest"],
            summaries,
            state["vector_index"],
            state["file_inventory"]
        )
        
        return {
            "logs": ["Results exported successfully"]
        }
    
    # Build graph
    workflow = StateGraph(ScannerState)
    
    # Add nodes
    workflow.add_node("filewalker", filewalker_node)
    workflow.add_node("parser_chunker", parser_chunker_node)
    workflow.add_node("redactor", redactor_node)
    workflow.add_node("embedder", embedder_node)
    workflow.add_node("summarizer", summarizer_node)
    workflow.add_node("indexer", indexer_node)
    workflow.add_node("exporter", exporter_node)
    
    # Add edges (linear workflow)
    workflow.add_edge(START, "filewalker")
    workflow.add_edge("filewalker", "parser_chunker")
    workflow.add_edge("parser_chunker", "redactor")
    workflow.add_edge("redactor", "embedder")
    workflow.add_edge("embedder", "summarizer")
    workflow.add_edge("summarizer", "indexer")
    workflow.add_edge("indexer", "exporter")
    workflow.add_edge("exporter", END)
    
    return workflow.compile()
