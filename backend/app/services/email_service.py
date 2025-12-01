import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from email.mime.application import MimeApplication
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class EmailService:
  def __init__(self):
    self.smtp_server = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    self.smtp_port = int(os.environ.get('MAIL_PORT', 587))
    self.smtp_username = os.environ.get('MAIL_USERNAME')
    self.smtp_password = os.environ.get('MAIL_PASSWORD')
    self.use_tls = True
  
  def send_email(self, to_email, subject, html_content, text_content=None, attachments=None):
      """
      Send email with HTML content and optional attachments
      """
      try:
          if not self.smtp_username or not self.smtp_password:
            logger.warning("Email credentials not configured. Skipping email send.")
            return False
          
          # Create message
          msg = MimeMultipart('alternative')
          msg['Subject'] = subject
          msg['From'] = self.smtp_username
          msg['To'] = to_email
          
          # Add text content
          if text_content:
            text_part = MimeText(text_content, 'plain')
            msg.attach(text_part)
          
          # Add HTML content
          html_part = MimeText(html_content, 'html')
          msg.attach(html_part)
          
          # Add attachments
          if attachments:
            for attachment in attachments:
              if isinstance(attachment, dict):
                part = MimeApplication(
                    attachment['content'],
                    Name=attachment['filename']
                )
                part['Content-Disposition'] = f'attachment; filename="{attachment["filename"]}"'
                msg.attach(part)
          
          # Send email
          with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            if self.use_tls:
              server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
          
          logger.info(f"Email sent successfully to {to_email}")
          return True
          
      except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return False
  
  def send_appointment_reminder(self, patient_email, patient_name, appointment_date, appointment_time, doctor_name, location="Main Hospital"):
      """
      Send appointment reminder email
      """
      subject = f"Appointment Reminder - {appointment_date}"
      
      html_content = f"""
      <!DOCTYPE html>
      <html>
      <head>
          <style>
              body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
              .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
              .header {{ background: #007bff; color: white; padding: 20px; text-align: center; }}
              .content {{ padding: 20px; background: #f9f9f9; }}
              .appointment-details {{ background: white; padding: 15px; border-radius: 5px; border-left: 4px solid #007bff; }}
              .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
          </style>
      </head>
      <body>
          <div class="container">
              <div class="header">
                  <h1>🏥 Hospital Management System</h1>
                  <h2>Appointment Reminder</h2>
              </div>
              <div class="content">
                  <p>Dear <strong>{patient_name}</strong>,</p>
                  <p>This is a friendly reminder about your upcoming appointment:</p>
                  
                  <div class="appointment-details">
                    <h3>Appointment Details</h3>
                    <p><strong>Date:</strong> {appointment_date}</p>
                    <p><strong>Time:</strong> {appointment_time}</p>
                    <p><strong>Doctor:</strong> Dr. {doctor_name}</p>
                    <p><strong>Location:</strong> {location}</p>
                  </div>
                  
                  <p><strong>Important Notes:</strong></p>
                  <ul>
                    <li>Please arrive 15 minutes before your scheduled time</li>
                    <li>Bring your ID and insurance card</li>
                    <li>Cancel at least 2 hours in advance if you cannot make it</li>
                  </ul>
                  
                  <p>If you have any questions, please contact our front desk.</p>
                  
                  <p>Best regards,<br>Hospital Management Team</p>
              </div>
              <div class="footer">
                <p>This is an automated message. Please do not reply to this email.</p>
              </div>
          </div>
      </body>
      </html>
      """
      
      text_content = f"""
      Appointment Reminder
      
      Dear {patient_name},
      
      This is a reminder about your upcoming appointment:
      
      Date: {appointment_date}
      Time: {appointment_time}
      Doctor: Dr. {doctor_name}
      Location: {location}
      
      Please arrive 15 minutes early and bring your ID and insurance card.
      
      Best regards,
      Hospital Management Team
      """
      
      return self.send_email(patient_email, subject, html_content, text_content)
  
  def send_monthly_report(self, doctor_email, doctor_name, report_data, pdf_attachment=None):
      """
      Send monthly activity report to doctor
      """
      subject = f"Monthly Activity Report - {report_data['month']}"
      
      html_content = f"""
      <!DOCTYPE html>
      <html>
      <head>
          <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #28a745; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; background: #f9f9f9; }}
            .stats {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 20px 0; }}
            .stat-card {{ background: white; padding: 15px; border-radius: 5px; text-align: center; }}
            .stat-value {{ font-size: 24px; font-weight: bold; color: #007bff; }}
            .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
          </style>
      </head>
      <body>
          <div class="container">
              <div class="header">
                  <h1>🏥 Monthly Activity Report</h1>
                  <h2>{report_data['month']}</h2>
              </div>
              <div class="content">
                  <p>Dear Dr. <strong>{doctor_name}</strong>,</p>
                  <p>Here is your monthly activity summary for {report_data['month']}:</p>
                  
                  <div class="stats">
                      <div class="stat-card">
                          <div class="stat-value">{report_data['total_appointments']}</div>
                          <div>Total Appointments</div>
                      </div>
                      <div class="stat-card">
                          <div class="stat-value">{report_data['completed_appointments']}</div>
                          <div>Completed</div>
                      </div>
                      <div class="stat-card">
                          <div class="stat-value">{report_data['new_patients']}</div>
                          <div>New Patients</div>
                      </div>
                      <div class="stat-card">
                          <div class="stat-value">{report_data['cancellation_rate']}%</div>
                          <div>Cancellation Rate</div>
                      </div>
                  </div>
                  
                  <h3>Top Diagnoses</h3>
                  <ul>
                      {"".join([f"<li>{diag['diagnosis']}: {diag['count']} cases</li>" for diag in report_data.get('top_diagnoses', [])])}
                  </ul>
                  
                  <p>A detailed PDF report is attached to this email.</p>
                  
                  <p>Best regards,<br>Hospital Management System</p>
              </div>
              <div class="footer">
                  <p>This report is generated automatically on a monthly basis.</p>
              </div>
          </div>
      </body>
      </html>
      """
      
      attachments = []
      if pdf_attachment:
          attachments.append(pdf_attachment)
      
      return self.send_email(doctor_email, subject, html_content, attachments=attachments)

email_service = EmailService()