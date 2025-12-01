import redis
import json
import pickle
from datetime import timedelta
import logging
from functools import wraps
from flask import current_app

logger = logging.getLogger(__name__)

class CacheService:
  def __init__(self):
      self.redis_client = None
      self._connect()
  
  def _connect(self):
    """Establish connection to Redis"""
    try:
      self.redis_client = redis.Redis(
        host=current_app.config.get('REDIS_HOST', 'localhost'),
        port=current_app.config.get('REDIS_PORT', 6379),
        db=current_app.config.get('REDIS_DB', 0),
        password=current_app.config.get('REDIS_PASSWORD'),
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_timeout=True
      )
      # Test connection
      self.redis_client.ping()
      logger.info("Redis connection established successfully")
    except Exception as e:
      logger.error(f"Failed to connect to Redis: {str(e)}")
      self.redis_client = None
  
  def is_connected(self):
    """Check if Redis is connected"""
    try:
      return self.redis_client and self.redis_client.ping()
    except:
      return False
  
  def get(self, key):
    """Get value from cache"""
    if not self.is_connected():
      return None
    
    try:
      value = self.redis_client.get(key)
      if value:
        # Try to deserialize JSON first, then fall back to pickle
        try:
          return json.loads(value)
        except:
          return pickle.loads(value.encode('latin1'))
      return None
    except Exception as e:
      logger.error(f"Error getting key {key} from cache: {str(e)}")
      return None
  
  def set(self, key, value, expiry_seconds=3600):
    """Set value in cache with expiry"""
    if not self.is_connected():
      return False
    
    try:
        # Try to serialize as JSON first, then fall back to pickle
        try:
          serialized_value = json.dumps(value)
        except:
          serialized_value = pickle.dumps(value).decode('latin1')
        
        if expiry_seconds:
          self.redis_client.setex(key, expiry_seconds, serialized_value)
        else:
          self.redis_client.set(key, serialized_value)
        
        return True
    except Exception as e:
      logger.error(f"Error setting key {key} in cache: {str(e)}")
      return False
  
  def delete(self, key):
    """Delete key from cache"""
    if not self.is_connected():
      return False
    
    try:
      self.redis_client.delete(key)
      return True
    except Exception as e:
      logger.error(f"Error deleting key {key} from cache: {str(e)}")
      return False
  
  def delete_pattern(self, pattern):
    """Delete all keys matching pattern"""
    if not self.is_connected():
      return False
    
    try:
      keys = self.redis_client.keys(pattern)
      if keys:
        self.redis_client.delete(*keys)
      return True
    except Exception as e:
      logger.error(f"Error deleting pattern {pattern} from cache: {str(e)}")
      return False
  
  def exists(self, key):
    """Check if key exists in cache"""
    if not self.is_connected():
      return False
    
    try:
      return self.redis_client.exists(key)
    except Exception as e:
      logger.error(f"Error checking key {key} in cache: {str(e)}")
      return False
  
  def increment(self, key, amount=1):
    """Increment value in cache"""
    if not self.is_connected():
      return None
    
    try:
      return self.redis_client.incrby(key, amount)
    except Exception as e:
      logger.error(f"Error incrementing key {key} in cache: {str(e)}")
      return None
  
  def get_cache_stats(self):
    """Get cache statistics"""
    if not self.is_connected():
      return {}
    
    try:
      info = self.redis_client.info()
      return {
        'connected_clients': info.get('connected_clients', 0),
        'used_memory_human': info.get('used_memory_human', '0'),
        'keyspace_hits': info.get('keyspace_hits', 0),
        'keyspace_misses': info.get('keyspace_misses', 0),
        'total_commands_processed': info.get('total_commands_processed', 0),
        'keys_count': len(self.redis_client.keys('*'))
        }
    except Exception as e:
      logger.error(f"Error getting cache stats: {str(e)}")
      return {}

# Global cache service instance
cache_service = CacheService()

def cached(key_pattern=None, expiry=3600, unless=None):
  """
  Decorator for caching function results
  """
  def decorator(f):
      @wraps(f)
      def decorated_function(*args, **kwargs):
          # Skip caching if Redis is not connected
          if not cache_service.is_connected():
            return f(*args, **kwargs)
          
          # Check unless condition
          if unless and unless():
            return f(*args, **kwargs)
          
          # Generate cache key
          if key_pattern:
            cache_key = key_pattern
          else:
            # Generate key from function name and arguments
            key_parts = [f.__module__, f.__name__]
            key_parts.extend([str(arg) for arg in args])
            for k, v in sorted(kwargs.items()):
              key_parts.append(f"{k}={v}")
            cache_key = "::".join(key_parts)
          
          # Try to get from cache
          cached_result = cache_service.get(cache_key)
          if cached_result is not None:
            logger.debug(f"Cache hit for key: {cache_key}")
            return cached_result
          
          # Execute function and cache result
          result = f(*args, **kwargs)
          cache_service.set(cache_key, result, expiry)
          logger.debug(f"Cache set for key: {cache_key}")
          
          return result
      return decorated_function
  return decorator

def invalidate_cache(pattern):
  """
  Invalidate cache entries matching pattern
  """
  def decorator(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
      result = f(*args, **kwargs)
      
      # Invalidate cache after function execution
      if cache_service.is_connected():
        cache_service.delete_pattern(pattern)
        logger.debug(f"Invalidated cache pattern: {pattern}")
      
      return result
    return decorated_function
  return decorator