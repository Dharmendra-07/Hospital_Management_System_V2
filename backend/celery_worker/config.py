import os
from datetime import timedelta

class CeleryConfig:
  broker_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
  result_backend = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
  
  # Task settings
  task_serializer = 'json'
  result_serializer = 'json'
  accept_content = ['json']
  timezone = 'UTC'
  enable_utc = True
  
  # Beat schedule
  beat_schedule = {
      'daily-reminders': {
          'task': 'celery_worker.reminder_tasks.send_daily_appointment_reminders',
          'schedule': timedelta(hours=1),  # Check every hour
      },
      'monthly-reports': {
          'task': 'celery_worker.report_tasks.generate_monthly_reports',
          'schedule': timedelta(days=1),  # Check daily
      },
      'cleanup-task-results': {
          'task': 'celery_worker.tasks.cleanup_old_task_results',
          'schedule': timedelta(days=1),
      },
  }
  
  # Result expiry
  result_expires = 3600  # 1 hour
  
  # Worker settings
  worker_prefetch_multiplier = 1
  task_acks_late = True
  worker_max_tasks_per_child = 1000