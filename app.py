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

# Update profile
@app.route('/api/update_profile', methods=['PUT'])
@jwt_required()
def update_profile():
    # Ambil data pengguna yang login dari token JWT
    user = get_jwt_identity()
    role = user['role']  # Ambil role dari data user di token JWT
    
    # Data yang dikirimkan oleh client
    data = request.get_json()
    
    # Validasi data berdasarkan role
    required_fields = {
        'siswa': ['class', 'grade'],
        'guru': ['subject', 'qualification'],
        'orang_tua': ['phone_number', 'address', 'student_id']
    }
    
    if role not in required_fields:
        return jsonify({"status": "error", "message": "Invalid role"}), 400
    
    missing_fields = [field for field in required_fields[role] if field not in data]
    if missing_fields:
        return jsonify({
            "status": "error",
            "message": f"Missing required fields: {', '.join(missing_fields)}"
        }), 422
    
    # Koneksi ke database
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            if role == 'siswa':
                cursor.execute("""
                    UPDATE siswa SET class=%s, grade=%s WHERE user_id=%s
                """, (data.get('class'), data.get('grade'), user['id']))
            elif role == 'guru':
                cursor.execute("""
                    UPDATE guru SET subject=%s, qualification=%s WHERE user_id=%s
                """, (data.get('subject'), data.get('qualification'), user['id']))
            elif role == 'orang_tua':
                cursor.execute("""
                    UPDATE orang_tua SET phone_number=%s, address=%s, student_id=%s WHERE user_id=%s
                """, (data.get('phone_number'), data.get('address'), data.get('student_id'), user['id']))
        
        # Simpan perubahan ke database
        connection.commit()
        return jsonify({"status": "success", "message": "Profile updated successfully"}), 200
    except Exception as e:
        connection.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        connection.close()

