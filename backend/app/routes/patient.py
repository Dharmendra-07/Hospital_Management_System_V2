from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import User, Doctor, Patient, Appointment, Treatment, DoctorAvailability, Department, db
from app.utils.decorators import patient_required
from datetime import datetime, timedelta, date
import json

patient_bp = Blueprint('patient', __name__)

@patient_bp.route('/dashboard/stats', methods=['GET'])
@login_required
@patient_required
def dashboard_stats():
  try:
      patient = current_user.patient_profile
      if not patient:
          return jsonify({'error': 'Patient profile not found'}), 404
      
      today = datetime.now().date()
      
      # Today's appointments
      today_appointments = Appointment.query.filter(
          Appointment.patient_id == patient.id,
          Appointment.appointment_date == today
      ).count()
      
      # Upcoming appointments
      upcoming_appointments = Appointment.query.filter(
          Appointment.patient_id == patient.id,
          Appointment.appointment_date >= today,
          Appointment.status == 'scheduled'
      ).count()
      
      # Total appointments
      total_appointments = Appointment.query.filter_by(patient_id=patient.id).count()
      
      # Completed appointments
      completed_appointments = Appointment.query.filter(
          Appointment.patient_id == patient.id,
          Appointment.status == 'completed'
      ).count()
      
      return jsonify({
          'stats': {
              'today_appointments': today_appointments,
              'upcoming_appointments': upcoming_appointments,
              'total_appointments': total_appointments,
              'completed_appointments': completed_appointments
          },
          'patient': {
              'name': f"{patient.first_name} {patient.last_name}",
              'email': current_user.email
          }
      }), 200
      
  except Exception as e:
      return jsonify({'error': str(e)}), 500

@patient_bp.route('/doctors', methods=['GET'])
@login_required
@patient_required
def get_doctors():
  try:
      search = request.args.get('search', '')
      specialization = request.args.get('specialization', '')
      department_id = request.args.get('department_id', type=int)
      
      query = Doctor.query.join(User).join(Department).filter(Doctor.is_available == True)
      
      if search:
          query = query.filter(
              (User.username.ilike(f'%{search}%')) |
              (Doctor.specialization.ilike(f'%{search}%')) |
              (Department.name.ilike(f'%{search}%'))
          )
      
      if specialization:
          query = query.filter(Doctor.specialization.ilike(f'%{specialization}%'))
      
      if department_id:
          query = query.filter(Doctor.department_id == department_id)
      
      doctors = query.all()
      
      result = []
      for doctor in doctors:
          # Get next available slot
          next_available = DoctorAvailability.query.filter(
              DoctorAvailability.doctor_id == doctor.id,
              DoctorAvailability.date >= datetime.now().date(),
              DoctorAvailability.is_available == True
          ).order_by(DoctorAvailability.date.asc(), DoctorAvailability.start_time.asc()).first()
          
          result.append({
              'id': doctor.id,
              'name': doctor.user.username,
              'email': doctor.user.email,
              'specialization': doctor.specialization,
              'department': doctor.department.name,
              'qualification': doctor.qualification,
              'experience': doctor.experience,
              'consultation_fee': doctor.consultation_fee,
              'bio': doctor.bio,
              'next_available': next_available.date.isoformat() if next_available else None,
              'rating': 4.5  # Placeholder for future rating system
          })
      
      return jsonify({'doctors': result}), 200
      
  except Exception as e:
      return jsonify({'error': str(e)}), 500

@patient_bp.route('/doctors/<int:doctor_id>', methods=['GET'])
@login_required
@patient_required
def get_doctor_detail(doctor_id):
  try:
      doctor = Doctor.query.filter_by(id=doctor_id, is_available=True).first_or_404()
      
      # Get availability for next 7 days
      start_date = datetime.now().date()
      end_date = start_date + timedelta(days=7)
      
      availability = DoctorAvailability.query.filter(
          DoctorAvailability.doctor_id == doctor_id,
          DoctorAvailability.date >= start_date,
          DoctorAvailability.date <= end_date,
          DoctorAvailability.is_available == True
      ).order_by(DoctorAvailability.date.asc(), DoctorAvailability.start_time.asc()).all()
      
      available_slots = []
      for slot in availability:
          # Check if slot is fully booked
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
      
      return jsonify({
          'doctor': {
              'id': doctor.id,
              'name': doctor.user.username,
              'email': doctor.user.email,
              'specialization': doctor.specialization,
              'department': doctor.department.name,
              'qualification': doctor.qualification,
              'experience': doctor.experience,
              'consultation_fee': doctor.consultation_fee,
              'bio': doctor.bio
          },
          'availability': available_slots
      }), 200
      
  except Exception as e:
      return jsonify({'error': str(e)}), 500

