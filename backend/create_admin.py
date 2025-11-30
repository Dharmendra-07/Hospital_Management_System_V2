from app import create_app, db
from app.models import User, Department

def create_default_data():
  app = create_app()

  with app.app_context():
    # Create default department
    if not Department.query.first():
      departments = [
        Department(name='Cardiology', description='Heart and cardiovascular system'),
        Department(name='Neurology', description='Brain and nervous system'),
        Department(name='Pediatrics', description='Child healthcare'),
        Department(name='Orthopedics', description='Bones and muscles'),
        Department(name='dermatology', description='Skin diseases and conditions'),
      ]
      db.session.bulk_save_objects(departments)
      db.session.commit()
      print('Default departments created')
    
    # Create admin user
    if not User.query.filter_by(role='admin').first():
      admin = User(
        username='admin',
        email='admin@hospital.com',
        role='admin'
      )
      admin.set_password('admin123')
      db.session.add(admin)
      db.session.commit()
      print('Admin user created: admin/admin123')
    print('Default data setup completed!')
  
if __name__ == '__main__':
  create_default_data()