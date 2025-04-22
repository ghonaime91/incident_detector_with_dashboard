import json, os, datetime, uuid, mimetypes
from collections import Counter
from flask import (
    request,
    render_template,
    redirect,
    send_file,
    url_for,
    flash,
    session,
    abort,
    current_app
    )
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db, socketio , login_manager
from app.model_predict import process_video
from app.database_models import Incident, EmergencyCenter, IncidentDetails
from app.helpers import logout_required, get_location_name

@app.template_filter('dict_without')
def dict_without(d, key):
    """Remove a key from a dict (used in pagination)."""
    new = d.copy()
    new.pop(key, None)
    return new



# Prediction page
@app.route('/detect', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        # Get the uploaded video
        video_file = request.files['video']
        if video_file:
            # Generate a unique identifier and append it to the filename
            unique_filename = f"{uuid.uuid4().hex}_{video_file.filename}"
            
            # Save the video to the folder
            video_path = os.path.join(
                app.config['UPLOAD_FOLDER'],
                unique_filename
            )
            video_file.save(video_path)

            # Get the location coordinates (latitude and longitude) from the form
            latitude = request.form.get('latitude')
            longitude = request.form.get('longitude')

            # Process the video using the model
            result = process_video(video_path)

            # If the result indicates an accident, display the alert
            return render_template(
                'detection.html',
                result=result,
                latitude=latitude,
                longitude=longitude,
                # Send the unique filename to the frontend 
                video_filename=unique_filename 
            )

    return render_template('detection.html', result=None)


# Dashboard

@app.route('/', methods=['GET'])
@login_required
def index():
    # Get the current page number from the query string, default to page 1
    page = request.args.get('page', 1, type=int)
    
    # Set how many items per page
    per_page = 6 
    
    # Query the incidents and paginate them
    incidents = Incident.query.order_by(
        Incident.id.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    # Get the latest 3 new incidents
    latest_incidents = Incident.query.filter_by(
        status="New"
    ).order_by(
        Incident.date.desc()
    ).limit(3).all()
    
    # Format the incident id to be always 5 digits
    for incident in incidents.items:
        incident.id = str(incident.id).zfill(5)  

    for incident in latest_incidents:
        incident.id = str(incident.id).zfill(5)  
    

    all_incidents = Incident.query.all()
    status_counts = Counter(i.status for i in all_incidents)

    new_count = status_counts.get("New", 0)
    in_progress_count = status_counts.get("In Progress", 0)
    closed_count = status_counts.get("Closed", 0)

    # Get pagination info
    pagination_info = {
        'total': incidents.total,
        'pages': incidents.pages,
        'current_page': incidents.page,
        'has_next': incidents.has_next,
        'has_prev': incidents.has_prev
    }

    return render_template(
        "dashboard/index.html",
        incidents=incidents.items,
        pagination_info=pagination_info,
        latest_incidents=latest_incidents,
        new_count=new_count,
        in_progress_count=in_progress_count,
        closed_count=closed_count
    )

@app.route('/update-status/<int:incident_id>', methods=['POST'])
@login_required
def update_status(incident_id):
    data = request.get_json()  
    
    if not data or 'confirmed' not in data or data['confirmed'] != True:
        return 'Invalid or missing JSON data', 400
    
    incident = Incident.query.get_or_404(incident_id)


    if not incident.details:
        incident.details = IncidentDetails(incident_id=incident.id)

    incident.status = 'In Progress'
    incident.details.emergency_center_id = current_user.id

    db.session.commit()

    return redirect(url_for('incident_response', incident_id=incident.id))

@app.context_processor
def inject_latest_incident_id():
    latest = Incident.query.order_by(Incident.date.desc()).first()
    return {'latest_incident_id': latest.id if latest else 1}


# Route for get Incident Response page
@app.route('/incident-response/<int:incident_id>')
@login_required
def incident_response(incident_id):
    incident = Incident.query.get_or_404(incident_id)
    details = IncidentDetails.query.filter_by(
        incident_id=incident_id
    ).first()

    return render_template(
        "dashboard/incident-response.html",
        incident=incident,
        details=details  
    )



@app.route('/uploads/<path:filename>')
def uploads(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    if not os.path.exists(filepath):
        return abort(404)

    mime_type, _ = mimetypes.guess_type(filepath)
    if mime_type is None:
        mime_type = 'application/octet-stream'  

    return send_file(filepath, mimetype=mime_type)


# Add Or Update Incident details
@app.route('/submit-response/<int:incident_id>', methods=['POST'])
@login_required
def submit_response(incident_id):

    details = IncidentDetails.query.filter_by(
        incident_id=incident_id
    ).first()

    if not details:
        details = IncidentDetails(incident_id=incident_id)

    details.response_type = request.form.get('response_type')
    details.injury_status = request.form.get('injury_status')
    details.injured_count = request.form.get('injured_count')
    details.incident_description = request.form.get(
        'incident_description'
    )
    details.vehicle_count = request.form.get('vehicle_count')
    details.emergency_center_id = current_user.id  

    db.session.add(details)


    incident = db.session.get(Incident, incident_id)
    if incident:
        incident.status = 'Closed'
        db.session.add(incident)

    db.session.commit()

    flash('Response details saved and incident closed.', 'success')
    return redirect(url_for(
        'incident_response',
        incident_id=incident_id
    ))


@app.route('/delete-response/<int:incident_id>')
@login_required
def delete_response(incident_id):
    details = IncidentDetails.query.filter_by(
        incident_id=incident_id
    ).first()
    incident = Incident.query.get(incident_id)

    # If there are details for the incident, delete them
    if details:
        db.session.delete(details)

    # If there is an incident, delete it and the video
    if incident:
        # Get the video path from the media_link field
        video_path = os.path.join(
            current_app.config['UPLOAD_FOLDER'],
            incident.media_link
        )
        
        # Delete the video from the uploads folder if it exists
        if video_path and os.path.exists(video_path):
            os.remove(video_path)

        # Delete the incident itself
        db.session.delete(incident)

    # Commit the changes after deleting all related data
    if details or incident:
        db.session.commit()
        flash('Incident, response details, and video deleted.', 'info')
    else:
        flash('Nothing to delete.', 'warning')

    # Redirect to the dashboard or another page
    return redirect(url_for('index'))


@app.route('/incident/<int:incident_id>/media')
@login_required
def view_media(incident_id):
    incident = Incident.query.get_or_404(incident_id)
    return render_template("dashboard/view_media.html", incident=incident)

@app.route('/incident/<int:incident_id>/location')
@login_required
def view_location(incident_id):
    incident = Incident.query.get_or_404(incident_id)
    try:
        lat, lon = map(
            lambda x: x.split(":")[1].strip(),
            incident.address.split(",")
        )
    except:
        lat, lon = 0, 0  
    return render_template("dashboard/view_location.html", lat=lat, lon=lon)


# Route for Incident Log page
@app.route('/incident-log')
@login_required
def incident_log():
    selected_date = request.args.get('date')
    selected_status = request.args.get('status')
    page = request.args.get('page', 1, type=int)
    per_page = 9

    query = Incident.query

    if selected_date == 'today':
        query = query.filter(Incident.date == datetime.date.today())

    elif selected_date == 'this_week':
        start_of_week = datetime.date.today() - datetime.timedelta(
            days=datetime.date.today().weekday()
        )
        query = query.filter(Incident.date >= start_of_week)

    elif selected_date == 'this_month':
        query = query.filter(
            Incident.date.month == datetime.date.today().month
        )

    if selected_status:
        query = query.filter(
            Incident.status == selected_status.replace('_', ' ').title()
        )

    query = query.order_by(Incident.date.desc())
    incidents = query.paginate(page=page, per_page=per_page)

    return render_template('dashboard/incident-log.html', incidents=incidents)



# Login page
@app.route('/login', methods=['GET', 'POST'])
@logout_required
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        center = EmergencyCenter.query.filter_by(email=email).first()
        if center and center.check_password(password):
            login_user(center)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Please enter a valid email or password.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')


# Register A new Center
@app.route('/register', methods=['GET', 'POST'])
@logout_required
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('register'))

        # Check if email already exists
        existing = EmergencyCenter.query.filter_by(email=email).first()
        if existing:
            flash('Email already registered.', 'error')
            return redirect(url_for('register'))

        # Create a new EmergencyCenter
        new_center = EmergencyCenter(name=name, email=email)
        new_center.set_password(password)

        db.session.add(new_center)
        db.session.commit()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Logout 
@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))


