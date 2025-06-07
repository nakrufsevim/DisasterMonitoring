import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///disasters.db'  # SQLite database (use PostgreSQL for production)
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable modification tracking to avoid warnings
    SECRET_KEY = os.urandom(24)  # Used for session management, etc.
