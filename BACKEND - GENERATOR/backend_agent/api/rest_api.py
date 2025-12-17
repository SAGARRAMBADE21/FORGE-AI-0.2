"""
REST API for Backend Agent
Allows remote code generation via HTTP API.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uuid

from backend_agent.workflow.backend_workflow import create_backend_workflow
from backend_agent.config import BackendAgentConfig

app = FastAPI(title="Backend Generation Agent API", version="1.0.0")

# In-memory job storage (use Redis in production)
jobs = {}


class GenerationRequest(BaseModel):
    """Request model for code generation."""
    frontend_manifest: Dict[str, Any]
    requirements: str
    config: Optional[Dict[str, Any]] = None


class GenerationResponse(BaseModel):
    """Response model for code generation."""
    job_id: str
    status: str
    message: str


@app.post("/generate", response_model=GenerationResponse)
async def generate_backend(request: GenerationRequest, background_tasks: BackgroundTasks):
    """Generate backend code (async)."""
    
    job_id = str(uuid.uuid4())
    
    # Initialize job
    jobs[job_id] = {
        "status": "pending",
        "progress": 0,
        "result": None,
        "error": None
    }
    
    # Start generation in background
    background_tasks.add_task(run_generation, job_id, request)
    
    return GenerationResponse(
        job_id=job_id,
        status="pending",
        message="Generation started"
    )


@app.get("/status/{job_id}")
async def get_status(job_id: str):
    """Get generation job status."""
    
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return jobs[job_id]


@app.get("/download/{job_id}")
async def download_code(job_id: str):
    """Download generated code."""
    
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed")
    
    return job["result"]["integrated_code"]


def run_generation(job_id: str, request: GenerationRequest):
    """Run code generation (background task)."""
    
    try:
        jobs[job_id]["status"] = "running"
        
        # Create workflow
        workflow = create_backend_workflow()
        
        # Load config
        if request.config:
            config = BackendAgentConfig(**request.config)
        else:
            config = BackendAgentConfig()
        
        # Initial state
        initial_state = {
            "frontend_manifest": request.frontend_manifest,
            "user_requirements": request.requirements,
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
            "workflow_stage": "initialized",
            "timestamp": ""
        }
        
        # Execute
        result = workflow.invoke(initial_state)
        
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["result"] = result
        jobs[job_id]["progress"] = 100
        
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
