from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin
from datetime import datetime, timezone

# Initialize db object (will be bound to app in app.py)
db = SQLAlchemy()

# Association Table for User and Role (Many-to-Many)
# Kept to ensure Flask-Security auth continues to work
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer(), db.ForeignKey('users.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(50)) 
    is_blacklisted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Required by Flask-Security
    active = db.Column(db.Boolean(), default=True) 
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False) 
    
    # Relationships
    roles = db.relationship('Role', secondary=user_roles, backref=db.backref('users', lazy='dynamic'))
    bookings = db.relationship('Booking', backref='user', lazy=True)
    created_treks = db.relationship('Trek', backref='creator', lazy=True)


class TrekStaff(db.Model):
    __tablename__ = 'trek_staff'
    
    id = db.Column(db.Integer, primary_key=True)
    trek_id = db.Column(db.Integer, db.ForeignKey('treks.id'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships to easily access the related Trek and User objects
    trek = db.relationship('Trek', backref='assigned_staff_records')
    staff = db.relationship('User', backref='assigned_trek_records')


class Trek(db.Model):
    __tablename__ = 'treks'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255))
    description = db.Column(db.Text)
    difficulty = db.Column(db.String(50))
    duration_days = db.Column(db.Integer)
    total_seats = db.Column(db.Integer)
    available_slots = db.Column(db.Integer, default=0)
    price = db.Column(db.Float)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    status = db.Column(db.String(50), default='Pending')
    
    # Foreign Key for Admin who created the trek
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    bookings = db.relationship('Booking', backref='trek', lazy=True)


class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey('treks.id'), nullable=False)
    # Using .date() here since this specific column is db.Date, not db.DateTime
    booking_date = db.Column(db.Date, default=lambda: datetime.now(timezone.utc).date())
    status = db.Column(db.String(50), default='Booked')