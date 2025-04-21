from functools import wraps
from geopy.geocoders import Nominatim
from app import login_manager
from flask import redirect, url_for
from flask_login import current_user
from app.database_models import EmergencyCenter

# Convert Lat and Lon Into Location name
geolocator = Nominatim(user_agent="incident_dashboard")

def get_location_name(lat, lon):
    try:
        location = geolocator.reverse((lat, lon), language='en')
        if location and location.address:
            address = location.raw.get('address', {})
            road = address.get('road', '')
            suburb = address.get('suburb', '')
            city = address.get('city', '') or address.get(
                'town', ''
            ) or address.get('village', '')
            return f"{road}, {suburb}, {city}".strip(', ')
        return f"Lat: {lat}, Lon: {lon}"
    except:
        return f"Lat: {lat}, Lon: {lon}"
    
# Function To manage login
@login_manager.user_loader
def load_user(user_id):
    return EmergencyCenter.query.get(int(user_id)) 
# Decorator to ensure user is logged out
def logout_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for('index')) 
        return f(*args, **kwargs)
    return decorated_function