@patient_bp.route('/appointments', methods=['GET'])
@login_required
@patient_required
def get_appointments():
  try:
      patient = current_user.patient_profile
      status = request.args.get('status', '')
      
      query = Appointment.query.filter_by(patient_id=patient.id)
      
      if status:
          query = query.filter(Appointment.status == status)
      else:
          # Default to upcoming appointments
          query = query.filter(
              (Appointment.appointment_date >= datetime.now().date()) |
              (Appointment.status == 'scheduled')
          )
      
      appointments = query.order_by(
          Appointment.appointment_date.desc(),
          Appointment.appointment_time.desc()
      ).all()
      
      result = []
      for appointment in appointments:
          treatment_data = None
          if appointment.treatment:
              treatment_data = {
                  'diagnosis': appointment.treatment.diagnosis,
                  'prescription': appointment.treatment.prescription,
                  'notes': appointment.treatment.notes
              }
          
          result.append({
              'id': appointment.id,
              'doctor_name': appointment.doctor.user.username,
              'doctor_specialization': appointment.doctor.specialization,
              'appointment_date': appointment.appointment_date.isoformat(),
              'appointment_time': appointment.appointment_time.strftime('%H:%M'),
              'status': appointment.status,
              'reason': appointment.reason,
              'treatment': treatment_data,
              'created_at': appointment.created_at.isoformat()
          })
      
      return jsonify({'appointments': result}), 200
      
  except Exception as e:
      return jsonify({'error': str(e)}), 500

@patient_bp.route('/appointments', methods=['POST'])
@login_required
@patient_required
def book_appointment():
  try:
      data = request.get_json()
      patient = current_user.patient_profile
      
      required_fields = ['doctor_id', 'appointment_date', 'appointment_time', 'reason']
      for field in required_fields:
          if not data.get(field):
              return jsonify({'error': f'{field} is required'}), 400
      
      doctor_id = data['doctor_id']
      appointment_date = datetime.strptime(data['appointment_date'], '%Y-%m-%d').date()
      appointment_time = datetime.strptime(data['appointment_time'], '%H:%M').time()
      
      # Check if doctor exists and is available
      doctor = Doctor.query.filter_by(id=doctor_id, is_available=True).first()
      if not doctor:
          return jsonify({'error': 'Doctor not available'}), 400
      
      # Check if the requested slot is available
      availability_slot = DoctorAvailability.query.filter(
          DoctorAvailability.doctor_id == doctor_id,
          DoctorAvailability.date == appointment_date,
          DoctorAvailability.start_time == appointment_time,
          DoctorAvailability.is_available == True
      ).first()
      
      if not availability_slot:
          return jsonify({'error': 'Selected time slot is not available'}), 400
      
      # Check if slot is fully booked
      existing_appointments = Appointment.query.filter(
          Appointment.doctor_id == doctor_id,
          Appointment.appointment_date == appointment_date,
          Appointment.appointment_time == appointment_time,
          Appointment.status.in_(['scheduled', 'completed'])
      ).count()
      
      if existing_appointments >= availability_slot.max_patients:
          return jsonify({'error': 'Selected time slot is fully booked'}), 400
      
      # Check if patient already has an appointment at the same time
      patient_conflict = Appointment.query.filter(
          Appointment.patient_id == patient.id,
          Appointment.appointment_date == appointment_date,
          Appointment.appointment_time == appointment_time,
          Appointment.status == 'scheduled'
      ).first()
      
      if patient_conflict:
          return jsonify({'error': 'You already have an appointment at this time'}), 400
      
      # Create appointment
      appointment = Appointment(
          patient_id=patient.id,
          doctor_id=doctor_id,
          appointment_date=appointment_date,
          appointment_time=appointment_time,
          reason=data['reason'],
          status='scheduled'
      )
      
      db.session.add(appointment)
      db.session.commit()
      
      return jsonify({
          'message': 'Appointment booked successfully',
          'appointment': {
              'id': appointment.id,
              'doctor_name': doctor.user.username,
              'appointment_date': appointment.appointment_date.isoformat(),
              'appointment_time': appointment.appointment_time.strftime('%H:%M'),
              'status': appointment.status
          }
      }), 201
      
  except Exception as e:
      db.session.rollback()
      return jsonify({'error': str(e)}), 500

