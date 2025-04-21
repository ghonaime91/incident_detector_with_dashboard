from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum
from sqlalchemy.orm import backref
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

# Initialize the SQLAlchemy instance
db = SQLAlchemy()

# Define possible incident statuses as an Enum
incident_status_enum = ('New', 'In Progress', 'Closed')

# EmergencyCenter model: Represents an emergency center that responds to incidents
class EmergencyCenter(db.Model, UserMixin):
    # Define the columns for the EmergencyCenter table
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    
    # Define the relationship between EmergencyCenter and IncidentDetails (One-to-Many)
    incidents = db.relationship(
        'IncidentDetails', 
        backref=backref('center', lazy=True),
        lazy=True, 
        passive_deletes=True
    )

    # Method to set the password by hashing it
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Method to check if the entered password matches the stored hash
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # String representation for the EmergencyCenter
    def __repr__(self):
        return f'<EmergencyCenter {self.name}>'

# Incident model: Represents an incident with associated details
class Incident(db.Model):
    # Define the columns for the Incident table
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    location_name = db.Column(db.String(300))
    
    # Status field as an Enum with possible values: 'New', 'In Progress', 'Closed'
    status = db.Column(
        Enum(*incident_status_enum, name='incident_status_enum'),
        default='New',
        nullable=False
    )
    
    # Column to store the media link (e.g., video)
    media_link = db.Column(db.String(300))
    
    # Define the relationship between Incident and IncidentDetails (One-to-One)
    details = db.relationship(
        'IncidentDetails', 
        backref=backref('incident', lazy=True),
        uselist=False,  # Ensures One-to-One relationship
        passive_deletes=True
    )

    # String representation for the Incident
    def __repr__(self):
        return f'<Incident {self.id} - {self.address} - {self.status}>'

# IncidentDetails model: Represents detailed information about an incident
class IncidentDetails(db.Model):
    # Define the columns for the IncidentDetails table
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign key to link the incident details to an incident (One-to-One)
    incident_id = db.Column(
        db.Integer, 
        db.ForeignKey('incident.id', ondelete='SET NULL'),
        nullable=True
    )
    
    # Other details about the incident
    response_type = db.Column(db.String(100))  
    injury_status = db.Column(db.String(200))  
    injured_count = db.Column(db.Integer)
    incident_description = db.Column(db.Text)
    vehicle_count = db.Column(db.Integer)
    
    # Foreign key to link the incident details to an emergency center (One-to-Many)
    emergency_center_id = db.Column(
        db.Integer, 
        db.ForeignKey('emergency_center.id', ondelete='SET NULL'),
        nullable=True
    )

    # String representation for the IncidentDetails
    def __repr__(self):
        return f'<IncidentDetails for Incident {self.incident_id}>'
