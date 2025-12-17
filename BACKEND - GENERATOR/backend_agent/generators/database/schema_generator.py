"""
Schema Generator Agent
Generates database schema (DDL) from data models.
"""

from typing import Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate
from backend_agent.utils.llm_factory import create_llm


class SchemaGeneratorAgent:
    """Generates database schema."""
    
    def __init__(self, database_type: str, llm_config: Dict[str, Any]):
        self.database_type = database_type
        self.llm = create_llm(llm_config)
        
        self.schema_prompt = ChatPromptTemplate.from_messages([
            ("system", f"""You are a database expert. Generate {database_type} schema.

Create:
- Tables with appropriate columns
- Primary keys
- Foreign keys
- Indexes
- Constraints (NOT NULL, UNIQUE, CHECK)

Return valid {database_type} DDL SQL."""),
            ("user", "Data models:\n{models}\n\nGenerate {database_type} schema:")
        ])
    
    def generate(self, data_models: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate database schema."""
        
        if self.database_type == "mongodb":
            return self._generate_mongodb_schema(data_models)
        else:
            return self._generate_sql_schema(data_models)
    
    def _generate_sql_schema(self, data_models: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate SQL schema."""
        
        tables = []
        
        for model in data_models:
            table_name = self._pluralize(model["name"].lower())
            
            # Create table DDL
            columns = []
            for field in model["fields"]:
                col_def = self._field_to_column(field)
                columns.append(col_def)
            
            columns_str = ',\n    '.join(columns)
            create_table = f"""CREATE TABLE {table_name} (
    {columns_str}
);"""
            
            # Create indexes
            indexes = []
            for field in model["fields"]:
                if field.get("indexed") or field["name"] in ["email", "username"]:
                    idx_name = f"idx_{table_name}_{field['name']}"
                    indexes.append(f"CREATE INDEX {idx_name} ON {table_name}({field['name']});")
            
            tables.append({
                "name": table_name,
                "ddl": create_table,
                "indexes": indexes,
                "model": model["name"]
            })
        
        return {
            "database_type": self.database_type,
            "tables": tables,
            "relationships": self._extract_relationships(data_models)
        }
    
    def _field_to_column(self, field: Dict[str, Any]) -> str:
        """Convert field to SQL column definition."""
        
        name = field["name"]
        field_type = field["type"]
        
        # Map types
        type_map = {
            "integer": "INTEGER",
            "string": "VARCHAR(255)",
            "text": "TEXT",
            "boolean": "BOOLEAN",
            "datetime": "TIMESTAMP",
            "decimal": "DECIMAL(10, 2)",
            "float": "FLOAT",
            "date": "DATE"
        }
        
        sql_type = type_map.get(field_type, "VARCHAR(255)")
        
        constraints = []
        
        if field.get("primary_key"):
            constraints.append("PRIMARY KEY")
            if self.database_type == "postgresql":
                sql_type = "SERIAL"
        
        if field.get("required", True) and not field.get("primary_key"):
            constraints.append("NOT NULL")
        
        if field.get("unique"):
            constraints.append("UNIQUE")
        
        if field.get("default") is not None:
            constraints.append(f"DEFAULT {field['default']}")
        
        col_def = f"{name} {sql_type}"
        if constraints:
            col_def += " " + " ".join(constraints)
        
        return col_def
    
    def _generate_mongodb_schema(self, data_models: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate MongoDB schema (for Mongoose)."""
        
        collections = []
        
        for model in data_models:
            schema = {
                "name": model["name"],
                "collection": self._pluralize(model["name"].lower()),
                "fields": model["fields"]
            }
            collections.append(schema)
        
        return {
            "database_type": "mongodb",
            "collections": collections,
            "relationships": []
        }
    
    def _extract_relationships(self, data_models: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract foreign key relationships."""
        
        relationships = []
        
        for model in data_models:
            for field in model["fields"]:
                if field["name"].endswith("_id"):
                    # Assume foreign key
                    ref_model = field["name"].replace("_id", "").capitalize()
                    relationships.append({
                        "from_table": self._pluralize(model["name"].lower()),
                        "to_table": self._pluralize(ref_model.lower()),
                        "foreign_key": field["name"],
                        "reference": "id"
                    })
        
        return relationships
    
    def _pluralize(self, word: str) -> str:
        """Simple pluralization."""
        if word.endswith('y'):
            return word[:-1] + 'ies'
        elif word.endswith('s'):
            return word + 'es'
        else:
            return word + 's'
