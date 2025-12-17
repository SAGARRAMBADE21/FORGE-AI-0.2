"""
Seed Data Generator Agent
Generates seed data for testing.
"""

from typing import Dict, Any, List
import random
import string


class SeedGeneratorAgent:
    """Generates seed/fixture data."""
    
    def __init__(self):
        self.fake_data = {
            "username": lambda: f"user_{random.randint(1000, 9999)}",
            "email": lambda: f"user{random.randint(1, 999)}@example.com",
            "password": lambda: "hashed_password_here",
            "title": lambda: f"Sample Title {random.randint(1, 100)}",
            "content": lambda: "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            "name": lambda: random.choice(["Alice", "Bob", "Charlie", "Diana", "Eve"]),
            "description": lambda: "Sample description text.",
        }
    
    def generate(self, schema: Dict[str, Any], count: int = 10) -> Dict[str, List[Dict[str, Any]]]:
        """Generate seed data."""
        
        seed_data = {}
        
        for table in schema.get("tables", []):
            table_name = table["name"]
            records = []
            
            for i in range(count):
                record = self._generate_record(table, i + 1)
                records.append(record)
            
            seed_data[table_name] = records
        
        return seed_data
    
    def _generate_record(self, table: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Generate a single record."""
        
        record = {}
        
        # Parse fields from DDL
        for line in table["ddl"].split("\n")[1:-1]:
            line = line.strip().rstrip(",")
            if not line:
                continue
            
            parts = line.split()
            if len(parts) < 2:
                continue
            
            field_name = parts[0]
            field_type = parts[1]
            
            # Skip auto-increment primary keys
            if "PRIMARY KEY" in line or field_name == "id":
                continue
            
            # Skip timestamps (handled by DB)
            if field_name in ["created_at", "updated_at"]:
                continue
            
            # Generate value
            value = self._generate_value(field_name, field_type, index)
            record[field_name] = value
        
        return record
    
    def _generate_value(self, field_name: str, field_type: str, index: int) -> Any:
        """Generate a value for a field."""
        
        # Use predefined generators if available
        if field_name in self.fake_data:
            return self.fake_data[field_name]()
        
        # Generate based on type
        type_map = {
            "INTEGER": lambda: random.randint(1, 1000),
            "VARCHAR(255)": lambda: f"Sample {field_name} {index}",
            "TEXT": lambda: f"Sample {field_name} content for record {index}",
            "BOOLEAN": lambda: random.choice([True, False]),
            "DECIMAL": lambda: round(random.uniform(10, 1000), 2),
        }
        
        generator = type_map.get(field_type, lambda: f"value_{index}")
        return generator()
