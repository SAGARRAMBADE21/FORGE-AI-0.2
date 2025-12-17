"""
Stack Selector Agent
Chooses optimal tech stack based on requirements.
"""

from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
import json
from backend_agent.utils.llm_factory import create_llm


class StackSelectorAgent:
    """Selects optimal backend technology stack."""
    
    def __init__(self, llm_config: Dict[str, Any]):
        self.llm = create_llm(llm_config)
        
        self.selector_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a backend technology expert. Choose the optimal tech stack.

Consider:
- Frontend framework (React, Vue, Next.js)
- Project complexity
- Performance requirements
- Team expertise (if mentioned)
- ML/AI requirements

Available stacks:
1. Node.js + Express + PostgreSQL + Sequelize
2. Node.js + Express + MongoDB + Mongoose
3. Node.js + NestJS + PostgreSQL + TypeORM
4. Python + FastAPI + PostgreSQL + SQLAlchemy
5. Python + FastAPI + MongoDB + Motor
6. Python + Django + PostgreSQL + Django ORM

Return JSON with: language, framework, database, orm, reasoning"""),
            ("user", """Frontend: {frontend_framework}
Requirements: {requirements}
Config preferences: {config}

Select optimal stack:""")
        ])
    
    def select(self, frontend_manifest: Dict[str, Any], 
               requirements: Dict[str, Any],
               config: Dict[str, str]) -> Dict[str, str]:
        """Select technology stack."""
        
        # Check if user specified preferences
        if config.get("language") != "auto":
            return self._use_config(config)
        
        # Use LLM to decide
        try:
            chain = self.selector_prompt | self.llm
            response = chain.invoke({
                "frontend_framework": frontend_manifest.get("framework", "react"),
                "requirements": json.dumps(requirements),
                "config": json.dumps(config)
            })
            
            selection = json.loads(response.content)
            
            return {
                "language": selection.get("language", "python"),
                "framework": selection.get("framework", "fastapi"),
                "database": selection.get("database", "postgresql"),
                "orm": selection.get("orm", "sqlalchemy"),
                "reasoning": selection.get("reasoning", "")
            }
        
        except Exception as e:
            print(f"Error in stack selection: {e}")
            return self._default_stack(requirements)
    
    def _use_config(self, config: Dict[str, str]) -> Dict[str, str]:
        """Use user-specified configuration."""
        language = config.get("language", "python")
        framework = config.get("framework", "auto")
        database = config.get("database", "auto")
        orm = config.get("orm", "auto")
        
        # Auto-select based on language
        if framework == "auto":
            framework = "express" if language == "node" else "fastapi"
        
        if database == "auto":
            database = "postgresql"
        
        if orm == "auto":
            orm_map = {
                "node": {"postgresql": "sequelize", "mongodb": "mongoose"},
                "python": {"postgresql": "sqlalchemy", "mongodb": "motor"}
            }
            orm = orm_map.get(language, {}).get(database, "sqlalchemy")
        
        return {
            "language": language,
            "framework": framework,
            "database": database,
            "orm": orm,
            "reasoning": "User specified configuration"
        }
    
    def _default_stack(self, requirements: Dict[str, Any]) -> Dict[str, str]:
        """Default stack selection based on requirements."""
        
        # If ML is needed, prefer Python
        if requirements.get("ml_features"):
            return {
                "language": "python",
                "framework": "fastapi",
                "database": "postgresql",
                "orm": "sqlalchemy",
                "reasoning": "Python/FastAPI selected for ML integration"
            }
        
        # If complex relationships, prefer SQL
        if len(requirements.get("entities", [])) > 5:
            return {
                "language": "python",
                "framework": "fastapi",
                "database": "postgresql",
                "orm": "sqlalchemy",
                "reasoning": "SQL database for complex relationships"
            }
        
        # Default: FastAPI + PostgreSQL
        return {
            "language": "python",
            "framework": "fastapi",
            "database": "postgresql",
            "orm": "sqlalchemy",
            "reasoning": "Default high-performance stack"
        }
