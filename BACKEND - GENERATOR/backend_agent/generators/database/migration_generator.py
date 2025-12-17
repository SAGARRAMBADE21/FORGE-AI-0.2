"""
Migration Generator Agent
Generates database migration scripts (Alembic, Prisma, Sequelize).
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


class MigrationGeneratorAgent:
    """Generates migration scripts."""
    
    def __init__(self, orm_type: str, database_type: str):
        self.orm_type = orm_type
        self.database_type = database_type
    
    def generate(self, schema: Dict[str, Any], 
                 existing_schema: Optional[Dict[str, Any]] = None) -> List[Dict[str, str]]:
        """Generate migration scripts."""
        
        if existing_schema:
            return self._generate_incremental(schema, existing_schema)
        else:
            return self._generate_initial(schema)
    
    def _generate_initial(self, schema: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate initial migration."""
        
        generators = {
            "sqlalchemy": self._generate_alembic_migration,
            "sequelize": self._generate_sequelize_migration,
            "prisma": self._generate_prisma_migration,
        }
        
        generator = generators.get(self.orm_type, self._generate_sql_migration)
        return [generator(schema)]
    
    def _generate_alembic_migration(self, schema: Dict[str, Any]) -> Dict[str, str]:
        """Generate Alembic migration."""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        revision_id = timestamp[:12]
        
        upgrade_sql = []
        downgrade_sql = []
        
        for table in schema.get("tables", []):
            # Upgrade: create table
            upgrade_sql.append(table["ddl"])
            
            # Add indexes
            for index in table.get("indexes", []):
                upgrade_sql.append(index)
            
            # Downgrade: drop table
            downgrade_sql.append(f"DROP TABLE IF EXISTS {table['name']};")
        
        migration_content = f'''"""Initial migration

Revision ID: {revision_id}
Create Date: {datetime.now().isoformat()}
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = '{revision_id}'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema."""
{self._indent_sql(upgrade_sql, 4)}


def downgrade() -> None:
    """Downgrade database schema."""
{self._indent_sql(downgrade_sql, 4)}
'''
        
        filename = f"alembic/versions/{revision_id}_initial_migration.py"
        
        return {
            "version": revision_id,
            "filename": filename,
            "up": migration_content,
            "down": migration_content  # Contains both
        }
    
    def _generate_sequelize_migration(self, schema: Dict[str, Any]) -> Dict[str, str]:
        """Generate Sequelize migration."""
        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        up_code = []
        down_code = []
        
        for table in schema.get("tables", []):
            # Convert DDL to Sequelize format
            fields = self._parse_fields_from_ddl(table["ddl"])
            
            up_code.append(f'''await queryInterface.createTable('{table["name"]}', {{
{self._format_sequelize_fields(fields)}
    }});''')
            
            down_code.append(f"await queryInterface.dropTable('{table['name']}');")
        
        migration_content = f'''module.exports = {{
  up: async (queryInterface, Sequelize) => {{
{self._indent_code(up_code, 4)}
  }},

  down: async (queryInterface, Sequelize) => {{
{self._indent_code(down_code, 4)}
  }}
}};
'''
        
        filename = f"migrations/{timestamp}-initial-migration.js"
        
        return {
            "version": timestamp,
            "filename": filename,
            "up": migration_content,
            "down": migration_content
        }
    
    def _generate_prisma_migration(self, schema: Dict[str, Any]) -> Dict[str, str]:
        """Generate Prisma migration."""
        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        migration_name = "initial_migration"
        
        sql_statements = []
        for table in schema.get("tables", []):
            sql_statements.append(table["ddl"])
            for index in table.get("indexes", []):
                sql_statements.append(index)
        
        migration_sql = "\n\n".join(sql_statements)
        
        filename = f"prisma/migrations/{timestamp}_{migration_name}/migration.sql"
        
        return {
            "version": timestamp,
            "filename": filename,
            "up": migration_sql,
            "down": "-- No automatic rollback"
        }
    
    def _generate_sql_migration(self, schema: Dict[str, Any]) -> Dict[str, str]:
        """Generate raw SQL migration."""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        upgrade_sql = []
        downgrade_sql = []
        
        for table in schema.get("tables", []):
            upgrade_sql.append(table["ddl"])
            for index in table.get("indexes", []):
                upgrade_sql.append(index)
            downgrade_sql.append(f"DROP TABLE IF EXISTS {table['name']};")
        
        up_content = "\n\n".join(upgrade_sql)
        down_content = "\n\n".join(downgrade_sql)
        
        return {
            "version": timestamp,
            "filename": f"migrations/{timestamp}_initial.sql",
            "up": up_content,
            "down": down_content
        }
    
    def _generate_incremental(self, new_schema: Dict[str, Any], 
                              old_schema: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate incremental migration."""
        # Compare schemas and generate ALTER statements
        # Simplified: just treat as new migration
        return self._generate_initial(new_schema)
    
    def _indent_sql(self, statements: List[str], spaces: int) -> str:
        """Indent SQL statements for Python code."""
        indent = " " * spaces
        formatted = []
        for stmt in statements:
            formatted.append(f"{indent}op.execute('''{stmt}''')")
        return "\n".join(formatted)
    
    def _indent_code(self, statements: List[str], spaces: int) -> str:
        """Indent code statements."""
        indent = " " * spaces
        return "\n".join([f"{indent}{stmt}" for stmt in statements])
    
    def _parse_fields_from_ddl(self, ddl: str) -> List[Dict[str, Any]]:
        """Parse field definitions from DDL."""
        fields = []
        for line in ddl.split("\n")[1:-1]:
            line = line.strip().rstrip(",")
            if not line:
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            
            fields.append({
                "name": parts[0],
                "type": parts[1],
                "constraints": " ".join(parts[2:])
            })
        return fields
    
    def _format_sequelize_fields(self, fields: List[Dict[str, Any]]) -> str:
        """Format fields for Sequelize."""
        formatted = []
        for field in fields:
            type_map = {
                "SERIAL": "Sequelize.INTEGER",
                "INTEGER": "Sequelize.INTEGER",
                "VARCHAR(255)": "Sequelize.STRING",
                "TEXT": "Sequelize.TEXT",
                "BOOLEAN": "Sequelize.BOOLEAN",
                "TIMESTAMP": "Sequelize.DATE",
            }
            
            seq_type = type_map.get(field["type"], "Sequelize.STRING")
            
            constraints = []
            if "PRIMARY KEY" in field["constraints"]:
                constraints.append("primaryKey: true, autoIncrement: true")
            if "NOT NULL" in field["constraints"]:
                constraints.append("allowNull: false")
            if "UNIQUE" in field["constraints"]:
                constraints.append("unique: true")
            
            field_def = f"      {field['name']}: {{ type: {seq_type}"
            if constraints:
                field_def += f", {', '.join(constraints)}"
            field_def += " }"
            
            formatted.append(field_def)
        
        return ",\n".join(formatted)
