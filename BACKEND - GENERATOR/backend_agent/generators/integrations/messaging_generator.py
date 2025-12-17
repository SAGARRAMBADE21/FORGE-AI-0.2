"""
Messaging Generator Agent
Generates message queue integration (Redis, RabbitMQ).
"""

from typing import Dict, Any


class MessagingGeneratorAgent:
    """Generates message queue integration."""
    
    def __init__(self, framework: str, queue_type: str = "redis"):
        self.framework = framework
        self.queue_type = queue_type
    
    def generate(self) -> Dict[str, str]:
        """Generate message queue integration."""
        
        if self.queue_type == "redis":
            return self._generate_redis_queue()
        elif self.queue_type == "rabbitmq":
            return self._generate_rabbitmq()
        else:
            return {}
    
    def _generate_redis_queue(self) -> Dict[str, str]:
        """Generate Redis queue integration."""
        
        if self.framework == "fastapi":
            code = '''"""Redis queue service."""

import redis
import json
from app.core.config import settings


class RedisQueue:
    """Redis-based task queue."""
    
    def __init__(self):
        self.redis_client = redis.Redis.from_url(settings.REDIS_URL)
    
    def enqueue(self, queue_name: str, task_data: dict):
        """Add task to queue."""
        self.redis_client.rpush(queue_name, json.dumps(task_data))
    
    def dequeue(self, queue_name: str) -> dict | None:
        """Get task from queue."""
        data = self.redis_client.lpop(queue_name)
        if data:
            return json.loads(data)
        return None


redis_queue = RedisQueue()
'''
            return {"app/services/redis_queue.py": code}
        
        else:  # Express
            code = '''const redis = require('redis');

const client = redis.createClient({
  url: process.env.REDIS_URL
});

client.connect();

class RedisQueue {
  async enqueue(queueName, taskData) {
    await client.rPush(queueName, JSON.stringify(taskData));
  }
  
  async dequeue(queueName) {
    const data = await client.lPop(queueName);
    return data ? JSON.parse(data) : null;
  }
}

module.exports = new RedisQueue();
'''
            return {"src/services/redisQueue.js": code}
    
    def _generate_rabbitmq(self) -> Dict[str, str]:
        """Generate RabbitMQ integration."""
        return {
            "rabbitmq_integration.txt": "# RabbitMQ integration placeholder\n# Implement RabbitMQ producer/consumer"
        }
