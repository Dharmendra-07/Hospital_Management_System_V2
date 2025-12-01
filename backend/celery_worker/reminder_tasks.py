from celery_worker import celery
from app.models import Appointment, Patient, Doctor, db
from app.services.email_service import email_service
from datetime import datetime, timedelta
import logging
from sqlalchemy import and_

logger = logging.getLogger(__name__)

@celery.task(bind=True, name='reminder_tasks.send_daily_appointment_reminders')
def send_daily_appointment_reminders(self):
  """
  Send reminder emails for appointments scheduled for today
  """
  try:
      today = datetime.now().date()
      logger.info(f"Starting daily appointment reminders for {today}")
      
      # Find appointments for today that are still scheduled
      appointments = Appointment.query.filter(
          and_(
            Appointment.appointment_date == today,
            Appointment.status == 'scheduled'
          )
      ).all()
      
      reminder_count = 0
      failed_reminders = 0
      
      for appointment in appointments:
          try:
              patient = appointment.patient
              doctor = appointment.doctor
              
              # Send email reminder
              success = email_service.send_appointment_reminder(
                patient_email=patient.user.email,
                patient_name=f"{patient.first_name} {patient.last_name}",
                appointment_date=appointment.appointment_date.strftime('%Y-%m-%d'),
                appointment_time=appointment.appointment_time.strftime('%H:%M'),
                doctor_name=doctor.user.username
              )
              
              if success:
                reminder_count += 1
                logger.info(f"Reminder sent for appointment {appointment.id}")
              else:
                failed_reminders += 1
                logger.error(f"Failed to send reminder for appointment {appointment.id}")
                  
          except Exception as e:
            failed_reminders += 1
            logger.error(f"Error processing appointment {appointment.id}: {str(e)}")
            continue
      
      logger.info(f"Daily reminders completed. Sent: {reminder_count}, Failed: {failed_reminders}")
      
      return {
        'status': 'completed',
        'reminders_sent': reminder_count,
        'reminders_failed': failed_reminders,
        'total_appointments': len(appointments)
      }
      
  except Exception as e:
      logger.error(f"Error in send_daily_appointment_reminders: {str(e)}")
      return {
        'status': 'failed',
        'error': str(e)
      }

@celery.task(bind=True, name='reminder_tasks.send_custom_reminder')
def send_custom_reminder(self, appointment_id):
  """
  Send a custom reminder for a specific appointment
  """
  try:
      appointment = Appointment.query.get(appointment_id)
      if not appointment:
        return {'status': 'failed', 'error': 'Appointment not found'}
      
      patient = appointment.patient
      doctor = appointment.doctor
      
      success = email_service.send_appointment_reminder(
        patient_email=patient.user.email,
        patient_name=f"{patient.first_name} {patient.last_name}",
        appointment_date=appointment.appointment_date.strftime('%Y-%m-%d'),
        appointment_time=appointment.appointment_time.strftime('%H:%M'),
        doctor_name=doctor.user.username
      )
      
      return {
        'status': 'success' if success else 'failed',
        'appointment_id': appointment_id,
        'patient_email': patient.user.email
      }
      
  except Exception as e:
      logger.error(f"Error in send_custom_reminder: {str(e)}")
      return {
        'status': 'failed',
        'error': str(e)
      }

@celery.task(bind=True, name='reminder_tasks.send_follow_up_reminders')
def send_follow_up_reminders(self):
  """
  Send follow-up reminders for appointments that need follow-up
  """
  try:
      today = datetime.now().date()
      follow_up_appointments = Appointment.query.join(
          db.metadata.tables['treatments']
      ).filter(
          and_(
              db.metadata.tables['treatments'].c.follow_up_date == today,
              Appointment.status == 'completed'
          )
      ).all()
      
      reminder_count = 0
      for appointment in follow_up_appointments:
          try:
              patient = appointment.patient
              doctor = appointment.doctor
              
              # Send follow-up reminder
              subject = "Follow-up Appointment Reminder"
              html_content = f"""
              <h2>Follow-up Appointment Reminder</h2>
              <p>Dear {patient.first_name},</p>
              <p>This is a reminder that you have a follow-up appointment scheduled for today.</p>
              <p>If you haven't already, please schedule your follow-up visit.</p>
              <p>Best regards,<br>Hospital Team</p>
              """
              
              success = email_service.send_email(
                patient.user.email,
                subject,
                html_content
              )
              
              if success:
                reminder_count += 1
                  
          except Exception as e:
            logger.error(f"Error sending follow-up reminder: {str(e)}")
            continue
      
      return {
        'status': 'completed',
        'follow_up_reminders_sent': reminder_count
      }
      
  except Exception as e:
      logger.error(f"Error in send_follow_up_reminders: {str(e)}")
      return {
        'status': 'failed',
        'error': str(e)
      }