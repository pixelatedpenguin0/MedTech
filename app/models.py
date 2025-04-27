from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    medications = db.relationship('Medication', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Medication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.String(50))
    frequency = db.Column(db.String(50))
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reminders = db.relationship('Reminder', backref='medication', lazy='dynamic')
    notes = db.Column(db.Text)
    total_doses = db.Column(db.Integer, default=0)
    taken_doses = db.Column(db.Integer, default=0)
    missed_doses = db.Column(db.Integer, default=0)
    remaining_doses = db.Column(db.Integer, default=0)  # Track remaining doses

class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    medication_id = db.Column(db.Integer, db.ForeignKey('medication.id'), nullable=False)
    time = db.Column(db.Time, nullable=False)
    days = db.Column(db.String(50))  # Comma-separated days of week
    is_active = db.Column(db.Boolean, default=True)

class Adherence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    medication_id = db.Column(db.Integer, db.ForeignKey('medication.id'), nullable=False)
    taken_time = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20))  # 'taken', 'missed', 'skipped'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id)) 