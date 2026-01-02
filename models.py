"""
Database models for Freelancer SDK Demo
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    """User model for storing Freelancer OAuth tokens."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255))
    access_token = db.Column(db.Text)
    refresh_token = db.Column(db.Text)
    projects = db.relationship("Project", backref="user", lazy=True)

    def __init__(self, name, email, access_token, refresh_token):
        self.name = name
        self.email = email
        self.access_token = access_token
        self.refresh_token = refresh_token

    def __repr__(self):
        return f'<User {self.name}>'


class Project(db.Model):
    """Project model for tracking created projects."""
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def __init__(self, project_id, user_id):
        self.project_id = project_id
        self.user_id = user_id

    def __repr__(self):
        return f'<Project {self.project_id}>'
