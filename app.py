from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restx import Api, Resource, fields
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Disaster, Alert, DisasterSchema, AlertSchema
from flask_debugtoolbar import DebugToolbarExtension

# Initialize Flask app
app = Flask(__name__)

# Configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///disasters.db'  # SQLite for dev, PostgreSQL for production
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'os.urandom(24)'  # Replace with a secure secret key

# Debug Toolbar settings (only in development mode)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False  # Disable automatic redirects
app.config['DEBUG_TB_ENABLED'] = True  # Enable Debug Toolbar

# Initialize SQLAlchemy, Marshmallow, Flask-Migrate, Flask-Login, and Debug Toolbar
db.init_app(app)
ma = Marshmallow(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_page'  # Set login route for Flask-Login

# Initialize Debug Toolbar
toolbar = DebugToolbarExtension(app)

# User Loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Serve the login page
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if user exists
        user = User.query.filter_by(username=username).first()

        # If user exists and password matches the hashed password
        if user:
            if check_password_hash(user.password, password):
                login_user(user)  # Log in the user

                # Check for the 'next' parameter and redirect accordingly
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                else:
                    return redirect(url_for('dashboard_page'))  # Default to dashboard if no 'next' parameter
            else:
                return jsonify({"message": "Invalid credentials!"}), 401
        else:
            return jsonify({"message": "User not found!"}), 404

    return render_template('login.html')

# Serve the registration page
@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return jsonify({"message": "Username already exists!"}), 400
        
        # Create new user and store the hashed password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({"message": "User created successfully!"}), 201
    return render_template('register.html')

# Serve the dashboard page after login
@app.route('/dashboard')
@login_required
def dashboard_page():
    disasters = Disaster.query.all()
    alerts = Alert.query.all()
    return render_template('dashboard.html', disasters=disasters, alerts=alerts)

# Add disaster form submission
@app.route('/add_disaster', methods=['POST'])
@login_required
def add_disaster():
    disaster_type = request.form['disaster_type']
    location = request.form['location']
    severity = request.form['severity']
    time_occurred = request.form['time_occurred']

    disaster = Disaster(disaster_type=disaster_type, location=location, severity=severity, time_occurred=time_occurred)
    db.session.add(disaster)
    db.session.commit()

    return redirect(url_for('dashboard_page'))

# Add alert form submission
@app.route('/add_alert', methods=['POST'])
@login_required
def add_alert():
    disaster_id = request.form['disaster_id']
    alert_type = request.form['alert_type']
    message = request.form['message']
    time_sent = request.form['time_sent']

    new_alert = Alert(
        disaster_id=disaster_id,
        alert_type=alert_type,
        message=message,
        time_sent=time_sent
    )
    db.session.add(new_alert)
    db.session.commit()

    return redirect(url_for('dashboard_page'))

# Logout function
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login_page'))  # Redirect to login page after logout

# Profile page for logged-in users
@app.route('/profile')
@login_required
def profile():
    return "You are logged in!"

# Initialize Flask-RESTX API
api = Api(app, version='1.0', title='Geographic Disaster Monitoring API',
          description='An API for monitoring and alerting natural disasters')

# Disaster and Alert API models for Swagger documentation
disaster_model = api.model('Disaster', {
    'disaster_type': fields.String(required=True, description='Type of disaster'),
    'location': fields.String(required=True, description='Location of disaster'),
    'severity': fields.Float(required=True, description='Severity of disaster'),
    'time_occurred': fields.String(required=True, description='Time disaster occurred')
})

alert_model = api.model('Alert', {
    'disaster_id': fields.Integer(required=True, description='Disaster ID'),
    'alert_type': fields.String(required=True, description='Alert type (e.g., Warning, Evacuation)'),
    'message': fields.String(required=True, description='Alert message'),
    'time_sent': fields.String(required=True, description='Time the alert was sent')
})

# Disaster Resource - CRUD operations for disasters
@api.route('/disasters')
class DisasterResource(Resource):
    def get(self):
        disasters = Disaster.query.all()
        disaster_schema = DisasterSchema(many=True)
        return disaster_schema.dump(disasters), 200

    @api.expect(disaster_model)
    def post(self):
        disaster_data = request.get_json()
        try:
            disaster = Disaster(
                disaster_type=disaster_data['disaster_type'],
                location=disaster_data['location'],
                severity=disaster_data['severity'],
                time_occurred=disaster_data['time_occurred']
            )
            db.session.add(disaster)
            db.session.commit()
            disaster_schema = DisasterSchema()
            return disaster_schema.dump(disaster), 201
        except Exception as e:
            return {"message": str(e)}, 500

# Alert Resource - CRUD operations for alerts
@api.route('/alerts')
class AlertResource(Resource):
    def get(self):
        alerts = Alert.query.all()
        alert_schema = AlertSchema(many=True)
        return alert_schema.dump(alerts), 200

    @api.expect(alert_model)
    def post(self):
        alert_data = request.get_json()
        try:
            alert = Alert(
                disaster_id=alert_data['disaster_id'],
                alert_type=alert_data['alert_type'],
                message=alert_data['message'],
                time_sent=alert_data['time_sent']
            )
            db.session.add(alert)
            db.session.commit()
            alert_schema = AlertSchema()
            return alert_schema.dump(alert), 201
        except Exception as e:
            return {"message": str(e)}, 500

# Main entry point
if __name__ == '__main__':
    app.run(debug=True)  # This will allow the Flask Debug Toolbar to appear in the browser
