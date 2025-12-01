from celery_worker import celery
from app.models import Appointment, Doctor, Patient, Treatment, db
from app.services.email_service import email_service
from datetime import datetime, timedelta
import logging
from sqlalchemy import func, and_
import csv
import io
from weasyprint import HTML
import jinja2

logger = logging.getLogger(__name__)

@celery.task(bind=True, name='report_tasks.generate_monthly_reports')
def generate_monthly_reports(self):
  """
  Generate and send monthly activity reports to all doctors
  """
  try:
      today = datetime.now()
      
      # Only run on the first day of the month
      if today.day != 1:
        logger.info("Skipping monthly reports - not the first day of month")
        return {'status': 'skipped', 'reason': 'Not first day of month'}
      
      last_month = today.replace(day=1) - timedelta(days=1)
      month_name = last_month.strftime('%B %Y')
      
      logger.info(f"Generating monthly reports for {month_name}")
      
      doctors = Doctor.query.filter_by(is_available=True).all()
      reports_generated = 0
      reports_failed = 0
      
      for doctor in doctors:
          try:
              # Generate report data
              report_data = generate_doctor_monthly_report(doctor.id, last_month)
              
              # Generate PDF
              pdf_content = generate_pdf_report(doctor, report_data, month_name)
              
              # Send email with PDF attachment
              success = email_service.send_monthly_report(
                doctor_email=doctor.user.email,
                doctor_name=doctor.user.username,
                report_data=report_data,
                pdf_attachment={
                  'filename': f"Monthly_Report_{month_name.replace(' ', '_')}.pdf",
                  'content': pdf_content
                }
              )
              
              if success:
                reports_generated += 1
                logger.info(f"Monthly report sent to Dr. {doctor.user.username}")
              else:
                reports_failed += 1
                logger.error(f"Failed to send report to Dr. {doctor.user.username}")
                  
          except Exception as e:
            reports_failed += 1
            logger.error(f"Error generating report for Dr. {doctor.user.username}: {str(e)}")
            continue
      
      return {
        'status': 'completed',
        'month': month_name,
        'reports_generated': reports_generated,
        'reports_failed': reports_failed,
        'total_doctors': len(doctors)
      }
      
  except Exception as e:
    logger.error(f"Error in generate_monthly_reports: {str(e)}")
    return {
      'status': 'failed',
      'error': str(e)
    }

def generate_doctor_monthly_report(doctor_id, month):
  """
  Generate monthly report data for a specific doctor
  """
  # Calculate date range for the month
  start_date = month.replace(day=1)
  end_date = start_date.replace(day=28) + timedelta(days=4)
  end_date = end_date.replace(day=1) - timedelta(days=1)
  
  # Basic appointment statistics
  appointments = Appointment.query.filter(
    and_(
      Appointment.doctor_id == doctor_id,
      Appointment.appointment_date >= start_date,
      Appointment.appointment_date <= end_date
    )
  ).all()
  
  total_appointments = len(appointments)
  completed_appointments = len([a for a in appointments if a.status == 'completed'])
  cancelled_appointments = len([a for a in appointments if a.status == 'cancelled'])
  
  # Patient statistics
  patient_ids = list(set([a.patient_id for a in appointments]))
  total_patients = len(patient_ids)
  
  # New patients (first appointment with this doctor)
  new_patients = 0
  for patient_id in patient_ids:
    first_appointment = Appointment.query.filter(
      Appointment.patient_id == patient_id,
      Appointment.doctor_id == doctor_id
    ).order_by(Appointment.appointment_date.asc()).first()
    
    if first_appointment and first_appointment.appointment_date >= start_date:
      new_patients += 1
  
  # Diagnosis statistics
  treatments = Treatment.query.join(Appointment).filter(
    and_(
      Appointment.doctor_id == doctor_id,
      Appointment.appointment_date >= start_date,
      Appointment.appointment_date <= end_date
    )
  ).all()
  
  diagnosis_counts = {}
  for treatment in treatments:
    if treatment.diagnosis:
      if treatment.diagnosis not in diagnosis_counts:
        diagnosis_counts[treatment.diagnosis] = 0
      diagnosis_counts[treatment.diagnosis] += 1
  
  top_diagnoses = sorted(
      [{'diagnosis': k, 'count': v} for k, v in diagnosis_counts.items()],
      key=lambda x: x['count'],
      reverse=True
  )[:5]  # Top 5 diagnoses
  
  cancellation_rate = (cancelled_appointments / total_appointments * 100) if total_appointments > 0 else 0
  
  return {
      'month': month.strftime('%B %Y'),
      'total_appointments': total_appointments,
      'completed_appointments': completed_appointments,
      'cancelled_appointments': cancelled_appointments,
      'total_patients': total_patients,
      'new_patients': new_patients,
      'cancellation_rate': round(cancellation_rate, 2),
      'top_diagnoses': top_diagnoses,
      'period': {
          'start': start_date.strftime('%Y-%m-%d'),
          'end': end_date.strftime('%Y-%m-%d')
      }
  }

