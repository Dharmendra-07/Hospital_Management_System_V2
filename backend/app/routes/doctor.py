from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import User, Doctor, Patient, Appointment, Treatment, DoctorAvailability, db
from app.utils.decorators import doctor_required
from datetime import datetime, timedelta, date
import json

doctor_bp = Blueprint('doctor', __name__)

@doctor_bp.route('/dashboard/stats', methods=['GET'])
@login_required
@doctor_required
def dashboard_stats():
  try:
      doctor = current_user.doctor_profile
      if not doctor:
          return jsonify({'error': 'Doctor profile not found'}), 404
      
      today = datetime.now().date()
      
      # Today's appointments
      today_appointments = Appointment.query.filter(
          Appointment.doctor_id == doctor.id,
          Appointment.appointment_date == today
      ).count()
      
      # Upcoming appointments (next 7 days)
      week_later = today + timedelta(days=7)
      upcoming_appointments = Appointment.query.filter(
          Appointment.doctor_id == doctor.id,
          Appointment.appointment_date >= today,
          Appointment.appointment_date <= week_later,
          Appointment.status == 'scheduled'
      ).count()
      
      # Total patients
      total_patients = db.session.query(Patient).join(Appointment).filter(
          Appointment.doctor_id == doctor.id
      ).distinct().count()
      
      # Monthly appointments
      month_start = today.replace(day=1)
      monthly_appointments = Appointment.query.filter(
          Appointment.doctor_id == doctor.id,
          Appointment.appointment_date >= month_start,
          Appointment.status == 'completed'
      ).count()
      
      return jsonify({
          'stats': {
              'today_appointments': today_appointments,
              'upcoming_appointments': upcoming_appointments,
              'total_patients': total_patients,
              'monthly_appointments': monthly_appointments
          },
          'doctor': {
              'name': current_user.username,
              'specialization': doctor.specialization,
              'department': doctor.department.name if doctor.department else None
          }
      }), 200
      
  except Exception as e:
      return jsonify({'error': str(e)}), 500

@doctor_bp.route('/appointments', methods=['GET'])
@login_required
@doctor_required
def get_appointments():
  try:
      doctor = current_user.doctor_profile
      if not doctor:
          return jsonify({'error': 'Doctor profile not found'}), 404
      
      status = request.args.get('status', '')
      date_filter = request.args.get('date', '')
      
      query = Appointment.query.filter_by(doctor_id=doctor.id)
      
      if status:
          query = query.filter(Appointment.status == status)
      
      if date_filter:
          filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
          query = query.filter(Appointment.appointment_date == filter_date)
      else:
          # Default to today and future appointments
          query = query.filter(Appointment.appointment_date >= datetime.now().date())
      
      appointments = query.order_by(
          Appointment.appointment_date.asc(),
          Appointment.appointment_time.asc()
      ).all()
      
      result = []
      for appointment in appointments:
          result.append({
              'id': appointment.id,
              'patient_id': appointment.patient_id,
              'patient_name': f"{appointment.patient.first_name} {appointment.patient.last_name}",
              'patient_email': appointment.patient.user.email,
              'patient_phone': appointment.patient.phone,
              'appointment_date': appointment.appointment_date.isoformat(),
              'appointment_time': appointment.appointment_time.strftime('%H:%M'),
              'status': appointment.status,
              'reason': appointment.reason,
              'created_at': appointment.created_at.isoformat()
          })
      
      return jsonify({'appointments': result}), 200
      
  except Exception as e:
      return jsonify({'error': str(e)}), 500

