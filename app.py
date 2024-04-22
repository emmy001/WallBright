from flask import Flask, render_template
from flask import request, redirect, url_for, Response, flash, session, jsonify
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
import hashlib
import os
import cv2
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, auth, firestore
from firebase_admin import db
from firebase_admin import storage
from detection.face_matching import detect_faces, align_face
from detection.face_matching import extract_features, match_face
from utils.configuration import load_yaml
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from flask_mail import Mail, Message


config_file_path = load_yaml("configs/database.yaml")

TEACHER_PASSWORD_HASH = config_file_path["teacher"]["password_hash"]

# Initialize Firebase
cred = credentials.Certificate(config_file_path["firebase"]["pathToServiceAccount"])
firebase_admin.initialize_app(
    cred,
    {
        "databaseURL": config_file_path["firebase"]["databaseURL"],
        "storageBucket": config_file_path["firebase"]["storageBucket"],
    },
)

# Initialize Firestore database
db = firestore.client()

def upload_database(filename):
    """
    Checks if a file with the given filename already exists in the
    database storage, and if not, uploads the file to the database.
    """
    valid = False
    # If the fileName exists in the database storage, then continue
    if storage.bucket().get_blob(filename):
        valid = True
        error = f"<h1>{filename} already exists in the database</h1>"

    # First check if the name of the file is a number
    if not filename[:-4].isdigit():
        valid = True
        error = f"<h1>Please make sure that the name of the {filename} is a number</h1>"

    if not valid:
        # Image to database
        filename = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        bucket = storage.bucket()
        blob = bucket.blob(filename)
        blob.upload_from_filename(filename)
        error = None

    return valid, error

def match_with_database(img, database):
    '''The function "match_with_database" takes an image and a database as input, detects faces in the
    image, aligns and extracts features from each face, and matches the face to a face in the database.
    '''
    global match
    # Detect faces in the frame
    faces = detect_faces(img)
    # Draw the rectangle around each face
    for x, y, w, h in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 4)
    # save the image
    cv2.imwrite("static/recognized/recognized.png", img)
    for face in faces:
        try:
            # Align the face
            aligned_face = align_face(img, face)
            # Extract features from the face
            embedding = extract_features(aligned_face)
            embedding = embedding[0]["embedding"]
            # Match the face to a face in the database
            match = match_face(embedding, database)
            if match is not None:
                return f"Match found: {match}"
            else:
                return "No match found"
        except:
            return "No face detected"
        # break # TODO: remove this line to detect all faces in the frame

app = Flask(__name__, template_folder="template")
app.secret_key = "123456"  # Add this line
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'kajwangeinstein@gmail.com'  # Your Gmail email address
app.config['MAIL_PASSWORD'] = 'use youown for my security purposes'  # Your Gmail password or App Password
app.config['MAIL_DEFAULT_SENDER'] = 'kajwangeinstein@gmail.com'  # Your Gmail email address

mail = Mail(app)

# Specify the directory to save uploaded images
UPLOAD_FOLDER = "static/images"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route('/')
def signup_page():
    return render_template('SignUp.html')

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    # Check if password matches confirm password
    if password != confirm_password:
        return "Passwords do not match!"

    # Check if user already exists
    user_ref = db.collection('users').document(email)
    if user_ref.get().exists:
        return "User already exists!"
    hashed_password = hash_password(password)
    # Create user data
    user_data = {
        'username': username,
        'email': email,
        'password': hashed_password
    }
    # Save user data to Firestore
    user_ref.set(user_data)
    # Redirect to the login page after successful signup
    return redirect(url_for('login'))

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # Retrieve user data from Firestore based on the provided email
        user_ref = db.collection('users').document(email)
        user_data = user_ref.get().to_dict()
        # Check if user exists
        if not user_data:
            return "User does not exist!"
        # Check if the provided password matches the stored hashed password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        if hashed_password != user_data.get('password'):
            return "Incorrect password!"
        # If the email and password are correct, store user data in session
        session['user'] = user_data
        # Redirect to the dashboard or any other page after successful login
        return redirect(url_for('dashboard'))
    # If GET request, render the login page
    return render_template('login.html')
