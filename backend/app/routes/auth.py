from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, Doctor, Patient, db
from app.utils import generate_token, verify_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
  try:
      data = request.get_json()
      
      # Validate required fields
      required_fields = ['username', 'email', 'password', 'first_name', 'last_name', 'date_of_birth', 'gender']
      for field in required_fields:
          if not data.get(field):
              return jsonify({'error': f'{field} is required'}), 400
      
      # Check if user already exists
      if User.query.filter_by(username=data['username']).first():
          return jsonify({'error': 'Username already exists'}), 400
      
      if User.query.filter_by(email=data['email']).first():
          return jsonify({'error': 'Email already exists'}), 400
      
      # Create user
      user = User(
          username=data['username'],
          email=data['email'],
          role='patient'
      )
      user.set_password(data['password'])
      
      db.session.add(user)
      db.session.flush()  # Get user ID without committing
      
      # Create patient profile
      patient = Patient(
          user_id=user.id,
          first_name=data['first_name'],
          last_name=data['last_name'],
          date_of_birth=data['date_of_birth'],
          gender=data['gender'],
          phone=data.get('phone', ''),
          address=data.get('address', ''),
          emergency_contact=data.get('emergency_contact', ''),
          blood_group=data.get('blood_group', '')
      )
      
      db.session.add(patient)
      db.session.commit()
      
      # Generate JWT token
      token = generate_token(user.id)
      
      return jsonify({
          'message': 'Registration successful',
          'token': token,
          'user': {
              'id': user.id,
              'username': user.username,
              'email': user.email,
              'role': user.role,
              'profile': {
                  'first_name': patient.first_name,
                  'last_name': patient.last_name
              }
          }
      }), 201
      
  except Exception as e:
      db.session.rollback()
      return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
  try:
      data = request.get_json()
      
      if not data.get('username') or not data.get('password'):
          return jsonify({'error': 'Username and password are required'}), 400
      
      user = User.query.filter_by(username=data['username']).first()
      
      if not user or not user.check_password(data['password']):
          return jsonify({'error': 'Invalid credentials'}), 401
      
      if not user.is_active:
          return jsonify({'error': 'Account is deactivated'}), 401
      
      login_user(user)
      
      # Get profile based on role
      profile = {}
      if user.role == 'doctor' and user.doctor_profile:
          profile = {
              'specialization': user.doctor_profile.specialization,
              'department': user.doctor_profile.department.name if user.doctor_profile.department else None
          }
      elif user.role == 'patient' and user.patient_profile:
          profile = {
              'first_name': user.patient_profile.first_name,
              'last_name': user.patient_profile.last_name
          }
      
      token = generate_token(user.id)
      
      return jsonify({
          'message': 'Login successful',
          'token': token,
          'user': {
              'id': user.id,
              'username': user.username,
              'email': user.email,
              'role': user.role,
              'profile': profile
          }
      }), 200
      
  except Exception as e:
      return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
  logout_user()
  return jsonify({'message': 'Logout successful'}), 200

@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
  try:
      profile = {}
      if current_user.role == 'doctor' and current_user.doctor_profile:
          doctor = current_user.doctor_profile
          profile = {
              'specialization': doctor.specialization,
              'qualification': doctor.qualification,
              'department': doctor.department.name if doctor.department else None,
              'consultation_fee': doctor.consultation_fee,
              'bio': doctor.bio
          }
      elif current_user.role == 'patient' and current_user.patient_profile:
          patient = current_user.patient_profile
          profile = {
              'first_name': patient.first_name,
              'last_name': patient.last_name,
              'date_of_birth': patient.date_of_birth.isoformat() if patient.date_of_birth else None,
              'gender': patient.gender,
              'phone': patient.phone,
              'blood_group': patient.blood_group
          }
      
      return jsonify({
          'user': {
              'id': current_user.id,
              'username': current_user.username,
              'email': current_user.email,
              'role': current_user.role,
              'profile': profile
          }
      }), 200
      
  except Exception as e:
      return jsonify({'error': str(e)}), 500

      