@doctor_bp.route('/appointments/<int:appointment_id>', methods=['GET'])
@login_required
@doctor_required
def get_appointment_detail(appointment_id):
  try:
      doctor = current_user.doctor_profile
      appointment = Appointment.query.filter_by(
          id=appointment_id,
          doctor_id=doctor.id
      ).first_or_404()
      
      # Get patient medical history with this doctor
      patient_history = Appointment.query.filter(
          Appointment.patient_id == appointment.patient_id,
          Appointment.doctor_id == doctor.id,
          Appointment.status == 'completed'
      ).order_by(Appointment.appointment_date.desc()).all()
      
      history_data = []
      for hist_appointment in patient_history:
          treatment_data = None
          if hist_appointment.treatment:
              treatment_data = {
                  'diagnosis': hist_appointment.treatment.diagnosis,
                  'symptoms': hist_appointment.treatment.symptoms,
                  'prescription': hist_appointment.treatment.prescription,
                  'notes': hist_appointment.treatment.notes
              }
          
          history_data.append({
              'appointment_date': hist_appointment.appointment_date.isoformat(),
              'reason': hist_appointment.reason,
              'treatment': treatment_data
          })
      
      current_treatment = None
      if appointment.treatment:
          current_treatment = {
              'diagnosis': appointment.treatment.diagnosis,
              'symptoms': appointment.treatment.symptoms,
              'prescription': appointment.treatment.prescription,
              'notes': appointment.treatment.notes,
              'follow_up_date': appointment.treatment.follow_up_date.isoformat() if appointment.treatment.follow_up_date else None
          }
      
      return jsonify({
          'appointment': {
              'id': appointment.id,
              'patient_name': f"{appointment.patient.first_name} {appointment.patient.last_name}",
              'patient_email': appointment.patient.user.email,
              'patient_phone': appointment.patient.phone,
              'date_of_birth': appointment.patient.date_of_birth.isoformat() if appointment.patient.date_of_birth else None,
              'gender': appointment.patient.gender,
              'blood_group': appointment.patient.blood_group,
              'appointment_date': appointment.appointment_date.isoformat(),
              'appointment_time': appointment.appointment_time.strftime('%H:%M'),
              'status': appointment.status,
              'reason': appointment.reason
          },
          'current_treatment': current_treatment,
          'patient_history': history_data
      }), 200
      
  except Exception as e:
      return jsonify({'error': str(e)}), 500

@doctor_bp.route('/appointments/<int:appointment_id>/status', methods=['PUT'])
@login_required
@doctor_required
def update_appointment_status(appointment_id):
  try:
      data = request.get_json()
      status = data.get('status')
      
      if status not in ['scheduled', 'completed', 'cancelled', 'no_show']:
          return jsonify({'error': 'Invalid status'}), 400
      
      doctor = current_user.doctor_profile
      appointment = Appointment.query.filter_by(
          id=appointment_id,
          doctor_id=doctor.id
      ).first_or_404()
      
      appointment.status = status
      appointment.updated_at = datetime.utcnow()
      
      db.session.commit()
      
      return jsonify({
          'message': f'Appointment marked as {status}',
          'appointment': {
              'id': appointment.id,
              'status': appointment.status
          }
      }), 200
      
  except Exception as e:
      db.session.rollback()
      return jsonify({'error': str(e)}), 500

@doctor_bp.route('/appointments/<int:appointment_id>/treatment', methods=['POST'])
@login_required
@doctor_required
def add_treatment(appointment_id):
  try:
      data = request.get_json()
      
      doctor = current_user.doctor_profile
      appointment = Appointment.query.filter_by(
          id=appointment_id,
          doctor_id=doctor.id
      ).first_or_404()
      
      # Check if appointment is completed
      if appointment.status != 'completed':
          return jsonify({'error': 'Can only add treatment for completed appointments'}), 400
      
      # Create or update treatment
      if appointment.treatment:
          treatment = appointment.treatment
      else:
          treatment = Treatment(appointment_id=appointment_id)
      
      treatment.diagnosis = data.get('diagnosis', '')
      treatment.symptoms = data.get('symptoms', '')
      treatment.prescription = data.get('prescription', '')
      treatment.notes = data.get('notes', '')
      
      if data.get('follow_up_date'):
          treatment.follow_up_date = datetime.strptime(data['follow_up_date'], '%Y-%m-%d').date()
      
      if not appointment.treatment:
          db.session.add(treatment)
      
      db.session.commit()
      
      return jsonify({
          'message': 'Treatment details saved successfully',
          'treatment': {
              'diagnosis': treatment.diagnosis,
              'symptoms': treatment.symptoms,
              'prescription': treatment.prescription,
              'notes': treatment.notes,
              'follow_up_date': treatment.follow_up_date.isoformat() if treatment.follow_up_date else None
          }
      }), 200
      
  except Exception as e:
      db.session.rollback()
      return jsonify({'error': str(e)}), 500

