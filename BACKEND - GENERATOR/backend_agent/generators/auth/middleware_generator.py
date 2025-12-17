"""
Middleware Generator Agent
Generates authentication and other middleware.
"""

from typing import Dict, Any


class MiddlewareGeneratorAgent:
    """Generates middleware functions."""
    
    def __init__(self, framework: str):
        self.framework = framework
    
    def generate(self) -> Dict[str, str]:
        """Generate middleware files."""
        
        if self.framework == "express":
            return self._generate_express_middleware()
        elif self.framework == "fastapi":
            return {}  # FastAPI uses dependencies instead
        else:
            return {}
    
    def _generate_express_middleware(self) -> Dict[str, str]:
        """Generate Express middleware."""
        
        error_handler = '''/**
 * Global Error Handler Middleware
 */
const errorHandler = (err, req, res, next) => {
  console.error('Error:', err);
  
  const statusCode = err.statusCode || 500;
  const message = err.message || 'Internal Server Error';
  
  res.status(statusCode).json({
    error: message,
    ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
  });
};

module.exports = errorHandler;
'''
        
        logger = '''const logger = (req, res, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
  next();
};

module.exports = logger;
'''
        
        return {
            "src/middleware/errorHandler.js": error_handler,
            "src/middleware/logger.js": logger
        }
