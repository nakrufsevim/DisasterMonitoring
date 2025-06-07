# test_app.py

import unittest
from app import app, db
from models import Disaster, Alert

class DisasterMonitoringTestCase(unittest.TestCase):
    def setUp(self):
        """Set up the testing environment"""
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # In-memory database for testing
        app.config['TESTING'] = True
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        """Clean up the database after each test"""
        db.session.remove()
        db.drop_all()

    def test_create_disaster(self):
        response = self.app.post('/disasters', json={
            "disaster_type": "Earthquake",
            "location": "California",
            "severity": 8.5,
            "time_occurred": "2025-06-07T12:00:00"
        })
        self.assertEqual(response.status_code, 201)

    def test_get_disasters(self):
        response = self.app.get('/disasters')
        self.assertEqual(response.status_code, 200)

    def test_create_alert(self):
        response = self.app.post('/alerts', json={
            "disaster_id": 1,
            "alert_type": "Evacuation",
            "message": "Evacuate immediately",
            "time_sent": "2025-06-07T12:05:00"
        })
        self.assertEqual(response.status_code, 201)

    def test_get_alerts(self):
        response = self.app.get('/alerts')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