# Forgot password route
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        try:
            # Send password reset email
            auth.generate_password_reset_link(email)
            flash('Password reset link sent to your email.', 'success')
            return redirect(url_for('login'))
        except auth.InvalidEmailError:
            flash('Invalid email address. Please try again.', 'error')
        except Exception as e:
            flash('An error occurred. Please try again later.', 'error')
    return render_template('forgot_password.html')
@app.route('/dashboard')
def dashboard():
    # Check if user is logged in
    if 'user' not in session:
        return redirect(url_for('login'))
    # Retrieve user data from session
    user_data = session['user']
    # Reference to the 'Students' collection
    students_ref = db.collection('Students')
    # Get all documents in the "Students" collection
    student_docs = students_ref.stream()

    students = {}
    for student_doc in student_docs:
        student_data = student_doc.to_dict()
        students[student_doc.id] = [
            student_data.get("name", ""),
            student_data.get("email", ""),
            student_data.get("userType", ""),
            student_data.get("classes", ""),
        ]

    # Get the count of students
    num_students = len(students)
    # Display dashboard with user data and student count
    return render_template('dashboard.html', user_data=user_data, num_students=num_students, students=students)

@app.route('/logout')
def logout():
    # Clear the session to logout the user
    session.pop('user', None)
    return redirect(url_for('login'))


@app.route('/manage_attendance')
def manage_attendance():
    # Add logic for the manage attendance page
    if 'user' not in session:
        return redirect(url_for('login'))
    # Retrieve user data from session
    user_data = session['user']
    return render_template('manage_attendance.html', user_data=user_data)

@app.route("/add_info")
def add_info():
    return render_template("add_info.html")


@app.route("/teacher_login", methods=["GET", "POST"])
def teacher_login():
    if request.method == "POST":
        password = request.form.get("password")
        # Assuming TEACHER_PASSWORD_HASH is defined elsewhere
        if check_password_hash(TEACHER_PASSWORD_HASH, password):
            return redirect(url_for("attendance"))
        else:
            flash("Incorrect password")
    return render_template("teacher_login.html")


@app.route("/attendance")
def attendance():
    if 'user' not in session:
        return redirect(url_for('login'))
    # Retrieve user data from session
    user_data = session['user']
    students_ref = db.collection("Students")
    student_docs = students_ref.stream()  # Get all documents in the "Students" collection

    students = {}
    for student_doc in student_docs:
        student_data = student_doc.to_dict()
        students[student_doc.id] = [
            student_data.get("name", ""),
            student_data.get("email", ""),
            student_data.get("userType", ""),
            student_data.get("classes", ""),
        ]
    return render_template("studentlist.html", user_data=user_data, students=students)


@app.route('/print_report', methods=['POST'])
def print_report():
    attendance_data = get_attendance_data_from_firestore()  # Fetch attendance data from Cloud Firestore
    generate_pdf_report(attendance_data)  # Generate PDF report
    print("Report printed successfully.")
    return redirect(url_for('attendance'))

@app.route('/email_report')
def email_report():
    attendance_data = get_attendance_data_from_firestore()  # Fetch attendance data from Cloud Firestore
    send_email(attendance_data)  # Send email with attendance data
    print("Report emailed successfully.")
    return redirect(url_for('attendance'))

def get_attendance_data_from_firestore():
    # Query Cloud Firestore to fetch attendance data
    attendance_data = {}
    students_ref = db.collection("Students")
    student_docs = students_ref.stream()
    for student_doc in student_docs:
        student_data = student_doc.to_dict()
        attendance_data[student_doc.id] = [
            student_data.get("name", ""),
            student_data.get("email", ""),
            student_data.get("userType", ""),
            student_data.get("classes", {}),
        ]
    return attendance_data

