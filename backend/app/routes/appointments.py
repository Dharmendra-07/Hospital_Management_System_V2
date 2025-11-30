from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import Appointment, Treatment, Doctor, Patient, db
from app.services.appointment_service import AppointmentService
from app.utils.decorators import admin_required, doctor_required, patient_required
from datetime import datetime, timedelta
import json

appointments_bp = Blueprint('appointments', __name__)

@appointments_bp.route('/history/<int:appointment_id>', methods=['GET'])
@login_required
def get_appointment_history(appointment_id):
  """
  Get complete history of an appointment
  Accessible by admin, treating doctor, or the patient
  """
  try:
      appointment = Appointment.query.get_or_404(appointment_id)
      
      # Check permissions
      if current_user.role == 'patient':
        if appointment.patient.user_id != current_user.id:
          return jsonify({'error': 'Access denied'}), 403
      elif current_user.role == 'doctor':
        if appointment.doctor.user_id != current_user.id:
          return jsonify({'error': 'Access denied'}), 403
      # Admin has access to all
      
      success, result = AppointmentService.get_appointment_history(appointment_id)
      
      if not success:
        return jsonify({'error': result}), 500
      
      return jsonify({'history': result}), 200
      
  except Exception as e:
    return jsonify({'error': str(e)}), 500

@appointments_bp.route('/conflicts/check', methods=['POST'])
@login_required
def check_appointment_conflicts():
  """
  Check for scheduling conflicts before booking
  """
  try:
      data = request.get_json()
      
      required_fields = ['doctor_id', 'appointment_date', 'appointment_time']
      for field in required_fields:
          if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
      
      doctor_id = data['doctor_id']
      appointment_date = datetime.strptime(data['appointment_date'], '%Y-%m-%d').date()
      appointment_time = datetime.strptime(data['appointment_time'], '%H:%M').time()
      
      # Get patient ID based on user role
      if current_user.role == 'patient':
        patient_id = current_user.patient_profile.id
      else:
        patient_id = data.get('patient_id')
        if not patient_id:
          return jsonify({'error': 'patient_id is required for non-patient users'}), 400
      
      exclude_appointment_id = data.get('exclude_appointment_id')
      
      # Validate appointment
      valid, message = AppointmentService.validate_appointment_booking(
          doctor_id, patient_id, appointment_date, appointment_time, exclude_appointment_id
      )
      
      if valid:
          return jsonify({
            'available': True,
            'message': message
          }), 200
      else:
          return jsonify({
            'available': False,
            'message': message
          }), 200
          
  except Exception as e:
    return jsonify({'error': str(e)}), 500

@appointments_bp.route('/conflicts/analytics', methods=['GET'])
@login_required
@admin_required
def get_conflict_analytics():
  """
  Get analytics about scheduling conflicts (Admin only)
  """
  try:
      start_date = request.args.get('start_date')
      end_date = request.args.get('end_date')
      
      if start_date:
          start_date = datetime.strptime(start_date, '%Y-%m-%d')
      if end_date:
          end_date = datetime.strptime(end_date, '%Y-%m-%d')
      
      success, result = AppointmentService.get_conflict_analytics(start_date, end_date)
      
      if not success:
          return jsonify({'error': result}), 500
      
      return jsonify({'analytics': result}), 200
      
  except Exception as e:
      return jsonify({'error': str(e)}), 500

@appointments_bp.route('/bulk-availability', methods=['POST'])
@login_required
def get_bulk_availability():
  """
  Get availability for multiple doctors at once
  """
  try:
      data = request.get_json()
      
      doctor_ids = data.get('doctor_ids', [])
      start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d').date()
      end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d').date()
      
      if not doctor_ids:
          return jsonify({'error': 'doctor_ids are required'}), 400
      
      availability_data = {}
      
      for doctor_id in doctor_ids:
          doctor = Doctor.query.get(doctor_id)
          if not doctor:
            continue
          
          # Get availability slots
          availability_slots = DoctorAvailability.query.filter(
              DoctorAvailability.doctor_id == doctor_id,
              DoctorAvailability.date >= start_date,
              DoctorAvailability.date <= end_date,
              DoctorAvailability.is_available == True
          ).order_by(DoctorAvailability.date.asc(), DoctorAvailability.start_time.asc()).all()
          
          available_slots = []
          for slot in availability_slots:
              # Check current bookings
              appointment_count = Appointment.query.filter(
                Appointment.doctor_id == doctor_id,
                Appointment.appointment_date == slot.date,
                Appointment.appointment_time == slot.start_time,
                Appointment.status.in_(['scheduled', 'completed'])
              ).count()
              
              if appointment_count < slot.max_patients:
                  available_slots.append({
                    'date': slot.date.isoformat(),
                    'start_time': slot.start_time.strftime('%H:%M'),
                    'end_time': slot.end_time.strftime('%H:%M'),
                    'available_slots': slot.max_patients - appointment_count
                  })
          
          availability_data[doctor_id] = {
            'doctor_name': doctor.user.username,
            'specialization': doctor.specialization,
            'available_slots': available_slots
          }
      
      return jsonify({'availability': availability_data}), 200
      
  except Exception as e:
    return jsonify({'error': str(e)}), 500

@appointments_bp.route('/treatment-records', methods=['GET'])
@login_required
def get_treatment_records():
  """
  Get treatment records with filtering options
  """
  try:
      patient_id = request.args.get('patient_id')
      doctor_id = request.args.get('doctor_id')
      start_date = request.args.get('start_date')
      end_date = request.args.get('end_date')
      
      query = Appointment.query.join(Treatment).filter(
        Appointment.status == 'completed'
      )
      
      # Apply filters based on user role and permissions
      if current_user.role == 'patient':
        query = query.filter(Appointment.patient_id == current_user.patient_profile.id)
      elif current_user.role == 'doctor':
        query = query.filter(Appointment.doctor_id == current_user.doctor_profile.id)
      
      if patient_id and current_user.role in ['admin', 'doctor']:
        query = query.filter(Appointment.patient_id == patient_id)
      
      if doctor_id and current_user.role in ['admin', 'patient']:
        query = query.filter(Appointment.doctor_id == doctor_id)
      
      if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        query = query.filter(Appointment.appointment_date >= start_date)
      
      if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        query = query.filter(Appointment.appointment_date <= end_date)
      
      appointments = query.order_by(Appointment.appointment_date.desc()).all()
      
      treatment_records = []
      for appointment in appointments:
          treatment_records.append({
            'appointment_id': appointment.id,
            'appointment_date': appointment.appointment_date.isoformat(),
            'patient_name': f"{appointment.patient.first_name} {appointment.patient.last_name}",
            'doctor_name': appointment.doctor.user.username,
            'specialization': appointment.doctor.specialization,
            'diagnosis': appointment.treatment.diagnosis if appointment.treatment else None,
            'prescription': appointment.treatment.prescription if appointment.treatment else None,
            'symptoms': appointment.treatment.symptoms if appointment.treatment else None,
            'notes': appointment.treatment.notes if appointment.treatment else None
          })
      
      return jsonify({'treatment_records': treatment_records}), 200
      
  except Exception as e:
    return jsonify({'error': str(e)}), 500