from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import User, Doctor, Patient, Department, Appointment, db
from app.utils.decorators import admin_required
from datetime import datetime, timedelta
import json

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard/stats', methods=['GET'])
@login_required
@admin_required
def dashboard_stats():
  try:
      # Get basic statistics
      total_patients = Patient.query.count()
      total_doctors = Doctor.query.count()
      
      # Appointment statistics
      today = datetime.now().date()
      total_appointments = Appointment.query.count()
      today_appointments = Appointment.query.filter(
          Appointment.appointment_date == today
      ).count()
      
      # Recent appointments (last 7 days)
      week_ago = today - timedelta(days=7)
      recent_appointments = Appointment.query.filter(
          Appointment.appointment_date >= week_ago
      ).count()
      
      # Department statistics
      departments = Department.query.all()
      department_stats = []
      for dept in departments:
          doctor_count = Doctor.query.filter_by(department_id=dept.id).count()
          department_stats.append({
              'id': dept.id,
              'name': dept.name,
              'doctor_count': doctor_count,
              'description': dept.description
          })
      
      return jsonify({
          'stats': {
              'total_patients': total_patients,
              'total_doctors': total_doctors,
              'total_appointments': total_appointments,
              'today_appointments': today_appointments,
              'recent_appointments': recent_appointments
          },
          'departments': department_stats
      }), 200
      
  except Exception as e:
      return jsonify({'error': str(e)}), 500

@admin_bp.route('/doctors', methods=['GET'])
@login_required
@admin_required
def get_doctors():
  try:
      search = request.args.get('search', '')
      department_id = request.args.get('department_id', type=int)
      
      query = Doctor.query.join(User).join(Department)
      
      if search:
          query = query.filter(
              (User.username.ilike(f'%{search}%')) |
              (Doctor.specialization.ilike(f'%{search}%')) |
              (Department.name.ilike(f'%{search}%'))
          )
      
      if department_id:
          query = query.filter(Doctor.department_id == department_id)
      
      doctors = query.all()
      
      result = []
      for doctor in doctors:
          result.append({
              'id': doctor.id,
              'username': doctor.user.username,
              'email': doctor.user.email,
              'specialization': doctor.specialization,
              'department': doctor.department.name,
              'qualification': doctor.qualification,
              'experience': doctor.experience,
              'consultation_fee': doctor.consultation_fee,
              'is_available': doctor.is_available,
              'created_at': doctor.created_at.isoformat()
          })
      
      return jsonify({'doctors': result}), 200
      
  except Exception as e:
      return jsonify({'error': str(e)}), 500

@admin_bp.route('/doctors', methods=['POST'])
@login_required
@admin_required
def add_doctor():
  try:
      data = request.get_json()
      
      # Validate required fields
      required_fields = ['username', 'email', 'password', 'specialization', 'department_id']
      for field in required_fields:
          if not data.get(field):
              return jsonify({'error': f'{field} is required'}), 400
      
      # Check if user already exists
      if User.query.filter_by(username=data['username']).first():
          return jsonify({'error': 'Username already exists'}), 400
      
      if User.query.filter_by(email=data['email']).first():
          return jsonify({'error': 'Email already exists'}), 400
      
      # Check if department exists
      department = Department.query.get(data['department_id'])
      if not department:
          return jsonify({'error': 'Department not found'}), 404
      
      # Create user
      user = User(
          username=data['username'],
          email=data['email'],
          role='doctor'
      )
      user.set_password(data['password'])
      
      db.session.add(user)
      db.session.flush()  # Get user ID without committing
      
      # Create doctor profile
      doctor = Doctor(
          user_id=user.id,
          department_id=data['department_id'],
          specialization=data['specialization'],
          qualification=data.get('qualification', ''),
          experience=data.get('experience', 0),
          consultation_fee=data.get('consultation_fee', 0.0),
          bio=data.get('bio', ''),
          is_available=data.get('is_available', True)
      )
      
      db.session.add(doctor)
      db.session.commit()
      
      return jsonify({
          'message': 'Doctor added successfully',
          'doctor': {
              'id': doctor.id,
              'username': user.username,
              'email': user.email,
              'specialization': doctor.specialization,
              'department': department.name
          }
      }), 201
      
  except Exception as e:
      db.session.rollback()
      return jsonify({'error': str(e)}), 500

