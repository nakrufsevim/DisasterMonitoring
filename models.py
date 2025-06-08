from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
from werkzeug.security import check_password_hash

# Initialize db, Marshmallow, and Bcrypt
db = SQLAlchemy()  # This is the database object
ma = Marshmallow()  # Marshmallow for object serialization
bcrypt = Bcrypt()   # Bcrypt for password hashing


# Disaster model for the disaster monitoring system
class Disaster(db.Model):
    disaster_id = db.Column(db.Integer, primary_key=True)
    disaster_type = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    severity = db.Column(db.Float, nullable=False)
    time_occurred = db.Column(db.String(50), nullable=False)

    def __init__(self, disaster_type, location, severity, time_occurred):
        self.disaster_type = disaster_type
        self.location = location
        self.severity = severity
        self.time_occurred = time_occurred

class DisasterSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Disaster
        load_instance = True  # To deserialize into instances of the model

# Alert model for disaster alerts
class Alert(db.Model):
    alert_id = db.Column(db.Integer, primary_key=True)
    disaster_id = db.Column(db.Integer, db.ForeignKey('disaster.disaster_id'), nullable=False)
    alert_type = db.Column(db.String(100), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    time_sent = db.Column(db.String(50), nullable=False)

    disaster = db.relationship('Disaster', backref=db.backref('alerts', lazy=True))

    def __init__(self, disaster_id, alert_type, message, time_sent):
        self.disaster_id = disaster_id
        self.alert_type = alert_type
        self.message = message
        self.time_sent = time_sent

class AlertSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Alert
        load_instance = True

# User model for authentication (with hashed password)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    def __init__(self, username, password):
        self.username = username
        self.password = password

    # Flask-Login requires these methods
    def get_id(self):
        return str(self.id)

    def is_authenticated(self):
        return True  # All users are considered authenticated once logged in

    def is_active(self):
        return self.is_active  # Check if the user is active

    def is_anonymous(self):
        return False  # False because we want to avoid anonymous users

    def check_password(self, password):
        return check_password_hash(self.password, password)


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
