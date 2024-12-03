from flask import Flask, jsonify, request, make_response
import requests
import sqlite3
import bcrypt
import os
import jwt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flasgger import swag_from
import datetime
from swagger.config import init_swagger
import user
import auth

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Initialize Swagger
init_swagger(app)

# ----------------------------------------------------- POST /register
@app.route('/register', methods=['POST'])
@swag_from('swagger/register.yaml')
def register():
    data = request.json
    
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Missing email or password"}), 400
    
    email = data['email']
    password = data['password']
    
    # Hash the password
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    status, result = user.register_user(
        {
        'email': email,
        'password': hashed
        }   
    )

    return jsonify(result), status

# ----------------------------------------------------- POST /login
@app.route('/login', methods=['POST'])
@swag_from('swagger/login.yaml')
def login():
    data = request.json
    
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Missing email or password"}), 400
    
    email = data['email']
    password = data['password']
    
    status, result = user.get_user_by_email(email)
    
    if status != 200:
        return jsonify(result), status
    
    if result and _check_password(password, result['password']):
        access_token = auth.create_token(email, result['roles'])

        # Create the response and add the token to the Authorization header 
        response = make_response(jsonify({ "message": "Login successful", "Authorization": f'Bearer {access_token}'}), status) 
        # Automatically add the token to header
        response.headers['Authorization'] = f'Bearer {access_token}' 
        
        return response
    
    return jsonify({"error": "Invalid email or password"}), 401

# ----------------------------------------------------- GET /users
@app.route('/users', methods=['GET'])
@swag_from('swagger/login.yaml') # TODO
def get_users():
    status, result = user.get_users()
    return jsonify(result), status
    
# ----------------------------------------------------- PATCH /users/id
@app.route('/users/<int:id>', methods=['PATCH'])
@swag_from('swagger/login.yaml') # TODO
def patch_user(id):
    data = request.json

    email = data.get('email')
    new_password = data.get('new_password')
    old_password = data.get('old_password')

    if email and new_password and old_password:
        if _check_password(old_password, id):
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            status, result = user.update_user(id, {"email": email, "password": hashed_password})
            return jsonify(result), status
        
        return jsonify({"message": "Wrong old password"}), 404
    
    elif email:
        status, result = user.update_user(id, {"email": email})
        return jsonify(result), status
    
    elif new_password and old_password:
        if _check_password(old_password, id):
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            status, result = user.update_user(id, {"password": hashed_password})
            return jsonify(result), status
        
        return jsonify({"message": "Wrong old password"}), 404
    
    return jsonify({"message": "Please enter a new email or an old and new password first"}), 404

# ----------------------------------------------------- PATCH /users/id/add-role
@app.route('/users/<int:id>/add-role', methods=['PATCH'])
@swag_from('swagger/login.yaml') # TODO
def user_add_role(id):
    data = request.json

    new_role = data.get('new_role')

    if new_role:
        status, result = user.get_user(id)

        if status == 200:
            role_status, role_result = user.add_role(result['email'], new_role)
            return jsonify(role_result), role_status

        return jsonify(result), status

    return jsonify({"message": "Please enter a role to add first"}), 404

# ----------------------------------------------------- PATCH /users/id/remove-role
@app.route('/users/<int:id>/remove-role', methods=['PATCH'])
@swag_from('swagger/login.yaml') # TODO
def user_remove_role(id):
    data = request.json

    remove_role = data.get('remove_role')

    if remove_role:
        status, result = user.get_user(id)

        if status == 200:
            role_status, role_result = user.remove_role(result['email'], remove_role)
            return jsonify(role_result), role_status

        return jsonify(result), status

    return jsonify({"message": "Please enter a role to remove first"}), 404


# ----------------------------------------------------- DELETE /users/id
@app.route('/users/<int:id>', methods=['DELETE'])
@swag_from('swagger/login.yaml') # TODO
def delete_user(id):
    status, result = user.delete_user(id)
    return jsonify(result), status

# ----------------------------------------------------- GET /health
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

def _check_password(check_password, id):
    status, result = user.get_user_password(id)

    if status != 200:
        return jsonify(result), status

    return bcrypt.checkpw(check_password.encode('utf-8'), result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 80)))
