from app import app,db
from app.database_models import EmergencyCenter

with app.app_context():
    email = input("Enter Center email: ")
    
    # Check if the email already exists in the EmergencyCenter table
    existing_center = EmergencyCenter.query.filter_by(email=email).first()

    if existing_center:
        print(f"This email already exists: {email}")
    else:
        # Collect other details from the user
        name = input('Enter Center Name: ')
        password = input("Enter Center password: ")

        # Create a new EmergencyCenter instance and hash the password 
        new_center = EmergencyCenter(name=name, email=email)
        # This will hash the password automatically
        new_center.set_password(password)  

        # Add the new EmergencyCenter to the session and commit
        db.session.add(new_center)
        db.session.commit()

        print(f"Emergency Center added successfully: {email}")
