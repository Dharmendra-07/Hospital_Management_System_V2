from celery_worker import celery
from datetime import datetime, timedelta
import logging
from celery.result import AsyncResult

logger = logging.getLogger(__name__)

@celery.task(bind=True, name='tasks.cleanup_old_task_results')
def cleanup_old_task_results(self):
  """
  Clean up old task results from Redis to prevent memory issues
  """
  try:
    # This would typically interface with your result backend
    # For Redis, you might use keys command with pattern matching
    # In production, consider using Redis TTL or a proper cleanup strategy
    
    logger.info("Cleanup task executed")
    return {
      'status': 'completed',
      'message': 'Cleanup task completed (implementation depends on result backend)'
    }
      
  except Exception as e:
    logger.error(f"Error in cleanup_old_task_results: {str(e)}")
    return {
      'status': 'failed',
      'error': str(e)
    }

@celery.task(bind=True, name='tasks.get_task_status')
def get_task_status(self, task_id):
  """
  Get the status of a specific task
  """
  try:
    task_result = AsyncResult(task_id, app=celery)
    
    return {
      'task_id': task_id,
      'status': task_result.status,
      'result': task_result.result if task_result.ready() else None,
      'date_done': task_result.date_done.isoformat() if task_result.date_done else None
    }
      
  except Exception as e:
    logger.error(f"Error in get_task_status: {str(e)}")
    return {
      'status': 'error',
      'error': str(e)
    }