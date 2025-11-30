class AppointmentHistory(db.Model):
    __tablename__ = 'appointment_history'
    
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=False)
    changed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # User who made the change
    change_type = db.Column(db.String(20), nullable=False)  # created, updated, cancelled, status_changed
    previous_data = db.Column(db.Text)  # JSON string of previous data
    new_data = db.Column(db.Text)  # JSON string of new data
    change_reason = db.Column(db.Text)
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    appointment = db.relationship('Appointment', backref=db.backref('history', lazy=True))
    user = db.relationship('User', foreign_keys=[changed_by])

class ConflictLog(db.Model):
    __tablename__ = 'conflict_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    conflict_type = db.Column(db.String(50), nullable=False)  # double_booking, time_conflict, etc.
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    attempted_date = db.Column(db.Date, nullable=False)
    attempted_time = db.Column(db.Time, nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'))
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'))
    resolved = db.Column(db.Boolean, default=False)
    resolved_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id])
    doctor = db.relationship('Doctor', foreign_keys=[doctor_id])
    patient = db.relationship('Patient', foreign_keys=[patient_id])