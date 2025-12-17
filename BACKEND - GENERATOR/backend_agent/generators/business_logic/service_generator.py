"""
Service Generator Agent
Generates service layer with business logic.
"""

from typing import Dict, Any
from jinja2 import Template


class ServiceGeneratorAgent:
    """Generates service layer."""
    
    def __init__(self, framework: str, llm_config: Dict[str, Any]):
        self.framework = framework
    
    def generate(self, models: Dict[str, str], 
                 controllers: Dict[str, str],
                 business_logic: list) -> Dict[str, str]:
        """Generate service files."""
        
        if self.framework == "express":
            return self._generate_express_services(models)
        elif self.framework == "fastapi":
            # FastAPI uses CRUD functions (already generated)
            return {}
        elif self.framework == "nestjs":
            # NestJS services already generated with controllers
            return {}
        else:
            return {}
    
    def _generate_express_services(self, models: Dict[str, str]) -> Dict[str, str]:
        """Generate Express services."""
        
        services = {}
        
        template = Template('''const {{ model }} = require('../models/{{ model }}');

/**
 * {{ model | capitalize }} Service
 * Business logic for {{ model }} operations
 */

class {{ model | capitalize }}Service {
  /**
   * Get all {{ model }}s with pagination
   */
  async getAll(page = 1, limit = 10) {
    const offset = (page - 1) * limit;
    const {{ model }}s = await {{ model }}.findAndCountAll({
      limit,
      offset,
      order: [['created_at', 'DESC']]
    });
    
    return {
      data: {{ model }}s.rows,
      total: {{ model }}s.count,
      page,
      totalPages: Math.ceil({{ model }}s.count / limit)
    };
  }
  
  /**
   * Get {{ model }} by ID
   */
  async getById(id) {
    const {{ model }}Entity = await {{ model }}.findByPk(id);
    if (!{{ model }}Entity) {
      throw new Error('{{ model | capitalize }} not found');
    }
    return {{ model }}Entity;
  }
  
  /**
   * Create new {{ model }}
   */
  async create(data) {
    // Add business logic here
    return await {{ model }}.create(data);
  }
  
  /**
   * Update {{ model }}
   */
  async update(id, data) {
    const {{ model }}Entity = await this.getById(id);
    return await {{ model }}Entity.update(data);
  }
  
  /**
   * Delete {{ model }}
   */
  async delete(id) {
    const {{ model }}Entity = await this.getById(id);
    return await {{ model }}Entity.destroy();
  }
}

module.exports = new {{ model | capitalize }}Service();
''')
        
        for model_path in models.keys():
            if "/models/" in model_path:
                model_name = model_path.split("/models/")[1].replace(".js", "")
                
                service_code = template.render(model=model_name)
                services[f"src/services/{model_name}Service.js"] = service_code
        
        return services