@patient_bp.route('/appointments/<int:appointment_id>', methods=['PUT'])
@login_required
@patient_required
def update_appointment(appointment_id):
  try:
      data = request.get_json()
      patient = current_user.patient_profile
      
      appointment = Appointment.query.filter_by(
          id=appointment_id,
          patient_id=patient.id
      ).first_or_404()
      
      # Check if appointment can be modified (at least 2 hours before)
      appointment_datetime = datetime.combine(
          appointment.appointment_date,
          appointment.appointment_time
      )
      if datetime.now() > appointment_datetime - timedelta(hours=2):
          return jsonify({'error': 'Cannot modify appointment less than 2 hours before'}), 400
      
      if 'reason' in data:
          appointment.reason = data['reason']
      
      if 'appointment_date' in data and 'appointment_time' in data:
          new_date = datetime.strptime(data['appointment_date'], '%Y-%m-%d').date()
          new_time = datetime.strptime(data['appointment_time'], '%H:%M').time()
          
          # Check new slot availability
          availability_slot = DoctorAvailability.query.filter(
              DoctorAvailability.doctor_id == appointment.doctor_id,
              DoctorAvailability.date == new_date,
              DoctorAvailability.start_time == new_time,
              DoctorAvailability.is_available == True
          ).first()
          
          if not availability_slot:
              return jsonify({'error': 'Selected time slot is not available'}), 400
          
          # Check if new slot is available
          existing_appointments = Appointment.query.filter(
              Appointment.doctor_id == appointment.doctor_id,
              Appointment.appointment_date == new_date,
              Appointment.appointment_time == new_time,
              Appointment.status.in_(['scheduled', 'completed'])
          ).count()
          
          if existing_appointments >= availability_slot.max_patients:
              return jsonify({'error': 'Selected time slot is fully booked'}), 400
          
          appointment.appointment_date = new_date
          appointment.appointment_time = new_time
      
      appointment.updated_at = datetime.utcnow()
      db.session.commit()
      
      return jsonify({
          'message': 'Appointment updated successfully',
          'appointment': {
              'id': appointment.id,
              'appointment_date': appointment.appointment_date.isoformat(),
              'appointment_time': appointment.appointment_time.strftime('%H:%M'),
              'reason': appointment.reason
          }
      }), 200
      
  except Exception as e:
      db.session.rollback()
      return jsonify({'error': str(e)}), 500

@patient_bp.route('/appointments/<int:appointment_id>', methods=['DELETE'])
@login_required
@patient_required
def cancel_appointment(appointment_id):
  try:
      patient = current_user.patient_profile
      
      appointment = Appointment.query.filter_by(
          id=appointment_id,
          patient_id=patient.id
      ).first_or_404()
      
      # Check if appointment can be cancelled (at least 2 hours before)
      appointment_datetime = datetime.combine(
          appointment.appointment_date,
          appointment.appointment_time
      )
      if datetime.now() > appointment_datetime - timedelta(hours=2):
          return jsonify({'error': 'Cannot cancel appointment less than 2 hours before'}), 400
      
      if appointment.status == 'cancelled':
          return jsonify({'error': 'Appointment is already cancelled'}), 400
      
      appointment.status = 'cancelled'
      appointment.updated_at = datetime.utcnow()
      db.session.commit()
      
      return jsonify({'message': 'Appointment cancelled successfully'}), 200
      
  except Exception as e:
      db.session.rollback()
      return jsonify({'error': str(e)}), 500

@patient_bp.route('/appointments/<int:appointment_id>', methods=['GET'])
@login_required
@patient_required
def get_appointment_detail(appointment_id):
  try:
      patient = current_user.patient_profile
      
      appointment = Appointment.query.filter_by(
          id=appointment_id,
          patient_id=patient.id
      ).first_or_404()
      
      treatment_data = None
      if appointment.treatment:
          treatment_data = {
              'diagnosis': appointment.treatment.diagnosis,
              'symptoms': appointment.treatment.symptoms,
              'prescription': appointment.treatment.prescription,
              'notes': appointment.treatment.notes,
              'follow_up_date': appointment.treatment.follow_up_date.isoformat() if appointment.treatment.follow_up_date else None
          }
      
      return jsonify({
          'appointment': {
              'id': appointment.id,
              'doctor_name': appointment.doctor.user.username,
              'doctor_specialization': appointment.doctor.specialization,
              'doctor_email': appointment.doctor.user.email,
              'appointment_date': appointment.appointment_date.isoformat(),
              'appointment_time': appointment.appointment_time.strftime('%H:%M'),
              'status': appointment.status,
              'reason': appointment.reason,
              'created_at': appointment.created_at.isoformat()
          },
          'treatment': treatment_data
      }), 200
      
  except Exception as e:
      return jsonify({'error': str(e)}), 500

