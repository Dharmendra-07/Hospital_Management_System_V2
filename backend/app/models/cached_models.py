from app.models import Doctor, Patient, Appointment, Department, DoctorAvailability
from app.services.cache_service import cache_service, cached
from app.utils.cache_keys import CacheKeys
from datetime import datetime, timedelta

class CachedDoctor:
  @staticmethod
  @cached(key_pattern=CacheKeys.department_list(), expiry=3600)
  def get_all_departments():
    """Get all departments with caching"""
    return Department.query.all()
  
  @staticmethod
  @cached(key_pattern=CacheKeys.doctor_list(), expiry=1800)
  def get_available_doctors(search=None, department_id=None):
    """Get available doctors with caching"""
    from app.models import Doctor, User, Department
    query = Doctor.query.join(User).join(Department).filter(Doctor.is_available == True)
    
    if search:
      query = query.filter(
        (User.username.ilike(f'%{search}%')) |
        (Doctor.specialization.ilike(f'%{search}%')) |
        (Department.name.ilike(f'%{search}%'))
      )
    
    if department_id:
        query = query.filter(Doctor.department_id == department_id)
    
    return query.all()
  
  @staticmethod
  @cached(key_pattern=CacheKeys.doctor_detail("{doctor_id}"), expiry=3600)
  def get_doctor_with_details(doctor_id):
    """Get doctor details with caching"""
    from app.models import Doctor, User, Department
    return Doctor.query.join(User).join(Department).filter(Doctor.id == doctor_id).first()
  
  @staticmethod
  @cached(key_pattern=CacheKeys.doctor_availability("{doctor_id}", "{start_date}", "{end_date}"), expiry=900)
  def get_doctor_availability(doctor_id, start_date, end_date):
    """Get doctor availability with caching"""
    availability = DoctorAvailability.query.filter(
      DoctorAvailability.doctor_id == doctor_id,
      DoctorAvailability.date >= start_date,
      DoctorAvailability.date <= end_date,
      DoctorAvailability.is_available == True
    ).order_by(DoctorAvailability.date.asc(), DoctorAvailability.start_time.asc()).all()
    
    # Convert to serializable format
    result = []
    for slot in availability:
        # Check current bookings
        from app.models import Appointment
        appointment_count = Appointment.query.filter(
          Appointment.doctor_id == doctor_id,
          Appointment.appointment_date == slot.date,
          Appointment.appointment_time == slot.start_time,
          Appointment.status.in_(['scheduled', 'completed'])
        ).count()
        
        result.append({
          'id': slot.id,
          'date': slot.date.isoformat(),
          'start_time': slot.start_time.strftime('%H:%M'),
          'end_time': slot.end_time.strftime('%H:%M'),
          'is_available': slot.is_available and appointment_count < slot.max_patients,
          'max_patients': slot.max_patients,
          'current_appointments': appointment_count
        })
    return result

class CachedPatient:
  @staticmethod
  @cached(key_pattern=CacheKeys.patient_appointments("{patient_id}", "{status}"), expiry=1800)
  def get_patient_appointments(patient_id, status=None):
      """Get patient appointments with caching"""
      from app.models import Appointment, Doctor, User
      query = Appointment.query.join(Doctor).join(User).filter(
          Appointment.patient_id == patient_id
      )
      
      if status:
          query = query.filter(Appointment.status == status)
      else:
          query = query.filter(
              (Appointment.appointment_date >= datetime.now().date()) |
              (Appointment.status == 'scheduled')
          )
      
      appointments = query.order_by(
          Appointment.appointment_date.desc(),
          Appointment.appointment_time.desc()
      ).all()
      
      # Convert to serializable format
      result = []
      for appointment in appointments:
        result.append({
          'id': appointment.id,
          'doctor_name': appointment.doctor.user.username,
          'doctor_specialization': appointment.doctor.specialization,
          'appointment_date': appointment.appointment_date.isoformat(),
          'appointment_time': appointment.appointment_time.strftime('%H:%M'),
          'status': appointment.status,
          'reason': appointment.reason
          })
      return result

class CachedStats:
  @staticmethod
  @cached(key_pattern=CacheKeys.admin_dashboard_stats(), expiry=300)
  def get_admin_dashboard_stats():
    """Get admin dashboard stats with caching"""
    from app.models import Patient, Doctor, Appointment
    from datetime import datetime
    
    today = datetime.now().date()
    
    stats = {
      'total_patients': Patient.query.count(),
      'total_doctors': Doctor.query.count(),
      'total_appointments': Appointment.query.count(),
      'today_appointments': Appointment.query.filter(
          Appointment.appointment_date == today
      ).count(),
      'recent_appointments': Appointment.query.filter(
        Appointment.appointment_date >= today - timedelta(days=7)
      ).count()
    }
    
    return stats
  
  @staticmethod
  @cached(key_pattern=CacheKeys.doctor_dashboard_stats("{doctor_id}"), expiry=300)
  def get_doctor_dashboard_stats(doctor_id):
    """Get doctor dashboard stats with caching"""
    from app.models import Appointment
    from datetime import datetime, timedelta
    
    today = datetime.now().date()
    doctor_stats = {
      'today_appointments': Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.appointment_date == today
      ).count(),
      'upcoming_appointments': Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.appointment_date >= today,
        Appointment.appointment_date <= today + timedelta(days=7),
        Appointment.status == 'scheduled'
      ).count(),
      'total_patients': len(set([
        app.patient_id for app in Appointment.query.filter_by(doctor_id=doctor_id).all()
      ]))
    }
    
    return doctor_stats