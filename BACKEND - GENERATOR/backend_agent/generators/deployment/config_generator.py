"""
Config Generator Agent
Generates application configuration files.
"""

from typing import Dict, Any


class ConfigGeneratorAgent:
    """Generates configuration files."""
    
    def __init__(self, stack: Dict[str, str]):
        self.stack = stack
    
    def generate(self) -> Dict[str, str]:
        """Generate config files."""
        
        configs = {}
        
        if self.stack["language"] == "node":
            # ESLint config
            configs[".eslintrc.js"] = '''module.exports = {
  env: {
    node: true,
    es2021: true,
  },
  extends: ['eslint:recommended'],
  parserOptions: {
    ecmaVersion: 'latest',
  },
  rules: {
    'no-console': 'warn',
    'no-unused-vars': 'warn',
  },
};
'''
            
            # Prettier config
            configs[".prettierrc"] = '''{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2
}
'''
        
        else:  # Python
            # Black config
            configs["pyproject.toml"] = '''[tool.black]
line-length = 100
target-version = ['py310', 'py311']
include = '\\.pyi?$'

[tool.isort]
profile = "black"
line_length = 100

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = "-v --cov=app --cov-report=term-missing"

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
'''
            
            # Setup.cfg
            configs["setup.cfg"] = '''[flake8]
max-line-length = 100
exclude = .git,__pycache__,venv,env
ignore = E203,W503

[mypy]
ignore_missing_imports = True
'''
        
        return configs
