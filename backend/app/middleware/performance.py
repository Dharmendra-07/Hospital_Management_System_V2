import time
from flask import request, g
from app.services.cache_service import cache_service
import logging

logger = logging.getLogger(__name__)

def setup_performance_monitoring(app):
  """
  Setup performance monitoring middleware
  """
  @app.before_request
  def start_timer():
    g.start_time = time.time()
    g.db_query_count = 0
    g.cache_hits = 0
    g.cache_misses = 0

  @app.after_request
  def log_performance(response):
    # Skip for static files and health checks
    if request.path.startswith('/static') or request.path == '/health':
      return response

    # Calculate request time
    request_time = time.time() - g.start_time
    
    # Log performance metrics
    logger.info(
      f"Performance: {request.method} {request.path} - "
      f"Time: {request_time:.3f}s - "
      f"DB Queries: {getattr(g, 'db_query_count', 0)} - "
      f"Cache: {getattr(g, 'cache_hits', 0)}H/{getattr(g, 'cache_misses', 0)}M - "
      f"Status: {response.status_code}"
    )

    # Add performance headers for monitoring
    response.headers['X-Response-Time'] = f'{request_time:.3f}'
    response.headers['X-DB-Queries'] = str(getattr(g, 'db_query_count', 0))
    
    if cache_service.is_connected():
      cache_stats = cache_service.get_cache_stats()
      response.headers['X-Cache-Hits'] = str(cache_stats.get('keyspace_hits', 0))
      response.headers['X-Cache-Misses'] = str(cache_stats.get('keyspace_misses', 0))

    return response

# Database query counter
def setup_db_monitoring():
  """
  Setup database query monitoring
  """
  from sqlalchemy import event
  from app.models import db
  from flask import g

  @event.listens_for(db.engine, "before_cursor_execute")
  def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    if not hasattr(g, 'db_query_count'):
      g.db_query_count = 0
    g.db_query_count += 1