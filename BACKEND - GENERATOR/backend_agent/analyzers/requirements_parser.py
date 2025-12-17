"""
Requirements Parser Agent
Parses natural language requirements using LLM.
"""

from typing import Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate
import json
import sys
from pathlib import Path

# Import LLM factory
sys.path.insert(0, str(Path(__file__).parent.parent))
from backend_agent.utils.llm_factory import create_llm


class RequirementsParserAgent:
    """Parses user requirements into structured format."""
    
    def __init__(self, llm_config: Dict[str, Any]):
        self.llm = create_llm(llm_config)
        
        self.parser_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert backend architect. Parse user requirements into a structured format.

Extract:
1. Features (list of features to implement)
2. Entities (data models mentioned)
3. Business rules (any logic constraints)
4. Performance requirements
5. Security requirements
6. Third-party integrations needed
7. ML/AI features

Return valid JSON only."""),
            ("user", "Requirements: {requirements}\n\nParse into structured JSON:")
        ])
    
    def parse(self, requirements: str) -> Dict[str, Any]:
        """Parse natural language requirements."""
        
        if not requirements or requirements.strip() == "":
            return self._default_requirements()
        
        try:
            chain = self.parser_prompt | self.llm
            response = chain.invoke({"requirements": requirements})
            
            # Parse LLM response
            parsed = json.loads(response.content)
            
            return {
                "features": parsed.get("features", []),
                "entities": parsed.get("entities", []),
                "business_rules": parsed.get("business_rules", []),
                "performance": parsed.get("performance_requirements", {}),
                "security": parsed.get("security_requirements", {}),
                "integrations": parsed.get("third_party_integrations", []),
                "ml_features": parsed.get("ml_features", []),
                "raw": requirements
            }
        
        except Exception as e:
            print(f"Error parsing requirements with LLM: {e}")
            return self._fallback_parse(requirements)
    
    def _fallback_parse(self, requirements: str) -> Dict[str, Any]:
        """Fallback parsing without LLM."""
        features = []
        entities = []
        integrations = []
        
        # Simple keyword extraction
        if "auth" in requirements.lower():
            features.append("Authentication")
            entities.append("User")
        
        if "blog" in requirements.lower():
            features.extend(["CRUD Posts", "Comments"])
            entities.extend(["Post", "Comment"])
        
        if "crud" in requirements.lower():
            features.append("CRUD Operations")
        
        if "api" in requirements.lower():
            features.append("REST API")
        
        # Check for integrations
        integration_keywords = {
            "stripe": "Payment (Stripe)",
            "sendgrid": "Email (SendGrid)",
            "aws": "Cloud Storage (AWS)",
            "ml": "Machine Learning",
        }
        
        for keyword, integration in integration_keywords.items():
            if keyword in requirements.lower():
                integrations.append(integration)
        
        return {
            "features": features or ["Basic CRUD"],
            "entities": entities or ["User"],
            "business_rules": [],
            "performance": {},
            "security": {"authentication": True},
            "integrations": integrations,
            "ml_features": ["ML Model Integration"] if "ml" in requirements.lower() else [],
            "raw": requirements
        }
    
    def _default_requirements(self) -> Dict[str, Any]:
        """Default requirements when none provided."""
        return {
            "features": ["REST API", "CRUD Operations"],
            "entities": ["User"],
            "business_rules": [],
            "performance": {},
            "security": {"authentication": True},
            "integrations": [],
            "ml_features": [],
            "raw": ""
        }