def generate_pdf_report(doctor, report_data, month_name):
  """
  Generate PDF report using WeasyPrint
  """
  html_content = f"""
  <!DOCTYPE html>
  <html>
  <head>
      <meta charset="UTF-8">
      <style>
          body {{
              font-family: Arial, sans-serif;
              line-height: 1.6;
              color: #333;
              margin: 0;
              padding: 20px;
          }}
          .header {{
              text-align: center;
              border-bottom: 2px solid #007bff;
              padding-bottom: 20px;
              margin-bottom: 30px;
          }}
          .doctor-info {{
              background: #f8f9fa;
              padding: 15px;
              border-radius: 5px;
              margin-bottom: 20px;
          }}
          .stats-grid {{
              display: grid;
              grid-template-columns: repeat(2, 1fr);
              gap: 15px;
              margin: 20px 0;
          }}
          .stat-card {{
              background: white;
              border: 1px solid #dee2e6;
              border-radius: 5px;
              padding: 15px;
              text-align: center;
          }}
          .stat-value {{
              font-size: 24px;
              font-weight: bold;
              color: #007bff;
          }}
          .stat-label {{
              font-size: 14px;
              color: #6c757d;
          }}
          .diagnosis-list {{
              margin: 20px 0;
          }}
          .footer {{
              text-align: center;
              margin-top: 40px;
              padding-top: 20px;
              border-top: 1px solid #dee2e6;
              color: #6c757d;
              font-size: 12px;
          }}
          @page {{
              size: A4;
              margin: 2cm;
          }}
      </style>
  </head>
  <body>
      <div class="header">
        <h1>Monthly Activity Report</h1>
        <h2>{month_name}</h2>
        <h3>Dr. {doctor.user.username}</h3>
        <p>{doctor.specialization} - {doctor.department.name}</p>
      </div>
      
      <div class="doctor-info">
        <p><strong>Report Period:</strong> {report_data['period']['start']} to {report_data['period']['end']}</p>
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
      </div>
      
      <h3>Appointment Statistics</h3>
      <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-value">{report_data['total_appointments']}</div>
            <div class="stat-label">Total Appointments</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{report_data['completed_appointments']}</div>
            <div class="stat-label">Completed</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{report_data['cancelled_appointments']}</div>
            <div class="stat-label">Cancelled</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{report_data['cancellation_rate']}%</div>
            <div class="stat-label">Cancellation Rate</div>
          </div>
      </div>
      
      <h3>Patient Statistics</h3>
      <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-value">{report_data['total_patients']}</div>
            <div class="stat-label">Total Patients</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{report_data['new_patients']}</div>
            <div class="stat-label">New Patients</div>
          </div>
      </div>
      
      <div class="diagnosis-list">
        <h3>Top Diagnoses</h3>
        {"".join([f"<p>{diag['diagnosis']}: {diag['count']} cases</p>" for diag in report_data['top_diagnoses']])}
      </div>
      
      <div class="footer">
        <p>This report was automatically generated by Hospital Management System</p>
        <p>Confidential - For internal use only</p>
      </div>
  </body>
  </html>
  """
  
  return HTML(string=html_content).write_pdf()

@celery.task(bind=True, name='report_tasks.generate_custom_report')
def generate_custom_report(self, doctor_id, start_date, end_date, email):
  """
  Generate a custom report for a specific date range
  """
  try:
      doctor = Doctor.query.get(doctor_id)
      if not doctor:
        return {'status': 'failed', 'error': 'Doctor not found'}
      
      start_date = datetime.strptime(start_date, '%Y-%m-%d')
      end_date = datetime.strptime(end_date, '%Y-%m-%d')
      
      report_data = generate_doctor_monthly_report(doctor_id, start_date)
      pdf_content = generate_pdf_report(doctor, report_data, f"Custom Report {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
      
      success = email_service.send_monthly_report(
        doctor_email=email,
        doctor_name=doctor.user.username,
        report_data=report_data,
        pdf_attachment={
          'filename': f"Custom_Report_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.pdf",
          'content': pdf_content
        }
      )
      
      return {
        'status': 'success' if success else 'failed',
        'doctor_id': doctor_id,
        'period': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
      }
      
  except Exception as e:
      logger.error(f"Error in generate_custom_report: {str(e)}")
      return {
        'status': 'failed',
        'error': str(e)
      }