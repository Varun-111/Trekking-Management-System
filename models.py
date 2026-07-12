from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(50), nullable=False)
    is_blacklisted = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=False) 
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    bookings = db.relationship('Booking', backref='user', lazy=True)
    created_treks = db.relationship('Trek', backref='creator', lazy=True) 


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
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    bookings = db.relationship('Booking', backref='trek', lazy=True)


class TrekStaff(db.Model):
    __tablename__ = 'trek_staff'

    id = db.Column(db.Integer, primary_key=True)
    trek_id = db.Column(db.Integer, db.ForeignKey('treks.id'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    trek = db.relationship('Trek', backref='assigned_staff_records')
    staff = db.relationship('User', backref='assigned_trek_records')


class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey('treks.id'), nullable=False)
    booking_date = db.Column(db.Date, default=lambda: datetime.now(timezone.utc).date())
    status = db.Column(db.String(50), default='Booked')