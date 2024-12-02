from flask import Flask, jsonify, request
import requests
import sqlite3
import bcrypt
import os
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from dotenv import load_dotenv
from flasgger import swag_from
import datetime
from swagger.config import init_swagger
from user import register_user, get_user

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
SECRET_KEY = os.getenv('SECRET_KEY')
jwt = JWTManager(app)

# Initialize Swagger
init_swagger(app)

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
    
    status, result = register_user(
        {
        'email': email,
        'password': hashed
        }   
    )

    return jsonify(result), status



@app.route('/login', methods=['POST'])
@swag_from('swagger/login.yaml')
def login():
    data = request.json
    
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Missing email or password"}), 400
    
    email = data['email']
    password = data['password']
    
    status, result = get_user(email)
    
    if status != 200:
        return jsonify(result), status
    
    if result and bcrypt.checkpw(password.encode('utf-8'), result['password']):
        access_token = _create_token(email)
        return jsonify({
            "message": "Login successful",
            "access_token": access_token
        })
    
    return jsonify({"error": "Invalid email or password"}), 401



def _create_token(email, roles): 
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    payload = { 
            'exp': now + datetime.timedelta(days=1), 
            'iat': now, 
            'sub': email, 
            'roles': roles
        } 
    
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256') 

def _decode_token(token): 
    try: 
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256']) 
        return payload
    except jwt.ExpiredSignatureError: return 'Token expired. Please log in again.' 
    except jwt.InvalidTokenError: return 'Invalid token. Please log in again.'
