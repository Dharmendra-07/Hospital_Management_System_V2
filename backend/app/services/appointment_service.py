from datetime import datetime, timedelta, time
from app.models import Appointment, DoctorAvailability, ConflictLog, AppointmentHistory, db
from flask_login import current_user
import json

class AppointmentService:
  
  @staticmethod
  def check_doctor_availability(doctor_id, appointment_date, appointment_time):
      """
      Check if doctor is available at the requested time slot
      """
      try:
          # Check if doctor has availability for the date and time
          availability_slot = DoctorAvailability.query.filter(
            DoctorAvailability.doctor_id == doctor_id,
            DoctorAvailability.date == appointment_date,
            DoctorAvailability.start_time == appointment_time,
            DoctorAvailability.is_available == True
          ).first()
          
          if not availability_slot:
              return False, "Doctor is not available at this time slot"
          
          # Check if slot is fully booked
          existing_appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == appointment_date,
            Appointment.appointment_time == appointment_time,
            Appointment.status.in_(['scheduled', 'completed'])
          ).count()
          
          if existing_appointments >= availability_slot.max_patients:
            return False, "This time slot is fully booked"
          
          return True, "Slot available"
          
      except Exception as e:
          return False, f"Error checking availability: {str(e)}"
  
  @staticmethod
  def check_patient_conflicts(patient_id, appointment_date, appointment_time, exclude_appointment_id=None):
      """
      Check if patient has any scheduling conflicts
      """
      try:
          # Check if patient already has an appointment at the same time
          query = Appointment.query.filter(
            Appointment.patient_id == patient_id,
            Appointment.appointment_date == appointment_date,
            Appointment.appointment_time == appointment_time,
            Appointment.status == 'scheduled'
          )
          
          if exclude_appointment_id:
            query = query.filter(Appointment.id != exclude_appointment_id)
          
          conflicting_appointment = query.first()
          
          if conflicting_appointment:
            return False, "You already have an appointment scheduled at this time"
          
          # Check if patient has appointments within 2 hours before or after
          appointment_datetime = datetime.combine(appointment_date, appointment_time)
          time_buffer = timedelta(hours=2)
          
          start_time = appointment_datetime - time_buffer
          end_time = appointment_datetime + time_buffer
          
          # Convert back to time for query
          start_time_only = start_time.time()
          end_time_only = end_time.time()
          
          time_conflict_query = Appointment.query.filter(
            Appointment.patient_id == patient_id,
            Appointment.appointment_date == appointment_date,
            Appointment.status == 'scheduled'
          )
          
          if exclude_appointment_id:
            time_conflict_query = time_conflict_query.filter(Appointment.id != exclude_appointment_id)
          
          time_conflicts = time_conflict_query.filter(
              ((Appointment.appointment_time >= start_time_only) & 
                (Appointment.appointment_time <= end_time_only))
          ).all()
          
          if time_conflicts:
            return False, "You have another appointment within 2 hours of this time"
          
          return True, "No conflicts found"
          
      except Exception as e:
        return False, f"Error checking patient conflicts: {str(e)}"
  
  @staticmethod
  def log_conflict(conflict_type, user_id, attempted_date, attempted_time, doctor_id=None, patient_id=None, resolved=False):
      """
      Log scheduling conflicts for analytics
      """
      try:
        conflict_log = ConflictLog(
          conflict_type=conflict_type,
          user_id=user_id,
          attempted_date=attempted_date,
          attempted_time=attempted_time,
          doctor_id=doctor_id,
          patient_id=patient_id,
          resolved=resolved
        )
        
        db.session.add(conflict_log)
        db.session.commit()
        return True
      except Exception as e:
        db.session.rollback()
        print(f"Error logging conflict: {str(e)}")
        return False
  
  @staticmethod
  def log_appointment_history(appointment_id, change_type, previous_data=None,new_data=None, change_reason=None, changed_by=None):
      """
      Log changes to appointments for audit trail
      """
      try:
          history = AppointmentHistory(
            appointment_id=appointment_id,
            changed_by=changed_by or current_user.id,
            change_type=change_type,
            previous_data=json.dumps(previous_data) if previous_data else None,
            new_data=json.dumps(new_data) if new_data else None,
            change_reason=change_reason
          )
          
          db.session.add(history)
          db.session.commit()
          return True
      except Exception as e:
          db.session.rollback()
          print(f"Error logging appointment history: {str(e)}")
          return False
  
  @staticmethod
  def validate_appointment_booking(doctor_id, patient_id, appointment_date,appointment_time, exclude_appointment_id=None):
      """
      Comprehensive validation for appointment booking
      """
      # Check doctor availability
      available, message = AppointmentService.check_doctor_availability(
          doctor_id, appointment_date, appointment_time
      )
      if not available:
          AppointmentService.log_conflict(
            'doctor_unavailable',
            patient_id,
            appointment_date,
            appointment_time,
            doctor_id=doctor_id,
            patient_id=patient_id
          )
          return False, message
      
      # Check patient conflicts
      conflict_free, message = AppointmentService.check_patient_conflicts(
          patient_id, appointment_date, appointment_time, exclude_appointment_id
      )
      if not conflict_free:
          AppointmentService.log_conflict(
            'patient_conflict',
            patient_id,
            appointment_date,
            appointment_time,
            doctor_id=doctor_id,
            patient_id=patient_id
          )
          return False, message
      
      # Check if appointment is in the future
      appointment_datetime = datetime.combine(appointment_date, appointment_time)
      if appointment_datetime < datetime.now():
          return False, "Cannot book appointments in the past"
      
      # Check if within reasonable future (e.g., 3 months)
      max_future_date = datetime.now() + timedelta(days=90)
      if appointment_datetime > max_future_date:
        return False, "Cannot book appointments more than 3 months in advance"
      
      return True, "Validation successful"
  
  @staticmethod
  def get_appointment_history(appointment_id):
      """
      Get complete history of an appointment
      """
      try:
        history = AppointmentHistory.query.filter_by(
          appointment_id=appointment_id
        ).order_by(AppointmentHistory.changed_at.desc()).all()
        
        history_data = []
        for record in history:
          history_data.append({
            'id': record.id,
            'changed_by': record.user.username,
            'change_type': record.change_type,
            'previous_data': json.loads(record.previous_data) if record.previous_data else None,
            'new_data': json.loads(record.new_data) if record.new_data else None,
            'change_reason': record.change_reason,
            'changed_at': record.changed_at.isoformat()
            })
        return True, history_data
      except Exception as e:
        return False, f"Error fetching appointment history: {str(e)}"
  
  @staticmethod
  def get_conflict_analytics(start_date=None, end_date=None):
      """
      Get analytics data about scheduling conflicts
      """
      try:
          query = ConflictLog.query
          
          if start_date:
            query = query.filter(ConflictLog.created_at >= start_date)
          if end_date:
            query = query.filter(ConflictLog.created_at <= end_date)
          
          conflicts = query.all()
          
          # Group by conflict type
          conflict_types = {}
          for conflict in conflicts:
              if conflict.conflict_type not in conflict_types:
                conflict_types[conflict.conflict_type] = 0
              conflict_types[conflict.conflict_type] += 1
          
          # Get resolution rate
          total_conflicts = len(conflicts)
          resolved_conflicts = len([c for c in conflicts if c.resolved])
          resolution_rate = (resolved_conflicts / total_conflicts * 100) if total_conflicts > 0 else 0
          
          return True, {
            'total_conflicts': total_conflicts,
            'resolved_conflicts': resolved_conflicts,
            'resolution_rate': round(resolution_rate, 2),
            'conflict_types': conflict_types,
            'conflicts_by_day': AppointmentService.get_conflicts_by_day(conflicts)
          }
          
      except Exception as e:
        return False, f"Error generating conflict analytics: {str(e)}"
  
  @staticmethod
  def get_conflicts_by_day(conflicts):
      """
      Group conflicts by day for trend analysis
      """
      conflicts_by_day = {}
      for conflict in conflicts:
        day = conflict.created_at.strftime('%Y-%m-%d')
        if day not in conflicts_by_day:
          conflicts_by_day[day] = 0
        conflicts_by_day[day] += 1
      
      return conflicts_by_day