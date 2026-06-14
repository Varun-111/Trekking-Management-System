from app import app, db
from models import Role, User
from flask_bcrypt import Bcrypt
import uuid
from datetime import datetime, timezone

bcrypt = Bcrypt(app)

def setup():
    with app.app_context():
        # 1. Create all tables programmatically
        db.create_all()
        print('Database tables created successfully')

        # 2. Create Roles for Flask-Security 
        roles = ['Admin', 'Trek Staff', 'Trekker']
        for role_name in roles:
            if not Role.query.filter_by(name=role_name).first():
                db.session.add(Role(name=role_name))
        
        db.session.commit()
        print("Roles initialized.")

        # 3. Pre-create the Admin User matching the new ER Diagram
        admin_role = Role.query.filter_by(name='Admin').first()

        if not User.query.filter_by(email='admin@trek.com').first():
            hashed_pw = bcrypt.generate_password_hash('admin123').decode('utf-8')
            
            admin_user = User(
                username='Super-Admin',
                email='admintrek@gmail.com',
                password_hash=hashed_pw,
                phone='1234567890',
                role='Admin',               
                is_blacklisted=False,       
                created_at=datetime.now(timezone.utc), # Modern timezone-aware datetime
                active=True,                
                fs_uniquifier=str(uuid.uuid4()) 
            )
            # Assign the Flask-Security role
            admin_user.roles.append(admin_role)
            
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user successfully pre-created!")
        else:
            print("Admin user already exists in the database.")

if __name__ == '__main__':
    setup()