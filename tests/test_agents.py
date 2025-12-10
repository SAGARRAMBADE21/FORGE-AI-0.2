"""Tests for scanner agents."""
import pytest
from pathlib import Path
from frontend_scanner.config import ScannerConfig
from frontend_scanner.agents.filewalker import FileWalkerAgent
from frontend_scanner.agents.parser import ParserAgent
from frontend_scanner.agents.chunker import ChunkerAgent
from frontend_scanner.agents.redactor import RedactorAgent


@pytest.fixture
def config(tmp_path):
    """Create test config."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    
    # Create a simple test file
    test_file = project_dir / "test.js"
    test_file.write_text("function test() { return 'hello'; }")
    
    return ScannerConfig(
        project_root=project_dir,
        output_dir=tmp_path / "output"
    )


def test_filewalker_agent(config):
    """Test FileWalker agent."""
    agent = FileWalkerAgent(config)
    inventory = agent.scan()
    
    assert inventory.total_files >= 0
    assert inventory.project_root == str(config.project_root.resolve())


def test_parser_agent(config):
    """Test Parser agent."""
    agent = ParserAgent(config)
    
    sample_code = """
    import React from 'react';
    
    export function MyComponent() {
        const [data, setData] = useState(null);
        
        useEffect(() => {
            fetch('/api/data').then(r => r.json());
        }, []);
        
        return <div>Hello</div>;
    }
    """
    
    parsed = agent.parse("test.tsx", sample_code)
    
    assert parsed.language == "typescript"
    assert len(parsed.api_calls) > 0


def test_chunker_agent(config):
    """Test Chunker agent."""
    agent = ChunkerAgent(config)
    parser = ParserAgent(config)
    
    sample_code = "function test() { return 'hello'; }" * 10
    parsed = parser.parse("test.js", sample_code)
    
    chunks = agent.chunk(parsed, sample_code)
    
    assert len(chunks) > 0
    for chunk in chunks:
        assert chunk.file_path == "test.js"
        assert chunk.content
        assert chunk.token_count > 0


def test_redactor_agent(config):
    """Test Redactor agent."""
    from frontend_scanner.agents.chunker import CodeChunk
    
    agent = RedactorAgent(config)
    
    chunk = CodeChunk(
        chunk_id="test:1",
        file_path="test.js",
        content="const API_KEY = 'sk-1234567890abcdef';",
        start_line=0,
        end_line=1,
        token_count=10,
        chunk_type="text",
        language="javascript",
        metadata={},
        provenance={}
    )
    
    redacted = agent.redact(chunk)
    
    assert "[REDACTED]" in redacted.content
    assert "sk-1234567890abcdef" not in redacted.content
