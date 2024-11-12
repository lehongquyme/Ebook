from flask import Flask
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['IMAGE_URL'] = 'https://e0d2-2405-4802-461c-c550-a5c0-8423-f9a9-b6cf.ngrok-free.app/uploads/'
app.secret_key = '1234567890'  # Replace with a strong random key

# Create the upload folder if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