def send_email(attendance_data):
    # Send email with the PDF report as an attachment
    msg = Message('Attendance Report', recipients=['kajwangeinstein@gmail.com'])
    msg.body = 'Please find the attached attendance report.'
    with app.open_resource("attendance_report.pdf") as fp:
        msg.attach("attendance_report.pdf", "application/pdf", fp.read())
    mail.send(msg)

def generate_pdf_report(attendance_data):
    # Generate PDF report using ReportLab
    c = canvas.Canvas("attendance_report.pdf", pagesize=letter)
    c.drawString(100, 750, "Attendance Report")

    # Draw table header
    header = ['Name', 'Email', 'Type', 'Classes and Attendance']
    x_positions = [50, 200, 350, 500]
    for i, column in enumerate(header):
        c.drawString(x_positions[i], 700, column)
    # Draw attendance data
    y = 680  # Starting y-coordinate for drawing data
    for student_id, student_data in attendance_data.items():
        x = 50  # Starting x-coordinate for drawing data
        for i, data in enumerate(student_data):
            if i == 3:  # Handling classes and attendance separately
                for class_name, status in data.items():
                    c.drawString(x, y, f"{class_name}: {status}")
                    y -= 20  # Move to the next row
            else:
                c.drawString(x_positions[i], y, data)
            x += 150  # Move to the next column
        y -= 20  # Move to the next row
    # Add more content to the PDF report as needed
    c.save()


@app.route("/upload", methods=["POST"])
def upload():
    global filename
    if "file" not in request.files:
        return "No file uploaded", 400
    file = request.files["file"]
    if file.filename == "":
        return "No selected file", 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        ref = db.collection("Students")
        try:
            studentId = len(ref.get())
        except TypeError:
            studentId = 1
        filename = f"{studentId}.png"
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        # Assuming upload_database() function is defined elsewhere
        val, err = upload_database(filename)

        if val:
            return err
        return redirect(url_for("add_info"))
    return "File upload failed", 400


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    url = url_for("static", filename="images/" + filename, v=timestamp)
    return f'<h1>File uploaded successfully</h1><img src="{url}" alt="Uploaded image">'


def perform_face_recognition(frame):
    # Load pre-trained face detection and recognition models
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read("configs/haarcascade_frontalface_default.xml")

    # Convert the frame to grayscale for better processing
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Detect faces in the grayscale frame
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Print the number of faces detected
    print(f"Number of faces detected: {len(faces)}")
    recognized_faces = []

    # Iterate over each detected face
    for (x, y, w, h) in faces:
        # Crop the detected face region from the frame
        face_roi = gray[y:y+h, x:x+w]
        # Perform face recognition on the cropped face region
        label, confidence = recognizer.predict(face_roi)
        # If the confidence level is below a certain threshold, consider it as a recognized face
        if confidence < 50:
            # Here, you might fetch the name or ID associated with the recognized label from your database
            # For demonstration purposes, let's assume the label is the name of the person
            name = "Person " + str(label)
            recognized_faces.append((x, y, w, h, name))
    return recognized_faces

def gen_frames():
    global video
    video = cv2.VideoCapture(0)
    while True:
        success, frame = video.read()
        if not success:
            break
        else:
            # Perform face recognition on the frame
            faces = perform_face_recognition(frame)
            # Draw rectangles and text for each recognized face
            for face in faces:
                x, y, w, h, name = face
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                cv2.putText(frame, name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)
            ret, buffer = cv2.imencode(".jpg", frame)
            frame = buffer.tobytes()
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

