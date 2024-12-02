from flask import Flask, jsonify, request
import requests
import sqlite3
import bcrypt
import os
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from dotenv import load_dotenv
from flasgger import swag_from
from swagger.config import init_swagger

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
jwt = JWTManager(app)

# Initialize Swagger
init_swagger(app)



