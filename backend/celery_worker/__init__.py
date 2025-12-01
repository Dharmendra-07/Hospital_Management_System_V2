from celery import Celery
import os

def make_celery():
  redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
  
  celery = Celery(
    'hospital_management',
    broker=redis_url,
    backend=redis_url,
    include=[
      'celery_worker.tasks',
      'celery_worker.report_tasks',
      'celery_worker.reminder_tasks'
    ]
  )
  
  # Configuration
  celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    beat_schedule={
        'send-daily-reminders': {
          'task': 'celery_worker.reminder_tasks.send_daily_appointment_reminders',
          'schedule': 3600.0,  # Every hour
        },
        'send-monthly-reports': {
          'task': 'celery_worker.report_tasks.generate_monthly_reports',
          'schedule': 86400.0,  # Daily, but task checks if it's first day of month
        },
        'cleanup-old-tasks': {
          'task': 'celery_worker.tasks.cleanup_old_task_results',
          'schedule': 86400.0,  # Daily
        },
    }
  )
  
  return celery

celery = make_celery()