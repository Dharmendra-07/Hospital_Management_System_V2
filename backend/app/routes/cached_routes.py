from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.services.cache_service import cache_service, cached, invalidate_cache
from app.utils.cache_keys import CacheKeys
from app.models.cached_models import CachedDoctor, CachedPatient, CachedStats
from app.utils.decorators import admin_required, doctor_required, patient_required
import time

cached_bp = Blueprint('cached', __name__)

@cached_bp.route('/doctors', methods=['GET'])
@login_required
def get_doctors_cached():
  """
  Get doctors with caching
  """
  try:
      start_time = time.time()
      
      search = request.args.get('search', '')
      department_id = request.args.get('department_id', type=int)
      
      # Use cached model method
      doctors = CachedDoctor.get_available_doctors(search=search, department_id=department_id)
      
      result = []
      for doctor in doctors:
          result.append({
              'id': doctor.id,
              'name': doctor.user.username,
              'email': doctor.user.email,
              'specialization': doctor.specialization,
              'department': doctor.department.name,
              'qualification': doctor.qualification,
              'experience': doctor.experience,
              'consultation_fee': doctor.consultation_fee,
              'is_available': doctor.is_available
          })
      
      response_time = time.time() - start_time
      return jsonify({
          'doctors': result,
          'cached': True,
          'response_time': f"{response_time:.3f}s"
      }), 200
      
  except Exception as e:
      return jsonify({'error': str(e)}), 500

@cached_bp.route('/doctors/<int:doctor_id>', methods=['GET'])
@login_required
def get_doctor_detail_cached(doctor_id):
  """
  Get doctor details with caching
  """
  try:
      start_time = time.time()
      
      doctor = CachedDoctor.get_doctor_with_details(doctor_id)
      
      if not doctor:
          return jsonify({'error': 'Doctor not found'}), 404
      
      # Get availability for next 7 days
      start_date = datetime.now().date()
      end_date = start_date + timedelta(days=7)
      
      availability = CachedDoctor.get_doctor_availability(
          doctor_id, 
          start_date, 
          end_date
      )
      
      result = {
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
          'availability': availability,
          'cached': True,
          'response_time': f"{(time.time() - start_time):.3f}s"
      }
      
      return jsonify(result), 200
      
  except Exception as e:
      return jsonify({'error': str(e)}), 500

@cached_bp.route('/departments', methods=['GET'])
@login_required
def get_departments_cached():
  """
  Get all departments with caching
  """
  try:
      start_time = time.time()
      
      departments = CachedDoctor.get_all_departments()
      
      result = []
      for dept in departments:
          result.append({
              'id': dept.id,
              'name': dept.name,
              'description': dept.description
          })
      
      response_time = time.time() - start_time
      return jsonify({
          'departments': result,
          'cached': True,
          'response_time': f"{response_time:.3f}s"
      }), 200
      
  except Exception as e:
      return jsonify({'error': str(e)}), 500

@cached_bp.route('/patient/appointments', methods=['GET'])
@login_required
@patient_required
def get_patient_appointments_cached():
  """
  Get patient appointments with caching
  """
  try:
      start_time = time.time()
      
      patient_id = current_user.patient_profile.id
      status = request.args.get('status', '')
      
      appointments = CachedPatient.get_patient_appointments(patient_id, status)
      
      response_time = time.time() - start_time
      return jsonify({
          'appointments': appointments,
          'cached': True,
          'response_time': f"{response_time:.3f}s"
      }), 200
      
  except Exception as e:
      return jsonify({'error': str(e)}), 500

@cached_bp.route('/admin/dashboard/stats', methods=['GET'])
@login_required
@admin_required
def get_admin_dashboard_stats_cached():
  """
  Get admin dashboard stats with caching
  """
  try:
      start_time = time.time()
      
      stats = CachedStats.get_admin_dashboard_stats()
      
      response_time = time.time() - start_time
      return jsonify({
          'stats': stats,
          'cached': True,
          'response_time': f"{response_time:.3f}s"
      }), 200
      
  except Exception as e:
      return jsonify({'error': str(e)}), 500

@cached_bp.route('/doctor/dashboard/stats', methods=['GET'])
@login_required
@doctor_required
def get_doctor_dashboard_stats_cached():
  """
  Get doctor dashboard stats with caching
  """
  try:
      start_time = time.time()
      
      doctor_id = current_user.doctor_profile.id
      stats = CachedStats.get_doctor_dashboard_stats(doctor_id)
      
      response_time = time.time() - start_time
      return jsonify({
          'stats': stats,
          'cached': True,
          'response_time': f"{response_time:.3f}s"
      }), 200
      
  except Exception as e:
      return jsonify({'error': str(e)}), 500

@cached_bp.route('/cache/clear', methods=['POST'])
@login_required
@admin_required
def clear_cache():
  """
  Clear specific cache patterns (Admin only)
  """
  try:
      data = request.get_json()
      pattern = data.get('pattern', '*')
      
      if pattern == '*':
          # Clear all cache
          cache_service.delete_pattern('*')
      else:
          # Clear specific pattern
          cache_service.delete_pattern(pattern)
      
      return jsonify({
          'message': f'Cache cleared for pattern: {pattern}',
          'success': True
      }), 200
      
  except Exception as e:
      return jsonify({'error': str(e)}), 500

@cached_bp.route('/cache/stats', methods=['GET'])
@login_required
@admin_required
def get_cache_stats():
  """
  Get Redis cache statistics (Admin only)
  """
  try:
      stats = cache_service.get_cache_stats()
      
      return jsonify({
          'cache_stats': stats,
          'redis_connected': cache_service.is_connected()
      }), 200
      
  except Exception as e:
      return jsonify({'error': str(e)}), 500

@cached_bp.route('/cache/health', methods=['GET'])
def cache_health():
  """
  Cache health check endpoint
  """
  try:
      is_healthy = cache_service.is_connected()
      stats = cache_service.get_cache_stats() if is_healthy else {}
      
      return jsonify({
          'status': 'healthy' if is_healthy else 'unhealthy',
          'redis_connected': is_healthy,
          'stats': stats
      }), 200
      
  except Exception as e:
      return jsonify({'error': str(e)}), 500