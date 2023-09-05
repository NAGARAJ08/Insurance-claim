import bcrypt
import jwt
from flask import Flask
from flask import render_template, request, redirect, url_for, jsonify

import auth
import database
import engine
import models

app = Flask(__name__, template_folder='templates')


# Existing route definitions
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get user credentials from the form
        email = request.form.get("email")
        password = request.form.get("password")

        # Authenticate the user
        if authenticate_user(email, password):
            # Generate a JWT token
            token = auth.generate_jwt_token(email)
            print("The Bearer token received is: ", token)
            return render_template('submit_claim.html', email=email, bearer_token=token)

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get user credentials from the form
        email = request.form.get("email")
        password = request.form.get("password")

        # Register the user
        if register_user(email, password):
            return redirect(url_for('login'))

    return render_template('register.html')


# ... (previous code)

@app.route('/submit_claim', methods=['POST'])
def submit_claim():
    # Extract data from the form
    print(request.form)

    bearer_token = request.form.get("bearer_token")
    user_email = request.form.get("email")
    incident_date = request.form.get("incident_date")
    description = request.form.get("description")

    if not bearer_token:
        return jsonify({"error": "Missing token"}), 401

    # Verify the JWT token
    try:
        decoded_token = auth.decode_jwt_token(bearer_token)
        if decoded_token["email"] != user_email:
            return jsonify({"error": "Invalid token for this user"}), 401
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401

    # Check if the user exists
    user = database.get_user_by_email(user_email)
    if user is None:
        return jsonify({"error": "User not found. Please register first."}), 404

    # Now that we have checked if user is None, we can access its properties safely
    user_id = user.get("_id", None)

    if user_id:
        claim = {
            "user_id": user_id,
            "incident_date": incident_date,
            "description": description
        }
        if engine.evaluate_claim_period(claim):
            claim_id = str(database.add_claim(claim))
            message = "Claim submitted and approved"
            return render_template('claim_result.html', message=message, claim_id=claim_id)
            # return jsonify({"message": "Claim submitted and approved", "claim_id": claim_id}), 200
        else:
            error = "Invalid Claim"
            return render_template('claim_result.html', error=error)
    else:
        return jsonify({"error": "User not found. Please register first."}), 404

# ... (previous code)


# Implement your user authentication and registration functions here
def authenticate_user(email, password):
    # Check email and password against the database
    user = database.get_user_by_email(email)
    if user:
        hashed_password = user.get("password", b"")  # Default to bytes if password is not found
        if bcrypt.checkpw(password.encode("utf-8"), hashed_password):
            return True  # Authentication successful
    return False  # Authentication failed


def register_user(email, password):
    # Check if the user already exists in the database
    existing_user = database.get_user_by_email(email)
    if existing_user:
        return False  # User already exists, registration failed

    # Hash the password before storing it in the database
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    # Insert the user document into the database
    user_id = database.add_user(email, hashed_password)  # Insert email and hashed_password into the database

    if user_id:
        return True  # Registration successful
    else:
        return False  # Registration failed


if __name__ == '__main__':
    app.run(debug=True)
