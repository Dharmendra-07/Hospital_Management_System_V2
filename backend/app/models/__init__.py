from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
  __tablename__ = 'users'

  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(80), unique=True, nullable=False)
  email = db.Column(db.String(120), unique=True, nullable=False)
  password_hash = db.Column(db.String(255), nullable=False)
  role = db.Column(db.String(20), nullable=False)
  is_active = db.Column(db.Boolean, default=True)
  created_at = db.Column(db.DateTime, default=datetime.utcnow)

  # Relationships
  doctor_profile = db.relationship('Doctor', backref='user', uselist=False, cascade='all, delete-orphan')
  patient_profile = db.relationship('Patient', backref='user', uselist=False, cascade='all, delete-orphan')

  def set_password(self, password):
    self.password_hash = generate_password_hash(password)

  def check_password(self, password):
    return check_password_hash(self.password_hash, password)
  
class Department(db.Model):
  __tablename__ = 'departments'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100), nullable=False)
  description = db.Column(db.DateTime, default=datetime.utcnow)
  created_at = db.Column(db.DateTime, default=datetime.utcnow)

  # Relationships
  doctors = db.relationship('Doctor', backref='department', lazy=True)

class Doctor(db.Model):
  __tablename__ = 'doctors'

  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
  department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
  specialization = db.Column(db.String(100),nullable=False)
  qualification = db.Column(db.String(200))
  experience = db.Column(db.Integer) #years
  consultation_fee = db.Column(db.Float, default=0.0)
  bio = db.Column(db.Text)
  is_available = db.Column(db.Boolean, default=True)
  created_at = db.Column(db.DateTime, default=datetime.utcnow)

  # Relationships
  availabilities = db.relationship('DoctorAvailability',backref='doctor', lazy=True, cascade='all, delete-orphan')
  appointments = db.relationship('Appointment', backref='doctor', lazy=True)


class DoctorAvailability(db.Model):
  __tablename__ = 'doctor_availabilities'

  id = db.Column(db.Integer, primary_key=True)
  doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
  date = db.Column(db.Date, nullable=False)
  start_time = db.Column(db.Time, nullable=False)
  end_time = db.Column(db.Time, nullable=False)
  is_available = db.Column(db.Boolean, default=True)
  max_patients = db.Column(db.Integer, default=10)

  __table__args__ = (db.UniqueConstraint('doctor_id', 'date', 'start_time', name='unique_doctor_slot'))

class Patient(db.Model):
  __tablename__ = 'patients'

  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
  first_name = db.Column(db.String(50), nullable=False)
  last_name = db.Column(db.String(50), nullable=False)
  date_of_birth = db.Column(db.Date, nullable=False)
  gender = db.Column(db.String(10), nullable=False)
  phone = db.Column(db.String(15))
  address = db.Column(db.Text)
  emergency_contact = db.Column(db.String(15))
  blood_group = db.Column(db.String(5))
  created_at = db.Column(db.DateTime, default=datetime.utcnow)

  # Relationships
  appointments = db.relationship('Appointment', backref='patient', lazy=True)

class Appointment(db.Model):
  __tablename__ = 'appointments'

  id = db.Column(db.Integer, primary_key=True)
  patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
  doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
  appointment_date = db.Column(db.Date, nullable=False)
  appointment_date = db.Column(db.Time, nullable=False)
  status = db.Column(db.String(20), default='scheduled') # scheduled, completed,, cancelled, np_show
  reason = db.Column(db.Text)
  created_at = db.Column(db.DateTime, default=datetime.utcnow)
  updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


  # Relationships
  treatment = db.relationship('Treatment', backref='appointment', uselist=False, cascade='all, delete-orphan')

  __table_args__ = (db.UniqueConstraint('doctor_id', 'appointment_date', 'appointment_time', cascade='all, delete-orphan'))


class Treatment(db.Model):
  __tablename__ = 'treatments'

  id = db.Column(db.Integer, primary_key=True)
  appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=False)
  diagnosis = db.Column(db.Text)
  symptoms = db.Column(db.Text)
  prescription= db.Column(db.Text)
  notes = db.Column(db.Text)
  follow_up_date = db.Column(db.Date)
  created_at = db.Column(db.DateTime, default=datetime.utcnow)