@app.route("/video_feed")
def video_feed():
    return Response(gen_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/capture", methods=["POST"])
def capture():
    global filename
    ret, frame = video.read()
    if ret:
        ref = db.collection("Students")
        try:
            studentId = len(ref.get())
        except TypeError:
            studentId = 1
        filename = f"{studentId}.png"
        cv2.imwrite(os.path.join(app.config["UPLOAD_FOLDER"], filename), frame)
        # Assuming upload_database() function is defined elsewhere
        val, err = upload_database(filename)
        if val:
            return err
    return redirect(url_for("add_info"))


@app.route("/success/<filename>")
def success(filename):
    return render_template("success_alert.html", filename=filename)

@app.route("/submit_info", methods=["POST"])
def submit_info():
    try:
        name = request.form.get("name")
        email = request.form.get("email")
        userType = request.form.get("userType")
        classes = request.form.getlist("classes")
        password = request.form.get("password")
        current_day = datetime.now().strftime("%A")
        studentId, _ = os.path.splitext(filename)
        fileName = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        data = cv2.imread(fileName)
        faces = detect_faces(data)
        for face in faces:
            aligned_face = align_face(data, face)
            embedding = extract_features(aligned_face)
            break
        ref = db.collection("Students")
        data = {
            str(studentId): {
                "name": name,
                "email": email,
                "userType": userType,
                "classes": {class_: int("0") for class_ in classes},
                "password": password,
                "dayOfWeek": current_day,
                "embeddings": embedding[0]["embedding"],
            }
        }
        # Loop through the data dictionary and set each document in the collection
        for key, value in data.items():
            ref.document(key).set(value)
        return redirect(url_for("success", filename=filename))
    except Exception as e:
        # Log the error
        app.logger.error(f"An error occurred in submit_info route: {str(e)}")
        # Return JSON response with error message
        return jsonify({"error": "An error occurred while processing your request. Please try again later."}), 500


@app.route("/recognize", methods=["GET", "POST"])
def recognize():
    global detection
    ret, frame = video.read()
    if ret:
        # Information to database
        ref = db.collection("Students")
        # Obtain the last studentId number from the database
        student_docs = ref.stream()


        database = {}
        for student_doc in student_docs:
            student_data = student_doc.to_dict()
            studentName = student_data.get("name")
            studentEmbedding = student_data.get("embeddings")
            database[studentName] = studentEmbedding

        detection = match_with_database(frame, database)
    store_detection_in_database(detection)
    return redirect(url_for("select_class"))
def store_detection_in_database(detection):
    # Get the current timestamp
    current_time = datetime.now()
    # Store the detection in the database
    db.collection('detections').add({
        'name': detection,
        'timestamp': current_time
    })

@app.route("/select_class", methods=["GET", "POST"])
def select_class():
    detection = retrieve_latest_detection_from_database()
    if request.method == "POST":
        # Get the selected class and day from the form data
        selected_class = request.form.get("classes")
        day = datetime.now().strftime("%A")
        # Generate the URL of the image
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")  # for browser cache
        url = url_for("static", filename="recognized/recognized.png", v=timestamp)

        ref = db.collection("Students")
        # Retrieve all documents from the collection
        student_docs = ref.stream()

        for student_doc in student_docs:
            student_data = student_doc.to_dict()
            student_name = student_data.get("name")
            if detection == student_name:
                # Check if the selected class is in the list of classes for this student
                if selected_class in student_data.get("classes", []):
                    # Update the attendance in the database
                    ref.document(student_doc.id).update({
                        f"classes.{selected_class}": student_data["classes"][selected_class] + 1, "day": day  # Include the day in the update
                    })
                    # Render the template, passing the detection result and image URL
                    return f'<h2>Selected Class: {selected_class} - {detection}</h2>'
                else:
                    return f'<h2>Student not in class - {detection}</h2>'
        # If the student is not found in the database
        return f'<h2>Student {detection} found in the database</h2>'
    else:
        # Render the select class page
        return render_template("select_class.html")


def retrieve_latest_detection_from_database():
    # Query the database to retrieve the latest detection
    detections_ref = db.collection('detections').order_by('timestamp', direction='DESCENDING').limit(1).get()
    # Extract the detection from the query result
    for detection in detections_ref:
        return detection.to_dict()['name']  # Return the name of the detection
    # Return a default value if no detection is found
    return "No detection found"

def gen_frames():
    global video
    video = cv2.VideoCapture(0)
    while True:
        success, frame = video.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode(".jpg", frame)
            frame = buffer.tobytes()
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")


if __name__ == "__main__":
    app.run(debug=True)