@doctor_bp.route('/patients', methods=['GET'])
@login_required
@doctor_required
def get_patients():
  try:
      doctor = current_user.doctor_profile
      search = request.args.get('search', '')
      
      # Get unique patients who have appointments with this doctor
      query = db.session.query(Patient).join(Appointment).filter(
          Appointment.doctor_id == doctor.id
      ).distinct()
      
      if search:
        query = query.filter(
          (Patient.first_name.ilike(f'%{search}%')) |
          (Patient.last_name.ilike(f'%{search}%')) |
          (Patient.phone.ilike(f'%{search}%'))
        )
      
      patients = query.all()
      
      result = []
      for patient in patients:
          # Get last appointment date
          last_appointment = Appointment.query.filter_by(
              patient_id=patient.id,
              doctor_id=doctor.id
          ).order_by(Appointment.appointment_date.desc()).first()
          
          result.append({
              'id': patient.id,
              'first_name': patient.first_name,
              'last_name': patient.last_name,
              'email': patient.user.email,
              'phone': patient.phone,
              'date_of_birth': patient.date_of_birth.isoformat() if patient.date_of_birth else None,
              'gender': patient.gender,
              'blood_group': patient.blood_group,
              'last_visit': last_appointment.appointment_date.isoformat() if last_appointment else None,
              'total_visits': Appointment.query.filter_by(
                  patient_id=patient.id,
                  doctor_id=doctor.id
              ).count()
          })
      
      return jsonify({'patients': result}), 200
      
  except Exception as e:
      return jsonify({'error': str(e)}), 500

@doctor_bp.route('/patients/<int:patient_id>/history', methods=['GET'])
@login_required
@doctor_required
def get_patient_history(patient_id):
  try:
      doctor = current_user.doctor_profile
      
      # Verify patient has appointments with this doctor
      patient = Patient.query.get_or_404(patient_id)
      
      appointments = Appointment.query.filter(
          Appointment.patient_id == patient_id,
          Appointment.doctor_id == doctor.id
      ).order_by(Appointment.appointment_date.desc()).all()
      
      history = []
      for appointment in appointments:
          treatment_data = None
          if appointment.treatment:
              treatment_data = {
                  'diagnosis': appointment.treatment.diagnosis,
                  'symptoms': appointment.treatment.symptoms,
                  'prescription': appointment.treatment.prescription,
                  'notes': appointment.treatment.notes,
                  'follow_up_date': appointment.treatment.follow_up_date.isoformat() if appointment.treatment.follow_up_date else None
              }
          
          history.append({
              'appointment_id': appointment.id,
              'appointment_date': appointment.appointment_date.isoformat(),
              'appointment_time': appointment.appointment_time.strftime('%H:%M'),
              'status': appointment.status,
              'reason': appointment.reason,
              'treatment': treatment_data
          })
      
      return jsonify({
          'patient': {
              'id': patient.id,
              'name': f"{patient.first_name} {patient.last_name}",
              'email': patient.user.email,
              'phone': patient.phone,
              'date_of_birth': patient.date_of_birth.isoformat() if patient.date_of_birth else None,
              'gender': patient.gender,
              'blood_group': patient.blood_group,
              'address': patient.address
          },
          'medical_history': history
      }), 200
      
  except Exception as e:
      return jsonify({'error': str(e)}), 500

