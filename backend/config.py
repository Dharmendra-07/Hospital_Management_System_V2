import os
from datetime import timedelta

class Config:
  SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-2024'
  SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///healthcare.db'
  SQLALCHEMY_TRACK_MODIFICATIONS = False

  # Redis configuration 
  REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'

  # Celery configuration
  CELERY_BROKEN_URL = REDIS_URL
  CELERY_RESULT_BACKEND = REDIS_URL

  # JWT configuration
  JWT_SECRET_KEY = SECRET_KEY
  JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)

  # EMail configuration (for notifications)
  MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
  MAIL_PORT = int(os.environ.get("MAIL_PORT") or 587)
  MAIL_USE_TLS = True
  MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
  MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
  