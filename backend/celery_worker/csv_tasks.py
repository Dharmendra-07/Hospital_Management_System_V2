from celery_worker import celery
from app.models import Appointment, Patient, Doctor, Treatment, db
from datetime import datetime
import csv
import io
import logging
from sqlalchemy import and_

logger = logging.getLogger(__name__)

@celery.task(bind=True, name='csv_tasks.export_patient_treatment_history')
def export_patient_treatment_history(self, patient_id):
  """
  Export patient treatment history to CSV
  """
  try:
      patient = Patient.query.get(patient_id)
      if not patient:
        return {'status': 'failed', 'error': 'Patient not found'}
      
      # Get all appointments with treatments
      appointments = Appointment.query.filter(
        Appointment.patient_id == patient_id,
        Appointment.status == 'completed'
      ).order_by(Appointment.appointment_date.desc()).all()
      
      # Create CSV in memory
      output = io.StringIO()
      writer = csv.writer(output)
      
      # Write header
      writer.writerow([
        'Appointment Date',
        'Doctor',
        'Specialization',
        'Symptoms',
        'Diagnosis',
        'Prescription',
        'Treatment Notes',
        'Follow-up Date'
      ])
      
      # Write data
      for appointment in appointments:
        treatment = appointment.treatment
        writer.writerow([
          appointment.appointment_date.strftime('%Y-%m-%d'),
          appointment.doctor.user.username,
          appointment.doctor.specialization,
          treatment.symptoms if treatment else '',
          treatment.diagnosis if treatment else '',
          treatment.prescription if treatment else '',
          treatment.notes if treatment else '',
          treatment.follow_up_date.strftime('%Y-%m-%d') if treatment and treatment.follow_up_date else ''
          ])
      
      csv_content = output.getvalue()
      output.close()
      
      # Store the CSV content in the task result
      self.update_state(
        state='SUCCESS',
        meta={
          'status': 'completed',
          'patient_id': patient_id,
          'patient_name': f"{patient.first_name} {patient.last_name}",
          'csv_content': csv_content,
          'record_count': len(appointments),
          'generated_at': datetime.now().isoformat()
        }
      )
      
      return {
        'status': 'completed',
        'patient_id': patient_id,
        'patient_name': f"{patient.first_name} {patient.last_name}",
        'record_count': len(appointments),
        'csv_content': csv_content  # In production, you might want to store this in cloud storage
      }
      
  except Exception as e:
      logger.error(f"Error in export_patient_treatment_history: {str(e)}")
      return {
        'status': 'failed',
        'error': str(e)
      }

@celery.task(bind=True, name='csv_tasks.export_doctor_appointments')
def export_doctor_appointments(self, doctor_id, start_date, end_date):
  """
  Export doctor's appointments to CSV for a date range
  """
  try:
      doctor = Doctor.query.get(doctor_id)
      if not doctor:
          return {'status': 'failed', 'error': 'Doctor not found'}
      
      start_date = datetime.strptime(start_date, '%Y-%m-%d')
      end_date = datetime.strptime(end_date, '%Y-%m-%d')
      
      appointments = Appointment.query.filter(
          and_(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date >= start_date,
            Appointment.appointment_date <= end_date
          )
      ).order_by(Appointment.appointment_date.asc()).all()
      
      output = io.StringIO()
      writer = csv.writer(output)
      
      writer.writerow([
        'Date',
        'Time',
        'Patient Name',
        'Patient Email',
        'Status',
        'Reason',
        'Diagnosis',
        'Prescription'
      ])
      
      for appointment in appointments:
        treatment = appointment.treatment
        writer.writerow([
          appointment.appointment_date.strftime('%Y-%m-%d'),
          appointment.appointment_time.strftime('%H:%M'),
          f"{appointment.patient.first_name} {appointment.patient.last_name}",
          appointment.patient.user.email,
          appointment.status,
          appointment.reason or '',
          treatment.diagnosis if treatment else '',
          treatment.prescription if treatment else ''
        ])
      
      csv_content = output.getvalue()
      output.close()
      
      return {
        'status': 'completed',
        'doctor_id': doctor_id,
        'doctor_name': doctor.user.username,
        'period': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
        'record_count': len(appointments),
        'csv_content': csv_content
      }
      
  except Exception as e:
      logger.error(f"Error in export_doctor_appointments: {str(e)}")
      return {
        'status': 'failed',
        'error': str(e)
      }

@celery.task(bind=True, name='csv_tasks.export_admin_report')
def export_admin_report(self, start_date, end_date):
  """
  Export comprehensive admin report
  """
  try:
      start_date = datetime.strptime(start_date, '%Y-%m-%d')
      end_date = datetime.strptime(end_date, '%Y-%m-%d')
      
      # Get all appointments in the date range
      appointments = Appointment.query.filter(
          and_(
            Appointment.appointment_date >= start_date,
            Appointment.appointment_date <= end_date
          )
      ).all()
      
      output = io.StringIO()
      writer = csv.writer(output)
      
      writer.writerow([
        'Appointment ID',
        'Date',
        'Time',
        'Patient Name',
        'Patient Email',
        'Doctor Name',
        'Specialization',
        'Status',
        'Reason',
        'Diagnosis',
        'Prescription'
      ])
      
      for appointment in appointments:
          treatment = appointment.treatment
          writer.writerow([
            appointment.id,
            appointment.appointment_date.strftime('%Y-%m-%d'),
            appointment.appointment_time.strftime('%H:%M'),
            f"{appointment.patient.first_name} {appointment.patient.last_name}",
            appointment.patient.user.email,
            appointment.doctor.user.username,
            appointment.doctor.specialization,
            appointment.status,
            appointment.reason or '',
            treatment.diagnosis if treatment else '',
            treatment.prescription if treatment else ''
          ])
      
      csv_content = output.getvalue()
      output.close()
      
      return {
        'status': 'completed',
        'period': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
        'record_count': len(appointments),
        'csv_content': csv_content
      }
      
  except Exception as e:
    logger.error(f"Error in export_admin_report: {str(e)}")
    return {
      'status': 'failed',
      'error': str(e)
    }