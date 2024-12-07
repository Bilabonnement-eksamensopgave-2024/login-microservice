from flask import Flask, jsonify, request, make_response
import bcrypt
import os
from flasgger import swag_from
from swagger.config import init_swagger
import user
import auth
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Initialize Swagger
init_swagger(app)

# ----------------------------------------------------- Private functions
def _check_password(check_password, id):
    status, result = user.get_user_password(id)

    if status != 200:
        return jsonify(result), status

    return bcrypt.checkpw(check_password.encode('utf-8'), result)

# ----------------------------------------------------- GET /
@app.route('/', methods=['GET'])
def service_info():
    return jsonify({
        "service": "User Management Microservice",
        "description": "This microservice handles user-related operations such as registration, login, role management, and user updates.",
        "endpoints": [
            {
                "path": "/register",
                "method": "POST",
                "description": "Register a new user",
                "response": "JSON object with success or error message",
                "role_required": "none"
            },
            {
                "path": "/login",
                "method": "POST",
                "description": "Authenticate a user and return a token",
                "response": "JSON object with token or error message",
                "role_required": "none"
            },
            {
                "path": "/users",
                "method": "GET",
                "description": "Retrieve a list of all users",
                "response": "JSON array of user objects",
                "role_required": "admin"
            },
            {
                "path": "/users/<int:id>",
                "method": "PATCH",
                "description": "Update email or password of a specific user",
                "response": "JSON object with success or error message",
                "role_required": "admin"
            },
            {
                "path": "/users/<int:id>/add-role",
                "method": "PATCH",
                "description": "Add a role to a specific user",
                "response": "JSON object with success or error message",
                "role_required": "admin"
            },
            {
                "path": "/users/<int:id>/remove-role",
                "method": "PATCH",
                "description": "Remove a role from a specific user",
                "response": "JSON object with success or error message",
                "role_required": "admin"
            },
            {
                "path": "/users/<int:id>",
                "method": "DELETE",
                "description": "Delete a user by ID",
                "response": "JSON object with success or error message",
                "role_required": "admin"
            },
            {
                "path": "/health",
                "method": "GET",
                "description": "Check the health status of the microservice",
                "response": "JSON object indicating the health status",
                "role_required": "none"
            },
            {
                "path": "/logout",
                "method": "POST",
                "description": "Logout and delete the authorization cookie",
                "response": "JSON object with a success message",
                "role_required": "none"
            }
        ]
    })

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
        response = make_response(jsonify({ "message": "Login successful", "Authorization": access_token}), status) 
        # Automatically set token as a cookie
        response.set_cookie('Authorization', access_token, httponly=True, secure=True)
        
        return response
    
    return jsonify({"error": "Invalid email or password"}), 401

# ----------------------------------------------------- GET /users
@app.route('/users', methods=['GET'])
@auth.role_required('admin') 
@swag_from('swagger/get_users.yaml')
def get_users():
    status, result = user.get_users()
    return jsonify(result), status
    
# ----------------------------------------------------- PATCH /users/id
@app.route('/users/<int:id>', methods=['PATCH'])
@auth.role_required('admin') 
@swag_from('swagger/patch_user.yaml') 
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
@auth.role_required('admin') 
@swag_from('swagger/user_add_role.yaml')
def user_add_role(id):
    data = request.json

    new_role = data.get('new_role')

    if new_role:
        status, result = user.get_user(id)

        if status == 200:
            role_status, role_result = user.add_role(result['email'], new_role)

            if role_status == 201:
                access_token = auth.create_token(result['email'], result['roles'])

                # Create the response and add the token to the Authorization header 
                response = make_response(jsonify(role_result), status) 
                # Automatically set token as a cookie
                response.set_cookie('Authorization', access_token, httponly=True, secure=True)
                
                return response
            
            return jsonify(role_result), role_status

        return jsonify(result), status

    return jsonify({"message": "Please enter a role to add first"}), 404

# ----------------------------------------------------- PATCH /users/id/remove-role
@app.route('/users/<int:id>/remove-role', methods=['PATCH'])
@auth.role_required('admin') 
@swag_from('swagger/user_remove_role.yaml')
def user_remove_role(id):
    data = request.json

    remove_role = data.get('remove_role')

    if remove_role:
        status, result = user.get_user(id)

        if status == 200:
            role_status, role_result = user.remove_role(result['email'], remove_role)

            if role_status == 201:
                access_token = auth.create_token(result['email'], result['roles'])

                # Create the response and add the token to the Authorization header 
                response = make_response(jsonify(role_result), status) 
                # Automatically set token as a cookie
                response.set_cookie('Authorization', access_token, httponly=True, secure=True)
                
                return response
            
            return jsonify(role_result), role_status

        return jsonify(result), status

    return jsonify({"message": "Please enter a role to remove first"}), 404


# ----------------------------------------------------- DELETE /users/id
@app.route('/users/<int:id>', methods=['DELETE'])
@auth.role_required('admin') 
@swag_from('swagger/delete_user.yaml')
def delete_user(id):
    status, result = user.delete_user(id)
    return jsonify(result), status


# ----------------------------------------------------- POST /logout
@app.route('/logout', methods=['POST'])
def logout():
    response = make_response(jsonify({"message": "Logout successful"}))
    
    # Set the cookie with the same name to expire in the past so the browser will delete the cookie
    response.set_cookie('Authorization', '', expires=0, httponly=True, secure=True)
    
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5005)))


# ----------------------------------------------------- GET /health
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

# ----------------------------------------------------- Catch-all route for unmatched endpoints
@app.errorhandler(404)
def page_not_found_404(e):
    return jsonify({"message": "Endpoint does not exist"}), 404

@app.errorhandler(405)
def page_not_found_405(e):
    return jsonify({"message": "Method not allowed - double check the method you are using"}), 405

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5005)))
