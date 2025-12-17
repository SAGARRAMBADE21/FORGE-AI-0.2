"""
Architecture Planner Agent
Designs project architecture (monolith vs microservices).
"""

from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
import json
from backend_agent.utils.llm_factory import create_llm


class ArchitecturePlannerAgent:
    """Plans backend architecture."""
    
    def __init__(self, llm_config: Dict[str, Any]):
        self.llm = create_llm(llm_config)
        
        self.planner_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a software architect. Design the backend architecture.

For MONOLITH:
- Single codebase
- All features in one service
- Simpler deployment
- Good for small-medium projects

For MICROSERVICES:
- Multiple services
- Each service = one domain
- Complex deployment
- Good for large projects

Design the folder structure and service boundaries.
Return JSON with: style, structure, services, reasoning"""),
            ("user", """Requirements: {requirements}
Stack: {stack}
Preferred style: {style}

Design architecture:""")
        ])
    
    def plan(self, requirements: Dict[str, Any], 
             stack: Dict[str, str],
             style: str = "monolith") -> Dict[str, Any]:
        """Plan architecture."""
        
        # If user specified style, use it
        if style != "auto":
            return self._plan_by_style(style, stack)
        
        # Let LLM decide
        try:
            chain = self.planner_prompt | self.llm
            response = chain.invoke({
                "requirements": json.dumps(requirements),
                "stack": json.dumps(stack),
                "style": style
            })
            
            plan = json.loads(response.content)
            
            return {
                "style": plan.get("style", "monolith"),
                "structure": plan.get("structure", {}),
                "services": plan.get("services", []),
                "reasoning": plan.get("reasoning", "")
            }
        
        except Exception as e:
            print(f"Error in architecture planning: {e}")
            return self._plan_by_style("monolith", stack)
    
    def _plan_by_style(self, style: str, stack: Dict[str, str]) -> Dict[str, Any]:
        """Plan architecture for specific style."""
        
        if style == "microservices":
            return self._plan_microservices(stack)
        else:
            return self._plan_monolith(stack)
    
    def _plan_monolith(self, stack: Dict[str, str]) -> Dict[str, Any]:
        """Plan monolithic architecture."""
        
        framework = stack["framework"]
        
        if framework == "express":
            structure = {
                "src/": {
                    "config/": ["database.js", "env.js"],
                    "models/": [],
                    "routes/": [],
                    "controllers/": [],
                    "services/": [],
                    "middleware/": ["auth.js", "errorHandler.js"],
                    "utils/": ["logger.js"],
                    "app.js": None,
                    "server.js": None
                },
                "tests/": {},
                "package.json": None,
                ".env.example": None,
                "README.md": None
            }
        
        elif framework == "fastapi":
            structure = {
                "app/": {
                    "api/": {
                        "routes/": [],
                        "dependencies.py": None
                    },
                    "core/": ["config.py", "security.py"],
                    "models/": [],
                    "schemas/": [],
                    "crud/": [],
                    "services/": [],
                    "main.py": None
                },
                "tests/": {},
                "alembic/": {"versions/": []},
                "requirements.txt": None,
                ".env.example": None,
                "README.md": None
            }
        
        else:
            structure = {}
        
        return {
            "style": "monolith",
            "structure": structure,
            "services": ["main"],
            "reasoning": "Monolithic architecture for simpler deployment"
        }
    
    def _plan_microservices(self, stack: Dict[str, str]) -> Dict[str, Any]:
        """Plan microservices architecture."""
        
        structure = {
            "services/": {
                "auth-service/": {},
                "user-service/": {},
                "api-gateway/": {}
            },
            "shared/": {},
            "docker-compose.yml": None,
            "README.md": None
        }
        
        return {
            "style": "microservices",
            "structure": structure,
            "services": ["auth-service", "user-service", "api-gateway"],
            "reasoning": "Microservices for scalability and modularity"
        }
