from flask import jsonify, request
import random
import hashlib
import smtplib
import os
import string
from werkzeug.utils import secure_filename
from app_config import app
from database.db import get_db_connection, get_db_error
from model.Student import Student
from email.mime.text import MIMEText

SMTP_SERVER = "smtp.gmail.com"  # e.g., smtp.gmail.com
SMTP_PORT = 587  # For TLS
SMTP_USERNAME = "quymstle125@gmail.com"
SMTP_PASSWORD = "wmfknxmlqexcsyvv"
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['IMAGE_URL'] = 'https://e0d2-2405-4802-461c-c550-a5c0-8423-f9a9-b6cf.ngrok-free.app/uploads/'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Function to generate a random student ID
def generate_student_id(connection):
    while True:
        student_id = f"PH{random.randint(10000, 99999)}"
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM Students WHERE LOWER(idStudents) = LOWER(%s)", (student_id,))
        if cursor.fetchone()[0] == 0:
            cursor.close()  # Ensure cursor is closed
            return student_id
        cursor.close()

# Function to generate a 6-digit OTP
def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

# Function to send an OTP email
def send_otp_email(email, otp):
    try:
        msg = MIMEText(f"Your OTP code is {otp}. It is valid for 10 minutes.")
        msg["Subject"] = "Your OTP Code"
        msg["From"] = SMTP_USERNAME
        msg["To"] = email  # Send to the provided email

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_USERNAME, email, msg.as_string())
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

# Function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to generate an MD5 hash of a string
def string_to_md5(input_string):
    return hashlib.md5(input_string.encode('utf-8')).hexdigest()

# Function to retrieve the list of students
def get_students():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Students")
        students = cursor.fetchall()
        return jsonify(students)
    except get_db_error() as err:
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        connection.close()

# Function  list book
def get_book():
    try:
        connecction = get_db_connection()
        cursor = connecction.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Books")
        books = cursor.fetchall()
        return jsonify(books)
    except get_db_error() as err:
        return jsonify({'error':str(err)}),500
    finally:
        cursor.close
        connecction.close
    

# Function for student login

def login():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Hãy nhập đầy đủ thông tin."}), 400

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT * FROM Students WHERE email = %s", (email,))
        student_data = cursor.fetchone()
        if not student_data:
            return jsonify({"error": "Tài khoản không tồn tại."}), 404

        student_data.pop('image_path', None)
        student = Student(**student_data)

        if student.check_password(password):
            return jsonify({"message": "Đăng nhập thành công", "data": student.to_dict()}), 200
        else:
            return jsonify({"error": "Sai mật khẩu."}), 401

    except get_db_error() as err:
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        connection.close()

# Function for password recovery
def forgot():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({"error": "Please provide an email address."}), 400

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT * FROM Students WHERE email = %s", (email,))
        student_data = cursor.fetchone()
        if not student_data:
            return jsonify({"error": "Account not found."}), 404

        # Generate OTP
        otp = generate_otp()
        print(f"Generated OTP: {otp} (Length: {len(otp)})")  # Debug print

        # Ensure OTP length is correct before updating
        if len(otp) != 6:
            return jsonify({"error": "Generated OTP is not valid."}), 500

        # Store OTP and timestamp in the database
        cursor.execute("UPDATE Students SET otp = %s, otp_timestamp = NOW() WHERE email = %s", (otp, email))
        connection.commit()

        # Send OTP to user's email
        if send_otp_email(email, otp):
            return jsonify({"message": "OTP has been sent to your email."}), 200
        else:
            return jsonify({"error": "Failed to send OTP."}), 500

    except get_db_error() as err:
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        connection.close()

# Function for student registration
def register():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided."}), 400

    data = request.form
    name = data.get('name')
    email = data.get('email')
    password = string_to_md5(data.get('password'))
    course = data.get('course')
    yearBirth = data.get('yearBirth')
    specialized = data.get('specialized')
    phone = data.get('phone')
    gender = data.get('gender')
    image_path = None
    filename = None
    if 'image' in request.files:
        file = request.files['image']
        if file.filename == '':
            return jsonify({"error": "No selected file."}), 400
        if not allowed_file(file.filename):
            return jsonify({"error": "File type not allowed."}), 400
        filename = secure_filename(file.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(image_path)

    image_path = f"{app.config['IMAGE_URL']}{filename}" if filename else None

    try:
        otp =generate_otp()
        print(otp)
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM Students WHERE email = %s", (email,))
        if cursor.fetchone()[0] > 0:
            return jsonify({"error": "Tài khoản đã tồn tại."}), 409

        id_students = generate_student_id(connection)
        cursor.execute("""
            INSERT INTO Students (idStudents, nameStudent, email, password, course, yearBirth, specialized, phone, gender, image_path,otp)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)
        """, (id_students, name, email, password, course, yearBirth, specialized, phone, gender, image_path,otp))
        connection.commit()
        response_data = {
            "idStudents": id_students,
            "name": name,
            "email": email,
            "course": course,
            "yearBirth": yearBirth,
            "specialized": specialized,
            "phone": phone,
            "gender": gender,
            "image_path": image_path,
            "otp":otp
        }
        return jsonify({"message": "Đăng ký thành công!", "data": response_data}), 201
    except get_db_error() as err:
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        connection.close()

# Function to update student account
def update_account():
    data = request.form
    email = data.get('email')
    name = data.get('name')
    phone = data.get('phone')
    password = data.get('password')  # Get raw password, do not hash yet
    course = data.get('course')
    yearBirth = data.get('yearBirth')
    specialized = data.get('specialized')
    gender = data.get('gender')
    passtomd5 = string_to_md5(password)

    if not email:
        return jsonify({"error": "Vui lòng nhập email."}), 400

    filename = None  # Initialize filename for potential new image
    image_path = None
    if 'image' in request.files:
        file = request.files['image']
        if not allowed_file(file.filename):
            return jsonify({"error": "File type not allowed."}), 400
        filename = secure_filename(file.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(image_path)
        image_path = f"{app.config['IMAGE_URL']}{filename}"

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        update_query = """
            UPDATE Students
            SET nameStudent = %s, phone = %s, course = %s, yearBirth = %s, specialized = %s, gender = %s
            {}
            WHERE email = %s
        """.format(", image_path = %s" if filename else "")

        values = [name, phone, course, yearBirth, specialized, gender]

        if filename:
            values.append(image_path)

        values.append(email)

        cursor.execute(update_query, values)
        connection.commit()
        return jsonify({"message": "Cập nhật thông tin thành công."}), 200
    except get_db_error() as err:
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        connection.close()