"""Indexer Agent - Build vector index and manifest."""
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from pydantic import BaseModel, Field


class Manifest(BaseModel):
    """Project manifest."""
    project_root: str
    scan_timestamp: str
    framework: Optional[str] = None
    routes: List[str] = Field(default_factory=list)
    pages: List[str] = Field(default_factory=list)
    components: List[Dict[str, Any]] = Field(default_factory=list)
    api_calls: List[str] = Field(default_factory=list)
    suggested_backend_endpoints: List[str] = Field(default_factory=list)
    integration_hints: Dict[str, Any] = Field(default_factory=dict)
    file_inventory: Dict[str, Any] = Field(default_factory=dict)


class IndexerAgent:
    """Agent that builds vector index and generates manifest."""
    
    def __init__(self, config):
        self.config = config
    
    def build_index(self, chunks: List[Any], embeddings: List[Any], 
                   summaries: Dict[str, Any]) -> Dict[str, Any]:
        """Build vector index with metadata."""
        from frontend_scanner.storage.vector_store import VectorStoreFactory
        
        print("Building vector index...")
        
        try:
            vector_store = VectorStoreFactory.create(self.config)
            
            # Add chunks with embeddings
            for chunk, embedding in zip(chunks, embeddings):
                try:
                    vector_store.add(
                        chunk_id=chunk.chunk_id,
                        embedding=embedding.embedding,
                        content=chunk.content,
                        metadata={
                            "file_path": chunk.file_path,
                            "start_line": chunk.start_line,
                            "end_line": chunk.end_line,
                            "chunk_type": chunk.chunk_type,
                            "language": chunk.language,
                            **chunk.metadata
                        },
                        provenance=chunk.provenance
                    )
                except Exception as e:
                    print(f"Error adding chunk {chunk.chunk_id}: {e}")
                    continue
            
            # Persist
            vector_store.persist()
            
            print(f"✓ Vector index built with {len(embeddings)} embeddings")
            
            return {
                "store": vector_store,
                "total_chunks": len(chunks),
                "total_embeddings": len(embeddings)
            }
        
        except Exception as e:
            print(f"Error building index: {e}")
            return {
                "store": None,
                "total_chunks": 0,
                "total_embeddings": 0
            }
    
    def build_manifest(self, file_inventory: Any,
                      parsed_files: List[Any], 
                      summaries: Dict[str, Any]) -> Manifest:
        """Build project manifest."""
        print("Building manifest...")
        
        project_summary = summaries.get("project_summary")
        
        routes = []
        pages = []
        components = []
        api_calls = set()
        
        for parsed in parsed_files:
            if not parsed:
                continue
            
            try:
                routes.extend(parsed.routes)
                
                for comp in parsed.components:
                    components.append({
                        "name": comp.name,
                        "file": parsed.file_path,
                        "line": comp.start_line,
                        "type": comp.type
                    })
                
                for call in parsed.api_calls:
                    api_calls.add(call.get("url", "")[:100])
            
            except Exception as e:
                print(f"Error processing {parsed.file_path}: {e}")
                continue
        
        manifest = Manifest(
            project_root=str(self.config.project_root),
            scan_timestamp=datetime.now().isoformat(),
            framework=project_summary.framework if project_summary else None,
            routes=list(set(routes)),
            pages=pages,
            components=components[:50],
            api_calls=list(api_calls)[:20],
            suggested_backend_endpoints=(
                project_summary.suggested_backend_endpoints 
                if project_summary else []
            ),
            integration_hints={
                "detected_framework": project_summary.framework if project_summary else None,
                "total_components": len(components),
                "total_routes": len(routes),
                "architecture": project_summary.architecture if project_summary else "Unknown"
            },
            file_inventory={
                "total_files": file_inventory.total_files,
                "total_size_bytes": file_inventory.total_size_bytes,
                "scan_timestamp": file_inventory.scan_timestamp
            }
        )
        
        print(f"✓ Manifest built | Framework: {manifest.framework}")
        return manifest
