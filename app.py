# app.py
from flask import Flask, jsonify, request
from flask_restplus import Api, Resource, fields
from models import Disaster, Alert

# Initialize Flask app and Flask-RESTPlus API
app = Flask(__name__)
api = Api(app, version='1.0', title='Geographic Disaster Monitoring API',
          description='An API for monitoring and alerting natural disasters')

# Define Disaster and Alert models (for API documentation)
disaster_model = api.model('Disaster', {
    'disaster_id': fields.Integer(required=True, description='The disaster ID'),
    'disaster_type': fields.String(required=True, description='Type of disaster'),
    'location': fields.String(required=True, description='Location of disaster'),
    'severity': fields.Float(required=True, description='Severity of disaster'),
    'time_occurred': fields.String(required=True, description='Time disaster occurred')
})

alert_model = api.model('Alert', {
    'alert_id': fields.Integer(required=True, description='The alert ID'),
    'disaster_id': fields.Integer(required=True, description='Related disaster ID'),
    'alert_type': fields.String(required=True, description='Type of alert'),
    'message': fields.String(required=True, description='Alert message'),
    'time_sent': fields.String(required=True, description='Time alert was sent')
})

# Store disasters and alerts in-memory (just for this example)
disasters = []
alerts = []

# Disaster API resource
@api.route('/disasters')
class DisasterResource(Resource):
    def get(self):
        """Retrieve all disasters"""
        return jsonify(disasters)
    
    @api.expect(disaster_model)
    def post(self):
        """Create a new disaster"""
        disaster = api.payload
        disasters.append(disaster)
        return disaster, 201

# Alert API resource
@api.route('/alerts')
class AlertResource(Resource):
    def get(self):
        """Retrieve all alerts"""
        return jsonify(alerts)
    
    @api.expect(alert_model)
    def post(self):
        """Create a new alert"""
        alert = api.payload
        alerts.append(alert)
        return alert, 201

# Main entry point
if __name__ == '__main__':
    app.run(debug=True)
