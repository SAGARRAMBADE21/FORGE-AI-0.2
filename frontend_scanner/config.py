"""Configuration management for Frontend Scanner."""
from pathlib import Path
from typing import Literal, Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator
import yaml
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class EmbeddingConfig(BaseModel):
    """Embedding configuration."""
    provider: Literal["openai", "local"] = "local"
    model: str = "sentence-transformers/all-MiniLM-L6-v2"
    dimensions: int = 384
    batch_size: int = 100


class VectorStoreConfig(BaseModel):
    """Vector store configuration."""
    backend: Literal["chroma", "faiss"] = "chroma"
    persist_directory: str = "./vector_store"
    collection_name: str = "frontend_code"


class ChunkingConfig(BaseModel):
    """Chunking strategy configuration."""
    chunk_size: int = 1000
    chunk_overlap: int = 200
    use_ast_chunking: bool = True
    min_chunk_size: int = 100


class SecurityConfig(BaseModel):
    """Security and privacy settings."""
    redact_secrets: bool = True
    redact_patterns: List[str] = Field(default_factory=lambda: [
        r"(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*['\"]?[\w\-]+['\"]?",
        r"(?i)bearer\s+[\w\-\.]+",
        r"sk-[a-zA-Z0-9]{20,}",
        r"ghp_[a-zA-Z0-9]{36}",
    ])
    exclude_patterns: List[str] = Field(default_factory=lambda: [
        "node_modules/**",
        ".git/**",
        "dist/**",
        "build/**",
        "*.min.js",
        "coverage/**",
        ".next/**",
        "__pycache__/**",
    ])


class ScannerConfig(BaseModel):
    """Main scanner configuration."""
    project_root: Path
    output_dir: Path
    embedding: EmbeddingConfig = Field(default_factory=EmbeddingConfig)
    vector_store: VectorStoreConfig = Field(default_factory=VectorStoreConfig)
    chunking: ChunkingConfig = Field(default_factory=ChunkingConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    max_file_size_mb: int = 100
    supported_extensions: List[str] = Field(default_factory=lambda: [
        ".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte",
        ".html", ".css", ".json", ".yaml", ".yml"
    ])
    
    @field_validator('project_root', 'output_dir')
    @classmethod
    def resolve_paths(cls, v: Path) -> Path:
        """Resolve paths to absolute."""
        return v.resolve() if isinstance(v, Path) else Path(v).resolve()
    
    @classmethod
    def from_yaml(cls, path: str) -> "ScannerConfig":
        """Load config from YAML file."""
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # Convert string paths to Path objects
        if 'project_root' in data:
            data['project_root'] = Path(data['project_root'])
        if 'output_dir' in data:
            data['output_dir'] = Path(data['output_dir'])
        
        return cls(**data)
    
    def to_yaml(self, path: str):
        """Save config to YAML file."""
        data = self.model_dump(mode='python')
        
        # Convert Path objects to strings
        data['project_root'] = str(data['project_root'])
        data['output_dir'] = str(data['output_dir'])
        
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False)
    
    def ensure_directories(self):
        """Ensure output directories exist."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        Path(self.vector_store.persist_directory).mkdir(parents=True, exist_ok=True)
