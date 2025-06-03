# models.py
class Disaster:
    def __init__(self, disaster_id, disaster_type, location, severity, time_occurred):
        self.disaster_id = disaster_id
        self.disaster_type = disaster_type
        self.location = location
        self.severity = severity
        self.time_occurred = time_occurred

    def get_disaster_details(self):
        return {
            'disaster_id': self.disaster_id,
            'disaster_type': self.disaster_type,
            'location': self.location,
            'severity': self.severity,
            'time_occurred': self.time_occurred
        }

class Alert:
    def __init__(self, alert_id, disaster_id, alert_type, message, time_sent):
        self.alert_id = alert_id
        self.disaster_id = disaster_id
        self.alert_type = alert_type
        self.message = message
        self.time_sent = time_sent

    def send_alert(self):
        # In a real-world app, you'd send the alert via email/SMS here
        print(f"Alert: {self.message}")