@doctor_bp.route('/availability', methods=['GET'])
@login_required
@doctor_required
def get_availability():
  try:
      doctor = current_user.doctor_profile
      start_date = request.args.get('start_date', datetime.now().date().isoformat())
      end_date = request.args.get('end_date', (datetime.now() + timedelta(days=7)).date().isoformat())
      
      start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
      end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
      
      availability = DoctorAvailability.query.filter(
          DoctorAvailability.doctor_id == doctor.id,
          DoctorAvailability.date >= start_date,
          DoctorAvailability.date <= end_date
      ).order_by(DoctorAvailability.date.asc(), DoctorAvailability.start_time.asc()).all()
      
      result = []
      for slot in availability:
          # Check if slot has appointments
          appointment_count = Appointment.query.filter(
              Appointment.doctor_id == doctor.id,
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
      
      return jsonify({'availability': result}), 200
      
  except Exception as e:
      return jsonify({'error': str(e)}), 500

@doctor_bp.route('/availability', methods=['POST'])
@login_required
@doctor_required
def set_availability():
  try:
      data = request.get_json()
      doctor = current_user.doctor_profile
      
      date_str = data.get('date')
      start_time = data.get('start_time')
      end_time = data.get('end_time')
      max_patients = data.get('max_patients', 10)
      
      if not all([date_str, start_time, end_time]):
          return jsonify({'error': 'Date, start time, and end time are required'}), 400
      
      date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
      start_time_obj = datetime.strptime(start_time, '%H:%M').time()
      end_time_obj = datetime.strptime(end_time, '%H:%M').time()
      
      # Check if slot already exists
      existing_slot = DoctorAvailability.query.filter_by(
          doctor_id=doctor.id,
          date=date_obj,
          start_time=start_time_obj
      ).first()
      
      if existing_slot:
          existing_slot.end_time = end_time_obj
          existing_slot.max_patients = max_patients
          existing_slot.is_available = True
      else:
          new_slot = DoctorAvailability(
              doctor_id=doctor.id,
              date=date_obj,
              start_time=start_time_obj,
              end_time=end_time_obj,
              max_patients=max_patients,
              is_available=True
          )
          db.session.add(new_slot)
      
      db.session.commit()
      
      return jsonify({'message': 'Availability set successfully'}), 200
      
  except Exception as e:
      db.session.rollback()
      return jsonify({'error': str(e)}), 500

@doctor_bp.route('/availability/<int:slot_id>', methods=['DELETE'])
@login_required
@doctor_required
def delete_availability(slot_id):
  try:
      doctor = current_user.doctor_profile
      slot = DoctorAvailability.query.filter_by(
          id=slot_id,
          doctor_id=doctor.id
      ).first_or_404()
      
      # Check if slot has upcoming appointments
      upcoming_appointments = Appointment.query.filter(
          Appointment.doctor_id == doctor.id,
          Appointment.appointment_date == slot.date,
          Appointment.appointment_time == slot.start_time,
          Appointment.appointment_date >= datetime.now().date(),
          Appointment.status == 'scheduled'
      ).count()
      
      if upcoming_appointments > 0:
          return jsonify({
              'error': 'Cannot delete slot with upcoming appointments'
          }), 400
      
      db.session.delete(slot)
      db.session.commit()
      
      return jsonify({'message': 'Availability slot deleted successfully'}), 200
      
  except Exception as e:
      db.session.rollback()
      return jsonify({'error': str(e)}), 500

@doctor_bp.route('/profile', methods=['GET'])
@login_required
@doctor_required
def get_profile():
  try:
      doctor = current_user.doctor_profile
      if not doctor:
          return jsonify({'error': 'Doctor profile not found'}), 404
      
      return jsonify({
          'profile': {
              'username': current_user.username,
              'email': current_user.email,
              'specialization': doctor.specialization,
              'department': doctor.department.name if doctor.department else None,
              'qualification': doctor.qualification,
              'experience': doctor.experience,
              'consultation_fee': doctor.consultation_fee,
              'bio': doctor.bio,
              'is_available': doctor.is_available
          }
      }), 200
      
  except Exception as e:
      return jsonify({'error': str(e)}), 500

@doctor_bp.route('/profile', methods=['PUT'])
@login_required
@doctor_required
def update_profile():
  try:
      data = request.get_json()
      doctor = current_user.doctor_profile
      
      # Update user fields
      if 'username' in data and data['username'] != current_user.username:
          if User.query.filter(User.username == data['username'], User.id != current_user.id).first():
              return jsonify({'error': 'Username already exists'}), 400
          current_user.username = data['username']
      
      if 'email' in data and data['email'] != current_user.email:
          if User.query.filter(User.email == data['email'], User.id != current_user.id).first():
              return jsonify({'error': 'Email already exists'}), 400
          current_user.email = data['email']
      
      # Update doctor fields
      if 'qualification' in data:
          doctor.qualification = data['qualification']
      
      if 'experience' in data:
          doctor.experience = data['experience']
      
      if 'consultation_fee' in data:
          doctor.consultation_fee = data['consultation_fee']
      
      if 'bio' in data:
          doctor.bio = data['bio']
      
      if 'is_available' in data:
          doctor.is_available = data['is_available']
      
      if 'password' in data and data['password']:
          current_user.set_password(data['password'])
      
      db.session.commit()
      
      return jsonify({
          'message': 'Profile updated successfully',
          'profile': {
              'username': current_user.username,
              'email': current_user.email,
              'qualification': doctor.qualification,
              'experience': doctor.experience,
              'consultation_fee': doctor.consultation_fee,
              'bio': doctor.bio,
              'is_available': doctor.is_available
          }
      }), 200
      
  except Exception as e:
      db.session.rollback()
      return jsonify({'error': str(e)}), 500