@patient_bp.route('/medical-history', methods=['GET'])
@login_required
@patient_required
def get_medical_history():
  try:
      patient = current_user.patient_profile
      
      appointments = Appointment.query.filter(
          Appointment.patient_id == patient.id,
          Appointment.status == 'completed'
      ).order_by(Appointment.appointment_date.desc()).all()
      
      medical_history = []
      for appointment in appointments:
          if appointment.treatment:
              medical_history.append({
                  'appointment_date': appointment.appointment_date.isoformat(),
                  'doctor_name': appointment.doctor.user.username,
                  'doctor_specialization': appointment.doctor.specialization,
                  'diagnosis': appointment.treatment.diagnosis,
                  'symptoms': appointment.treatment.symptoms,
                  'prescription': appointment.treatment.prescription,
                  'notes': appointment.treatment.notes,
                  'follow_up_date': appointment.treatment.follow_up_date.isoformat() if appointment.treatment.follow_up_date else None
              })
      
      return jsonify({'medical_history': medical_history}), 200
      
  except Exception as e:
      return jsonify({'error': str(e)}), 500

@patient_bp.route('/departments', methods=['GET'])
@login_required
@patient_required
def get_departments():
  try:
      departments = Department.query.all()
      
      result = []
      for dept in departments:
          doctor_count = Doctor.query.filter_by(
              department_id=dept.id,
              is_available=True
          ).count()
          
          result.append({
              'id': dept.id,
              'name': dept.name,
              'description': dept.description,
              'doctor_count': doctor_count
          })
      
      return jsonify({'departments': result}), 200
      
  except Exception as e:
      return jsonify({'error': str(e)}), 500

@patient_bp.route('/profile', methods=['GET'])
@login_required
@patient_required
def get_profile():
  try:
      patient = current_user.patient_profile
      if not patient:
          return jsonify({'error': 'Patient profile not found'}), 404
      
      return jsonify({
          'profile': {
              'username': current_user.username,
              'email': current_user.email,
              'first_name': patient.first_name,
              'last_name': patient.last_name,
              'date_of_birth': patient.date_of_birth.isoformat() if patient.date_of_birth else None,
              'gender': patient.gender,
              'phone': patient.phone,
              'address': patient.address,
              'emergency_contact': patient.emergency_contact,
              'blood_group': patient.blood_group
          }
      }), 200
      
  except Exception as e:
      return jsonify({'error': str(e)}), 500

@patient_bp.route('/profile', methods=['PUT'])
@login_required
@patient_required
def update_profile():
  try:
      data = request.get_json()
      patient = current_user.patient_profile
      
      # Update user fields
      if 'username' in data and data['username'] != current_user.username:
          if User.query.filter(User.username == data['username'], User.id != current_user.id).first():
              return jsonify({'error': 'Username already exists'}), 400
          current_user.username = data['username']
      
      if 'email' in data and data['email'] != current_user.email:
          if User.query.filter(User.email == data['email'], User.id != current_user.id).first():
              return jsonify({'error': 'Email already exists'}), 400
          current_user.email = data['email']
      
      # Update patient fields
      if 'first_name' in data:
          patient.first_name = data['first_name']
      
      if 'last_name' in data:
          patient.last_name = data['last_name']
      
      if 'date_of_birth' in data:
          patient.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
      
      if 'gender' in data:
          patient.gender = data['gender']
      
      if 'phone' in data:
          patient.phone = data['phone']
      
      if 'address' in data:
          patient.address = data['address']
      
      if 'emergency_contact' in data:
          patient.emergency_contact = data['emergency_contact']
      
      if 'blood_group' in data:
          patient.blood_group = data['blood_group']
      
      if 'password' in data and data['password']:
          current_user.set_password(data['password'])
      
      db.session.commit()
      
      return jsonify({
          'message': 'Profile updated successfully',
          'profile': {
              'username': current_user.username,
              'email': current_user.email,
              'first_name': patient.first_name,
              'last_name': patient.last_name,
              'date_of_birth': patient.date_of_birth.isoformat() if patient.date_of_birth else None,
              'gender': patient.gender,
              'phone': patient.phone,
              'address': patient.address,
              'emergency_contact': patient.emergency_contact,
              'blood_group': patient.blood_group
          }
      }), 200
      
  except Exception as e:
      db.session.rollback()
      return jsonify({'error': str(e)}), 500