@admin_bp.route('/doctors/<int:doctor_id>', methods=['PUT'])
@login_required
@admin_required
def update_doctor(doctor_id):
  try:
      data = request.get_json()
      
      doctor = Doctor.query.get_or_404(doctor_id)
      user = doctor.user
      
      # Update user fields
      if 'username' in data and data['username'] != user.username:
          if User.query.filter(User.username == data['username'], User.id != user.id).first():
              return jsonify({'error': 'Username already exists'}), 400
          user.username = data['username']
      
      if 'email' in data and data['email'] != user.email:
          if User.query.filter(User.email == data['email'], User.id != user.id).first():
              return jsonify({'error': 'Email already exists'}), 400
          user.email = data['email']
      
      # Update doctor fields
      if 'specialization' in data:
          doctor.specialization = data['specialization']
      
      if 'department_id' in data:
          department = Department.query.get(data['department_id'])
          if not department:
              return jsonify({'error': 'Department not found'}), 404
          doctor.department_id = data['department_id']
      
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
          user.set_password(data['password'])
      
      db.session.commit()
      
      return jsonify({
          'message': 'Doctor updated successfully',
          'doctor': {
              'id': doctor.id,
              'username': user.username,
              'email': user.email,
              'specialization': doctor.specialization,
              'department': doctor.department.name,
              'is_available': doctor.is_available
          }
      }), 200
      
  except Exception as e:
      db.session.rollback()
      return jsonify({'error': str(e)}), 500

