import jwt
from datetime import datetime, timedelta
from flask import current_app
from app.models import User

def generate_token(user_id):
  payload = {
      'user_id': user_id,
      'exp': datetime.utcnow() + timedelta(days=1),
      'iat': datetime.utcnow()
  }
  return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

def verify_token(token):
  try:
      payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
      return User.query.get(payload['user_id'])
  except jwt.ExpiredSignatureError:
      return None
  except jwt.InvalidTokenError:
      return None

def token_required(f):
  from flask import request, jsonify
  from functools import wraps
  
  @wraps(f)
  def decorated(*args, **kwargs):
      token = None
      
      # Get token from header
      if 'Authorization' in request.headers:
          auth_header = request.headers['Authorization']
          try:
              token = auth_header.split(' ')[1]  # Bearer <token>
          except IndexError:
              return jsonify({'error': 'Invalid authorization header'}), 401
      
      if not token:
          return jsonify({'error': 'Token is missing'}), 401
      
      user = verify_token(token)
      if not user:
          return jsonify({'error': 'Invalid or expired token'}), 401
      
      return f(user, *args, **kwargs)
  
  return decorated