# Get profile
@app.route('/api/get_profile', methods=['GET'])
@jwt_required()
def get_profile():
    # Ambil data pengguna yang login dari token JWT
    user = get_jwt_identity()
    user_id = user['id']
    role = user['role']

    # Koneksi ke database
    connection = connect_db()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # Ambil data umum dari tabel `users`
            cursor.execute("SELECT id, name, email, role FROM users WHERE id=%s", (user_id,))
            user_data = cursor.fetchone()
            
            if not user_data:
                return jsonify({"status": "error", "message": "User not found"}), 404
            
            # Ambil data spesifik berdasarkan role
            if role == 'siswa':
                cursor.execute("SELECT class, grade FROM siswa WHERE user_id=%s", (user_id,))
                specific_data = cursor.fetchone()
            elif role == 'guru':
                cursor.execute("SELECT subject, qualification FROM guru WHERE user_id=%s", (user_id,))
                specific_data = cursor.fetchone()
            elif role == 'orang_tua':
                cursor.execute("SELECT phone_number, address, student_id FROM orang_tua WHERE user_id=%s", (user_id,))
                specific_data = cursor.fetchone()
            else:
                return jsonify({"status": "error", "message": "Invalid role"}), 400

            # Gabungkan data umum dan spesifik
            profile_data = {**user_data, **(specific_data or {})}
            return jsonify({"status": "success", "data": profile_data}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        connection.close()

@app.route('/api/predict', methods=['POST'])
@jwt_required()
def predict():
    user = get_jwt_identity()
    if user['role'] != 'guru':
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
    
    if 'file' not in request.files:
        return jsonify({"error": "Invalid request"}), 400
    
    file = request.files['file']
    temp_path = os.path.join("temp", file.filename)
    file.save(temp_path)
    
    # Predict with model
    img = image.load_img(temp_path, target_size=(128, 128))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0) / 255.0
    prediction = model.predict(img_array)
    os.remove(temp_path)
    
    predicted_name = "nagita" if prediction[0] > 0.5 else "raffi"
    
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            send_message = []
            attendance_count = 0
            
            # Hanya ambil siswa yang namanya sesuai dengan prediksi
            cursor.execute("""
                SELECT s.id, u.name 
                FROM siswa s
                JOIN users u ON s.user_id = u.id
                WHERE LOWER(u.name) LIKE %s
            """, (f"%{predicted_name.lower()}%",))
            
            matching_student = cursor.fetchone()
            
            if matching_student:
                student_id, student_name = matching_student[0], matching_student[1]
                
                # Periksa waktu saat ini
                current_time = datetime.now().time()
                current_date = datetime.now().date()
                cutoff_time = time(7, 0)  # Jam 7:00
                status = 'Hadir' if current_time <= cutoff_time else 'Terlambat'
                
                # Periksa kehadiran terakhir siswa
                cursor.execute("""
                    SELECT id, DATE(date) as attendance_date
                    FROM attendance
                    WHERE student_id = %s
                    ORDER BY date DESC
                    LIMIT 1
                """, (student_id,))
                
                last_attendance = cursor.fetchone()
                
                if last_attendance:
                    last_attendance_date = last_attendance[1]
                    
                    if last_attendance_date == current_date:
                        # Update jika di hari yang sama
                        cursor.execute("""
                            UPDATE attendance
                            SET status = %s, date = NOW()
                            WHERE id = %s
                        """, (status, last_attendance[0]))
                    else:
                        # Insert baru jika hari berbeda
                        cursor.execute("""
                            INSERT INTO attendance (student_id, status, date) 
                            VALUES (%s, %s, NOW())
                        """, (student_id, status))
                        attendance_count += 1
                else:
                    # Insert baru jika belum ada record
                    cursor.execute("""
                        INSERT INTO attendance (student_id, status, date) 
                        VALUES (%s, %s, NOW())
                    """, (student_id, status))
                    attendance_count += 1
                
                # Update pesan terakhir orang tua
                message = f"Siswa {student_name.title()} {status} pada {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                cursor.execute("""
                    UPDATE orang_tua 
                    SET last_message = %s 
                    WHERE student_id = %s
                """, (message, student_id))
                send_message.append(message)
                
        connection.commit()
        return jsonify({
            "status": "success",
            "predicted_name": predicted_name,
            "send_message": send_message,
            "attendance_count": attendance_count
        })
    except Exception as e:
        connection.rollback()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    finally:
        connection.close()

@app.route('/api/attendance/today', methods=['GET'])
@jwt_required()
def get_today_attendance():
    user = get_jwt_identity()

    # Pastikan hanya guru yang bisa mengakses endpoint ini
    if user['role'] != 'guru':
        return jsonify({"status": "error", "message": "Unauthorized"}), 403

    # Untuk debugging, bisa menggunakan parameter date dari query string
    target_date = request.args.get('date')
    
    if target_date:
        try:
            # Validasi format tanggal
            datetime.strptime(target_date, '%Y-%m-%d')
        except ValueError:
            return jsonify({
                "status": "error",
                "message": "Invalid date format. Use YYYY-MM-DD"
            }), 400
    else:
        # Jika tidak ada parameter date, gunakan hari ini
        target_date = datetime.today().strftime('%Y-%m-%d')

    # Koneksi ke database
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            # Query untuk mendapatkan semua data kehadiran
            cursor.execute("""
                SELECT a.student_id, u.name, a.status, a.date
                FROM attendance a
                JOIN siswa s ON a.student_id = s.id
                JOIN users u ON s.user_id = u.id
                WHERE DATE(a.date) = %s
                ORDER BY a.date DESC
            """, (target_date,))

            # Ambil hasil query
            attendance_data = cursor.fetchall()

            # Debug info
            debug_info = {
                "queried_date": target_date,
                "is_future_date": target_date > datetime.today().strftime('%Y-%m-%d'),
                "total_records": len(attendance_data)
            }

            # Jika tidak ada data
            if not attendance_data:
                return jsonify({
                    "status": "success",
                    "message": "No attendance records found",
                    "date": target_date,
                    "debug_info": debug_info
                }), 200

            # Struktur data untuk response
            attendance_list = []
            for row in attendance_data:
                student_id = row[0]
                student_name = row[1]
                status = row[2]
                attendance_time = row[3].strftime('%Y-%m-%d %H:%M:%S')

                attendance_list.append({
                    "student_id": student_id,
                    "student_name": student_name,
                    "attendance_status": status,
                    "attendance_time": attendance_time
                })

        # Mengembalikan data kehadiran
        return jsonify({
            "status": "success",
            "date": target_date,
            "attendance": attendance_list,
            "debug_info": debug_info
        })

    finally:
        connection.close()

if __name__ == '__main__':
    app.run(debug=True)
