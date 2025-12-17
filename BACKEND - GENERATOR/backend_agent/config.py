"""
Configuration management for Backend Agent.
"""

from pathlib import Path
from typing import Optional, List, Literal
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
import yaml


class ProjectConfig(BaseModel):
    """Project configuration."""
    name: str = "generated-backend"
    output_dir: Path = Path("./generated-backend")


class StackConfig(BaseModel):
    """Tech stack configuration."""
    language: Literal["auto", "node", "python"] = "auto"
    framework: Literal["auto", "express", "fastapi", "nestjs", "django"] = "auto"
    database: Literal["auto", "postgresql", "mysql", "mongodb", "sqlite"] = "auto"
    orm: Literal["auto", "sequelize", "prisma", "typeorm", "sqlalchemy", "mongoose"] = "auto"


class ArchitectureConfig(BaseModel):
    """Architecture configuration."""
    style: Literal["monolith", "microservices"] = "monolith"
    api_style: Literal["rest", "graphql", "both"] = "rest"


class DatabaseConfig(BaseModel):
    """Database configuration."""
    migrations: bool = True
    seeding: bool = True
    connection_pooling: bool = True


class AuthConfig(BaseModel):
    """Authentication configuration."""
    enabled: bool = True
    method: Literal["jwt", "oauth2", "session"] = "jwt"
    providers: List[str] = Field(default_factory=list)


class FeaturesConfig(BaseModel):
    """Features configuration."""
    ml_integration: bool = False
    external_services: List[str] = Field(default_factory=list)
    message_queue: bool = False
    caching: bool = True
    rate_limiting: bool = True


class GenerationConfig(BaseModel):
    """Code generation configuration."""
    include_comments: bool = True
    include_tests: bool = True
    include_docs: bool = True
    code_style: Literal["prettier", "eslint", "black"] = "prettier"


class DeploymentConfig(BaseModel):
    """Deployment configuration."""
    docker: bool = True
    ci_cd: Literal["github_actions", "gitlab_ci", "jenkins", "none"] = "github_actions"
    environment: Literal["development", "staging", "production"] = "development"


class LLMConfig(BaseModel):
    """LLM configuration."""
    provider: Literal["openai", "groq"] = "groq"  # Default to Groq
    model: str = "llama-3.3-70b-versatile"  # Groq model
    openai_model: str = "gpt-4o-mini"  # OpenAI model for future use
    temperature: float = 0.1
    openai_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None


class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    structured: bool = True
    format: Literal["json", "text"] = "json"


class BackendAgentConfig(BaseSettings):
    """Main configuration for Backend Agent."""
    
    project: ProjectConfig = Field(default_factory=ProjectConfig)
    stack: StackConfig = Field(default_factory=StackConfig)
    architecture: ArchitectureConfig = Field(default_factory=ArchitectureConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    auth: AuthConfig = Field(default_factory=AuthConfig)
    features: FeaturesConfig = Field(default_factory=FeaturesConfig)
    generation: GenerationConfig = Field(default_factory=GenerationConfig)
    deployment: DeploymentConfig = Field(default_factory=DeploymentConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    
    class Config:
        env_prefix = "BACKEND_AGENT_"
        case_sensitive = False
    
    @classmethod
    def from_yaml(cls, path: Path) -> "BackendAgentConfig":
        """Load configuration from YAML file."""
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        return cls(**data)
    
    def to_yaml(self, path: Path):
        """Save configuration to YAML file."""
        with open(path, 'w') as f:
            yaml.dump(self.model_dump(), f, default_flow_style=False)


# Default configuration instance
default_config = BackendAgentConfig()
