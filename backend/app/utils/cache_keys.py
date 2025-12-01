class CacheKeys:
  # Doctor related cache keys
  @staticmethod
  def doctor_list(search=None, department_id=None):
    base_key = "doctors::list"
    if search:
        base_key += f"::search::{search}"
    if department_id:
        base_key += f"::dept::{department_id}"
    return base_key
  
  @staticmethod
  def doctor_detail(doctor_id):
    return f"doctors::detail::{doctor_id}"
  
  @staticmethod
  def doctor_availability(doctor_id, start_date, end_date):
    return f"doctors::availability::{doctor_id}::{start_date}::{end_date}"
  
  # Patient related cache keys
  @staticmethod
  def patient_detail(patient_id):
    return f"patients::detail::{patient_id}"
  
  @staticmethod
  def patient_appointments(patient_id, status=None):
    key = f"patients::appointments::{patient_id}"
    if status:
      key += f"::status::{status}"
    return key
  
  # Appointment related cache keys
  @staticmethod
  def appointment_detail(appointment_id):
    return f"appointments::detail::{appointment_id}"
  
  @staticmethod
  def appointment_slots(doctor_id, date):
    return f"appointments::slots::{doctor_id}::{date}"
  
  # Department related cache keys
  @staticmethod
  def department_list():
    return "departments::list"
  
  @staticmethod
  def department_detail(department_id):
    return f"departments::detail::{department_id}"
  
  # Statistics cache keys
  @staticmethod
  def admin_dashboard_stats():
    return "stats::admin_dashboard"
  
  @staticmethod
  def doctor_dashboard_stats(doctor_id):
    return f"stats::doctor_dashboard::{doctor_id}"
  
  @staticmethod
  def patient_dashboard_stats(patient_id):
    return f"stats::patient_dashboard::{patient_id}"
  
  # Search related cache keys
  @staticmethod
  def search_doctors(query):
    return f"search::doctors::{query}"
  
  @staticmethod
  def search_patients(query):
    return f"search::patients::{query}"
  
  # Pattern for bulk invalidation
  @staticmethod
  def pattern_doctors():
    return "doctors::*"
  
  @staticmethod
  def pattern_patients():
    return "patients::*"
  
  @staticmethod
  def pattern_appointments():
    return "appointments::*"
  
  @staticmethod
  def pattern_departments():
    return "departments::*"
  
  @staticmethod
  def pattern_stats():
    return "stats::*"
  
  @staticmethod
  def pattern_search():
    return "search::*"