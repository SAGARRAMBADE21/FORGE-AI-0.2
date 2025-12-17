"""REST API for Frontend Scanner."""
from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pathlib import Path
from typing import Optional, Dict, Any
import json

from frontend_scanner.config import ScannerConfig
from frontend_scanner.workflows.scanner_graph import create_scanner_workflow
from frontend_scanner.storage.vector_store import VectorStoreFactory

app = FastAPI(
    title="Frontend Scanner API",
    version="1.0.0",
    description="LangGraph-powered frontend code scanner"
)


class ScanRequest(BaseModel):
    """Request model for scan."""
    path: str
    output_dir: str = "./scan-output"


class QueryRequest(BaseModel):
    """Request model for semantic query."""
    query: str
    k: int = 5
    filters: Optional[Dict[str, Any]] = None


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Frontend Scanner API",
        "version": "1.0.0",
        "endpoints": {
            "scan": "POST /scan",
            "manifest": "GET /manifest",
            "query": "POST /query",
            "file_ast": "GET /file/{path}/ast"
        }
    }


@app.post("/scan")
async def scan_project(request: ScanRequest):
    """Start a scan of a frontend project."""
    try:
        # Validate path exists
        project_path = Path(request.path)
        if not project_path.exists():
            raise HTTPException(
                status_code=400, 
                detail=f"Project path does not exist: {request.path}"
            )
        
        if not project_path.is_dir():
            raise HTTPException(
                status_code=400, 
                detail=f"Path is not a directory: {request.path}"
            )
        
        config = ScannerConfig(
            project_root=project_path,
            output_dir=Path(request.output_dir)
        )
        
        workflow = create_scanner_workflow(config)
        
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
        
        manifest = result.get("manifest")
        
        return JSONResponse({
            "status": "success",
            "manifest": manifest.model_dump() if manifest else {},
            "logs": result.get("logs", [])
        })
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/manifest")
async def get_manifest(output_dir: str = "./scan-output"):
    """Get the manifest.json from a completed scan."""
    try:
        manifest_path = Path(output_dir) / "manifest.json"
        
        if not manifest_path.exists():
            raise HTTPException(
                status_code=404, 
                detail=f"Manifest not found at {manifest_path}"
            )
        
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        return JSONResponse(manifest)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading manifest: {str(e)}")


@app.post("/query")
async def semantic_query(request: QueryRequest):
    """Perform semantic search on scanned codebase."""
    try:
        # Load config (assumes default path)
        config = ScannerConfig(
            project_root=Path("."),
            output_dir=Path("./scan-output")
        )
        
        vector_store = VectorStoreFactory.create(config)
        
        # Get query embedding based on configured provider
        try:
            if config.embedding.provider == "openai":
                from langchain_openai import OpenAIEmbeddings
                embedder = OpenAIEmbeddings()
            else:
                from langchain_community.embeddings import HuggingFaceEmbeddings
                embedder = HuggingFaceEmbeddings(
                    model_name=config.embedding.model
                )
            
            query_embedding = embedder.embed_query(request.query)
        except ImportError as ie:
            raise HTTPException(
                status_code=500, 
                detail=f"Embedding provider not available: {str(ie)}"
            )
        
        # Search
        results = vector_store.query(
            query_embedding,
            k=request.k,
            filters=request.filters
        )
        
        return JSONResponse({
            "query": request.query,
            "results": results
        })
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/file/{path:path}/ast")
async def get_file_ast(path: str, output_dir: str = "./scan-output"):
    """Get AST summary for a specific file."""
    try:
        summaries_path = Path(output_dir) / "hierarchical_summaries.json"
        
        if not summaries_path.exists():
            raise HTTPException(status_code=404, detail="Summaries not found")
        
        with open(summaries_path, 'r', encoding='utf-8') as f:
            summaries = json.load(f)
        
        # Find file summary
        file_summaries = summaries.get("file_summaries", [])
        
        for file_summary in file_summaries:
            if path in file_summary.get("file_path", ""):
                return JSONResponse(file_summary)
        
        raise HTTPException(status_code=404, detail=f"File '{path}' not found in summaries")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file AST: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
