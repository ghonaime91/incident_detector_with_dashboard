import os
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_login import LoginManager
from uuid import uuid4

# Initialize the Flask application
app = Flask(__name__)
app.secret_key = uuid4().hex
# Enable Cross-Origin Resource Sharing (CORS) for all domains
CORS(app)

# Handle login
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# Initialize SocketIO for real-time communication
socketio = SocketIO(app, cors_allowed_origins="*") 

# Define the folder to save uploaded video files
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')

# Create the 'uploads' folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Save the upload folder path in Flask's configuration
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configure the database URI for SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///saqr.db'

# Disable modification tracking for SQLAlchemy (it’s not necessary in this case)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Import the db instance from the models file to initialize it
from app.database_models import db

# Initialize the db instance with the Flask app
db.init_app(app)

# Create all database tables based on the defined models
with app.app_context():
    db.create_all()

# Import routes, live call, and error handlers for the app
from app import routes, live_call, errors, api

