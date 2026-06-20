from app import app, db
from models import User
from werkzeug.security import generate_password_hash
from datetime import datetime, timezone
import os

def setup():
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Tables created successfully.")

        # Seed admin only if not already present
        existing_admin = User.query.filter_by(role='Admin').first()

        if not existing_admin:
            admin_password = generate_password_hash(os.getenv("ADMIN_PASSWORD"))

            admin_user = User(
                username=os.getenv("ADMIN_USERNAME"),
                email=os.getenv("ADMIN_EMAIL"),
                password_hash=admin_password,
                phone=os.getenv("ADMIN_PHONE"),
                role='Admin',
                is_blacklisted=False,
                is_approved=True,
                created_at=datetime.now(timezone.utc)
            )

            db.session.add(admin_user)
            db.session.commit()
            
            print("Admin user created successfully.")
        else:
            print("Admin already exists. Skipping.")

if __name__ == '__main__':
    setup()