@admin_bp.route('/doctors/<int:doctor_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_doctor(doctor_id):
  try:
      doctor = Doctor.query.get_or_404(doctor_id)
      user = doctor.user
      
      # Check if doctor has upcoming appointments
      upcoming_appointments = Appointment.query.filter(
          Appointment.doctor_id == doctor_id,
          Appointment.appointment_date >= datetime.now().date(),
          Appointment.status == 'scheduled'
      ).count()
      
      if upcoming_appointments > 0:
          return jsonify({
              'error': 'Cannot delete doctor with upcoming appointments'
          }), 400
      
      # Deactivate user instead of deleting to maintain referential integrity
      user.is_active = False
      db.session.commit()
      
      return jsonify({'message': 'Doctor deactivated successfully'}), 200
      
  except Exception as e:
      db.session.rollback()
      return jsonify({'error': str(e)}), 500

@admin_bp.route('/patients', methods=['GET'])
@login_required
@admin_required
def get_patients():
  try:
      search = request.args.get('search', '')
      
      query = Patient.query.join(User)
      
      if search:
          query = query.filter(
              (User.username.ilike(f'%{search}%')) |
              (Patient.first_name.ilike(f'%{search}%')) |
              (Patient.last_name.ilike(f'%{search}%')) |
              (Patient.phone.ilike(f'%{search}%'))
          )
      
      patients = query.all()
      
      result = []
      for patient in patients:
          result.append({
              'id': patient.id,
              'user_id': patient.user_id,
              'username': patient.user.username,
              'email': patient.user.email,
              'first_name': patient.first_name,
              'last_name': patient.last_name,
              'date_of_birth': patient.date_of_birth.isoformat() if patient.date_of_birth else None,
              'gender': patient.gender,
              'phone': patient.phone,
              'blood_group': patient.blood_group,
              'is_active': patient.user.is_active,
              'created_at': patient.created_at.isoformat()
          })
      
      return jsonify({'patients': result}), 200
      
  except Exception as e:
      return jsonify({'error': str(e)}), 500

@admin_bp.route('/patients/<int:patient_id>', methods=['PUT'])
@login_required
@admin_required
def update_patient(patient_id):
  try:
      data = request.get_json()
      
      patient = Patient.query.get_or_404(patient_id)
      user = patient.user
      
      # Update user fields
      if 'username' in data and data['username'] != user.username:
          if User.query.filter(User.username == data['username'], User.id != user.id).first():
              return jsonify({'error': 'Username already exists'}), 400
          user.username = data['username']
      
      if 'email' in data and data['email'] != user.email:
          if User.query.filter(User.email == data['email'], User.id != user.id).first():
              return jsonify({'error': 'Email already exists'}), 400
          user.email = data['email']
      
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
      
      if 'blood_group' in data:
          patient.blood_group = data['blood_group']
      
      if 'is_active' in data:
          user.is_active = data['is_active']
      
      db.session.commit()
      
      return jsonify({
          'message': 'Patient updated successfully',
          'patient': {
              'id': patient.id,
              'username': user.username,
              'email': user.email,
              'first_name': patient.first_name,
              'last_name': patient.last_name,
              'is_active': user.is_active
          }
      }), 200
      
  except Exception as e:
      db.session.rollback()
      return jsonify({'error': str(e)}), 500

@admin_bp.route('/appointments', methods=['GET'])
@login_required
@admin_required
def get_appointments():
  try:
      status = request.args.get('status', '')
      date_from = request.args.get('date_from', '')
      date_to = request.args.get('date_to', '')
      
      query = Appointment.query.join(Patient).join(Doctor).join(User)
      
      if status:
          query = query.filter(Appointment.status == status)
      
      if date_from:
          date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
          query = query.filter(Appointment.appointment_date >= date_from)
      
      if date_to:
          date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
          query = query.filter(Appointment.appointment_date <= date_to)
      
      # Order by date and time
      appointments = query.order_by(
          Appointment.appointment_date.desc(),
          Appointment.appointment_time.desc()
      ).all()
      
      result = []
      for appointment in appointments:
          result.append({
              'id': appointment.id,
              'patient_name': f"{appointment.patient.first_name} {appointment.patient.last_name}",
              'doctor_name': appointment.doctor.user.username,
              'specialization': appointment.doctor.specialization,
              'appointment_date': appointment.appointment_date.isoformat(),
              'appointment_time': appointment.appointment_time.strftime('%H:%M'),
              'status': appointment.status,
              'reason': appointment.reason,
              'created_at': appointment.created_at.isoformat()
          })
      
      return jsonify({'appointments': result}), 200
      
  except Exception as e:
      return jsonify({'error': str(e)}), 500

@admin_bp.route('/departments', methods=['GET'])
@login_required
@admin_required
def get_departments():
  try:
      departments = Department.query.all()
      
      result = []
      for dept in departments:
          doctor_count = Doctor.query.filter_by(department_id=dept.id).count()
          result.append({
              'id': dept.id,
              'name': dept.name,
              'description': dept.description,
              'doctor_count': doctor_count,
              'created_at': dept.created_at.isoformat()
          })
      
      return jsonify({'departments': result}), 200
      
  except Exception as e:
      return jsonify({'error': str(e)}), 500

@admin_bp.route('/departments', methods=['POST'])
@login_required
@admin_required
def add_department():
  try:
      data = request.get_json()
      
      if not data.get('name'):
          return jsonify({'error': 'Department name is required'}), 400
      
      # Check if department already exists
      if Department.query.filter_by(name=data['name']).first():
          return jsonify({'error': 'Department already exists'}), 400
      
      department = Department(
          name=data['name'],
          description=data.get('description', '')
      )
      
      db.session.add(department)
      db.session.commit()
      
      return jsonify({
          'message': 'Department added successfully',
          'department': {
              'id': department.id,
              'name': department.name,
              'description': department.description
          }
      }), 201
      
  except Exception as e:
      db.session.rollback()
      return jsonify({'error': str(e)}), 500