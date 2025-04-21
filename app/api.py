import json
import os
import re
import uuid
from flask import  jsonify, request
from app import app
from app.database_models import Incident, IncidentDetails
from app.model_predict import process_video





# API endpoint to receive and process the video and location
@app.route('/api/detect', methods=['POST'])
def api_predict():
    # Check if video and location are in the request
    if 'video' not in request.files:
        return jsonify({
            "success": False,
            "message": "No video part in the request"
        }), 400
    
    # Check if location is provided in JSON format
    if 'location' not in request.form:
        return jsonify({
            "success": False,
            "message": "Location not provided"
        }), 400

    # Get the location data from the form
    location_data = request.form['location']
    location = json.loads(location_data)
    
    latitude = location.get('latitude')
    longitude = location.get('longitude')

    # Get the video file
    video_file = request.files['video']
    if video_file.filename == '':
        return jsonify({
            "success": False,
            "message": "Please select a video"
        }), 400

    # Generate a unique filename for the video
    unique_filename = f"{uuid.uuid4().hex}_{video_file.filename}"

    # Save the video to the uploads folder
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    video_file.save(video_path)

    # Run the accident detection
    result = process_video(video_path)

    # Return the result along with the location data and video link
    return jsonify({
        "success": True,
        "result": result,
        "location": {
            "latitude": latitude,
            "longitude": longitude
        },
        # The relative path to the saved video
        "video_link": f"uploads/{unique_filename}"  
    }), 200

@app.route('/api/incident-response/<int:incident_id>', methods=['GET'])
def api_incident_response(incident_id):
    # Search for the incident using the incident_id from the URL
    incident = Incident.query.get(incident_id)
    if not incident:
        return jsonify({
            "success": False,
            "message": "Incident not found"
        }), 404
    
    # Fetch the incident details
    details = IncidentDetails.query.filter_by(incident_id=incident_id).first()
    if not details:
        return jsonify({
            "success": False,
            "message": "Incident details not found"
        }), 404

    # Extract lat and lon from the address string
    address = incident.address 
    
    # Use regex to extract lat and lon from the address string
    match = re.match(r"Lat:\s*([0-9.-]+),\s*Lon:\s*([0-9.-]+)", address)
    if match:
        lat = float(match.group(1))  
        lon = float(match.group(2)) 
    else:
        lat = lon = None 

    # Prepare the data to be returned in the response
    data = {
        "response_type": details.response_type if details.response_type else "N/A", 
        "injury_status": details.injury_status if details.injury_status else "N/A", 
        "number_of_Injured": details.injured_count if details.injured_count else 0, 
        "incident_description": details.incident_description\
              if details.incident_description else "N/A", 
        "number_of_vehicles_involved": details.vehicle_count\
              if details.vehicle_count else 0, 
        "center_name": details.center.name if details.center else "Unknown",
        "address": {
            "lat": lat,
            "lon": lon
        }  # Return the address as a JSON object with lat and lon
    }

    # Return a JSON response with the data
    return jsonify({"success": True, "data": data}), 200

@app.route('/api/incident-log', methods=['GET'])
def api_incident_log():
    # Get the page number from the URL (default to 1 if not provided)
    page = request.args.get('page', 1, type=int)
    per_page = 6  # Set number of incidents per page

    # Query all incidents, ordered by date descending
    incidents = Incident.query.order_by(
        Incident.date.desc()).paginate(
            page=page, per_page=per_page
        )

    # Prepare the data to be returned in the response
    incident_data = []
    for incident in incidents.items:
        # Fetch center name from IncidentDetails 
        center_name = "Unknown"  # Default if no center found
        if incident.details and incident.details.center:
            center_name = incident.details.center.name

        incident_data.append({
            "id": incident.id,
            "date": incident.date.strftime('%d %b %Y'),
            "address": incident.location_name or "N/A",
            "status": incident.status,
            "video_name": incident.media_link if incident.media_link else "No Media",
            "center_name": center_name  
        })

    # Return JSON response with the data and pagination info
    return jsonify({
        "success": True,
        "data": incident_data,
        "pagination": {
            "page": incidents.page,
            "total_pages": incidents.pages,
            "total_items": incidents.total
        }
    }), 200