# Alert An Incedent
@app.route('/send_alert', methods=['POST'])
def send_alert():
    # Get the location data from the form (latitude and longitude)
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')

    # Use the get_location_name function to get the name of the location
    location_name = get_location_name(latitude, longitude)

    # Get the video filename
    video_filename = request.form.get('video_filename')

    # If the result was an accident, create a new incident entry in the database
    new_incident = Incident(
        date=datetime.date.today(),
        time=datetime.datetime.now().time(),
        address=f"Lat: {latitude}, Lon: {longitude}", 
        location_name=location_name,  
        status='New',
        media_link=video_filename  
    )

    # Add the new incident to the database
    db.session.add(new_incident)
    db.session.commit()

    # Format the incident id to be 5 digits (adding leading zeros)
    formatted_incident_id = str(new_incident.id).zfill(5)

    # Generate the URL for the incident
    incident_url = url_for('incident_response', incident_id=formatted_incident_id)

    # Emit an event to notify all connected clients
    socketio.emit('new_incident_notification', {
        'incident_id': formatted_incident_id,
        'latitude': latitude,
        'longitude': longitude,
        'location_name': location_name,
        'date': new_incident.date.strftime('%Y-%m-%d'),
        'time': new_incident.time.strftime('%H:%M:%S'),
        'status': new_incident.status,
        'media_link': new_incident.media_link,
        'incident_url': incident_url  
    })

    # Redirect to the page that receives the call (alert confirmation)
    return redirect(url_for('receive_call'))



@app.route('/call', methods=['GET'])
@login_required
def call():
    return render_template('call.html')


@app.route('/receive', methods=['GET'])
def receive_call():
    return render_template('receiver.html')



@app.route('/cancel_alert', methods=['GET'])
def cancel():
    return redirect(url_for('predict'))






