from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from celery_worker import celery
from celery_worker.csv_tasks import export_patient_treatment_history
from celery_worker.report_tasks import generate_custom_report
from celery_worker.reminder_tasks import send_custom_reminder
from app.utils.decorators import patient_required, doctor_required, admin_required
import json

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/export/patient-history', methods=['POST'])
@login_required
@patient_required
def trigger_patient_history_export():
  """
  Trigger CSV export of patient treatment history
  """
  try:
      patient_id = current_user.patient_profile.id
      
      # Start the async task
      task = export_patient_treatment_history.delay(patient_id)
      
      return jsonify({
          'message': 'Export started successfully',
          'task_id': task.id,
          'status_url': f'/api/tasks/status/{task.id}'
      }), 202
      
  except Exception as e:
      return jsonify({'error': str(e)}), 500

@tasks_bp.route('/export/doctor-appointments', methods=['POST'])
@login_required
@doctor_required
def trigger_doctor_appointments_export():
  """
  Trigger CSV export of doctor's appointments
  """
  try:
      data = request.get_json()
      doctor_id = current_user.doctor_profile.id
      start_date = data.get('start_date')
      end_date = data.get('end_date')
      
      if not start_date or not end_date:
          return jsonify({'error': 'start_date and end_date are required'}), 400
      
      from celery_worker.csv_tasks import export_doctor_appointments
      task = export_doctor_appointments.delay(doctor_id, start_date, end_date)
      
      return jsonify({
          'message': 'Export started successfully',
          'task_id': task.id,
          'status_url': f'/api/tasks/status/{task.id}'
      }), 202
      
  except Exception as e:
      return jsonify({'error': str(e)}), 500

@tasks_bp.route('/reports/custom', methods=['POST'])
@login_required
@doctor_required
def trigger_custom_report():
  """
  Trigger custom report generation
  """
  try:
      data = request.get_json()
      doctor_id = current_user.doctor_profile.id
      start_date = data.get('start_date')
      end_date = data.get('end_date')
      email = data.get('email', current_user.email)
      
      if not start_date or not end_date:
        return jsonify({'error': 'start_date and end_date are required'}), 400
      
      task = generate_custom_report.delay(doctor_id, start_date, end_date, email)
      
      return jsonify({
        'message': 'Report generation started',
        'task_id': task.id,
        'status_url': f'/api/tasks/status/{task.id}'
      }), 202
      
  except Exception as e:
    return jsonify({'error': str(e)}), 500

@tasks_bp.route('/reminders/custom', methods=['POST'])
@login_required
@admin_required
def trigger_custom_reminder():
  """
  Trigger custom reminder for an appointment (Admin only)
  """
  try:
      data = request.get_json()
      appointment_id = data.get('appointment_id')
      
      if not appointment_id:
        return jsonify({'error': 'appointment_id is required'}), 400
      
      task = send_custom_reminder.delay(appointment_id)
      
      return jsonify({
        'message': 'Reminder sent',
        'task_id': task.id,
        'status_url': f'/api/tasks/status/{task.id}'
      }), 202
      
  except Exception as e:
    return jsonify({'error': str(e)}), 500

@tasks_bp.route('/status/<task_id>', methods=['GET'])
@login_required
def get_task_status(task_id):
  """
  Get status of an async task
  """
  try:
      from celery_worker.tasks import get_task_status
      task_result = get_task_status.delay(task_id)
      
      # Wait for the result (in production, you might not want to wait)
      result = task_result.get(timeout=5)
      
      return jsonify(result), 200
      
  except Exception as e:
      return jsonify({'error': str(e)}), 500

@tasks_bp.route('/exports/history', methods=['GET'])
@login_required
def get_export_history():
  """
  Get history of exports for the current user
  """
  try:
    # This would typically query a database table storing export history
    # For now, return a mock response
    return jsonify({
      'exports': [
        {
          'id': 1,
          'type': 'patient_history',
          'status': 'completed',
          'created_at': '2024-01-15T10:30:00Z',
          'record_count': 15,
          'download_url': '/api/tasks/download/1'
        }
      ]
    }), 200
      
  except Exception as e:
    return jsonify({'error': str(e)}), 500

@tasks_bp.route('/download/<export_id>', methods=['GET'])
@login_required
def download_export(export_id):
  """
  Download a completed export
  """
  try:
    # In production, this would serve the actual file from storage
    # For now, return a mock response
    
    return jsonify({
      'message': 'Download endpoint',
      'export_id': export_id,
      'note': 'In production, this would return the actual file'
    }), 200
      
  except Exception as e:
    return jsonify({'error': str(e)}), 500