from app.services.cache_service import invalidate_cache
from app.utils.cache_keys import CacheKeys

def invalidate_doctor_cache(doctor_id=None):
  """
  Invalidate doctor-related cache
  """
  def decorator(f):
      def decorated_function(*args, **kwargs):
          result = f(*args, **kwargs)
          
          # Invalidate doctor lists and details
          invalidate_cache(CacheKeys.pattern_doctors())
          invalidate_cache(CacheKeys.pattern_stats())
          invalidate_cache(CacheKeys.pattern_search())
          
          # Invalidate specific doctor if provided
          if doctor_id:
              invalidate_cache(CacheKeys.doctor_detail(doctor_id))
              invalidate_cache(CacheKeys.doctor_dashboard_stats(doctor_id))
          
          return result
      return decorated_function
  return decorator

def invalidate_patient_cache(patient_id=None):
  """
  Invalidate patient-related cache
  """
  def decorator(f):
      def decorated_function(*args, **kwargs):
          result = f(*args, **kwargs)
          
          # Invalidate patient lists and details
          invalidate_cache(CacheKeys.pattern_patients())
          invalidate_cache(CacheKeys.pattern_stats())
          
          # Invalidate specific patient if provided
          if patient_id:
              invalidate_cache(CacheKeys.patient_detail(patient_id))
              invalidate_cache(CacheKeys.patient_appointments(patient_id, '*'))
              invalidate_cache(CacheKeys.patient_dashboard_stats(patient_id))
          
          return result
      return decorated_function
  return decorator

def invalidate_appointment_cache(appointment_id=None, doctor_id=None, patient_id=None):
  """
  Invalidate appointment-related cache
  """
  def decorator(f):
      def decorated_function(*args, **kwargs):
          result = f(*args, **kwargs)
          
          # Invalidate appointment caches
          invalidate_cache(CacheKeys.pattern_appointments())
          invalidate_cache(CacheKeys.pattern_stats())
          
          # Invalidate specific caches if IDs provided
          if appointment_id:
              invalidate_cache(CacheKeys.appointment_detail(appointment_id))
          
          if doctor_id:
              invalidate_cache(CacheKeys.doctor_dashboard_stats(doctor_id))
              invalidate_cache(CacheKeys.pattern_doctors())
          
          if patient_id:
              invalidate_cache(CacheKeys.patient_appointments(patient_id, '*'))
              invalidate_cache(CacheKeys.patient_dashboard_stats(patient_id))
          
          return result
      return decorated_function
  return decorator

def invalidate_department_cache():
  """
  Invalidate department-related cache
  """
  def decorator(f):
      def decorated_function(*args, **kwargs):
          result = f(*args, **kwargs)
          
          invalidate_cache(CacheKeys.pattern_departments())
          invalidate_cache(CacheKeys.pattern_doctors())  # Doctors depend on departments
          invalidate_cache(CacheKeys.pattern_search())
          
          return result
      return decorated_function
  return decorator