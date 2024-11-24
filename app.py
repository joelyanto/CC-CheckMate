from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from datetime import datetime, timedelta, time
import threading
import time as t
import pymysql
import os
from werkzeug.security import generate_password_hash, check_password_hash
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np

# Flask setup
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your_secret_key'
jwt = JWTManager(app)

# Load face classification model
model = load_model('face_classifier.h5')

# Database connection
def connect_db():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='schools'
    )

# Register user
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    name, email, password, role = data['name'], data['email'], data['password'], data['role']
    hashed_password = generate_password_hash(password)
    
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
                           (name, email, hashed_password, role))
            user_id = cursor.lastrowid
            
            # Insert into specific tables based on role
            if role == 'siswa':
                cursor.execute("INSERT INTO siswa (user_id) VALUES (%s)", (user_id,))
            elif role == 'guru':
                cursor.execute("INSERT INTO guru (user_id) VALUES (%s)", (user_id,))
            elif role == 'orang_tua':
                cursor.execute("INSERT INTO orang_tua (user_id, student_id) VALUES (%s, NULL)", (user_id,))
                
        connection.commit()
        return jsonify({"status": "success", "message": "User registered successfully"}), 201
    finally:
        connection.close()

if __name__ == '__main__':
    app.run(debug=True)
