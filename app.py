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

# Login user
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email, password = data['email'], data['password']
    
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, password, role FROM users WHERE email=%s", (email,))
            user = cursor.fetchone()
            if user and check_password_hash(user[1], password):
                token = create_access_token(identity={"id": user[0], "role": user[2]}, expires_delta=timedelta(days=1))
                return jsonify({"status": "success", "token": token})
            return jsonify({"status": "error", "message": "Invalid credentials"}), 401
    finally:
        connection.close()

@app.route('/api/logout', methods=['POST'])
@jwt_required()
def logout():
    # Mendapatkan JWT ID unik (JTI) dari token yang sedang digunakan
    jti = get_jwt()["jti"]
    
    # Menyimpan JTI ke blacklist di database
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            # Menyimpan jti yang sudah dicabut di blacklist
            cursor.execute("INSERT INTO token_blacklist (jti) VALUES (%s)", (jti,))
        connection.commit()

        return jsonify({"status": "success", "message": "Successfully logged out."}), 200
    except Exception as e:
        connection.rollback()
        # Adding logging for the error
        app.logger.error(f"Error during logout: {e}")
        return jsonify({"status": "error", "message": "An error occurred during logout."}), 500
    finally:
        connection.close()

@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            # Memeriksa apakah JTI ada di blocklist
            cursor.execute("SELECT * FROM token_blacklist WHERE jti = %s", (jti,))
            result = cursor.fetchone()
            if result:
                app.logger.info(f"Token with JTI {jti} is blacklisted.")
                return True  # Token ditemukan di blocklist, maka token dianggap tidak valid
            return False  # Token tidak ditemukan, berarti valid
    finally:
        connection.close()

if __name__ == '__main__':
    app.run(debug=True)
