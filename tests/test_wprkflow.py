"""Tests for LangGraph workflow."""
import pytest
from pathlib import Path
from frontend_scanner.config import ScannerConfig
from frontend_scanner.workflows.scanner_graph import create_scanner_workflow


@pytest.fixture
def config(tmp_path):
    """Create test config."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    
    # Create test files
    test_file = project_dir / "App.js"
    test_file.write_text("""
    import React from 'react';
    
    function App() {
        return <div>Hello World</div>;
    }
    
    export default App;
    """)
    
    return ScannerConfig(
        project_root=project_dir,
        output_dir=tmp_path / "output"
    )


def test_workflow_creation(config):
    """Test workflow can be created."""
    workflow = create_scanner_workflow(config)
    assert workflow is not None


def test_workflow_execution(config):
    """Test full workflow execution."""
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
    
    assert result is not None
    assert "logs" in result
    assert len(result["logs"]) > 0


def test_workflow_handles_empty_project(tmp_path):
    """Test workflow handles empty project gracefully."""
    empty_dir = tmp_path / "empty_project"
    empty_dir.mkdir()
    
    config = ScannerConfig(
        project_root=empty_dir,
        output_dir=tmp_path / "output"
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
    
    assert result is not None
