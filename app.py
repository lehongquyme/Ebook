from flask import  jsonify, request, send_from_directory
from controllers.api.api import forgot, get_book, get_students, login, register, update_account
from views.auth_views import admin_blueprint
from app_config import app

app.register_blueprint(admin_blueprint)


@app.route('/uploads/<path:filename>', methods=['GET'])
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/students', methods=['GET'])
def getStudents(): return get_students()

#get all book
@app.route('/getAllBook',methods=['GET'])
def getAllBooks() : return get_book()

@app.route('/loginAccount', methods=['POST'])
def loginStudents():return login()

@app.route('/signUpAccount', methods=['POST'])
def signUp():return register()
    
@app.route('/updateAccount', methods=['PUT'])
def updateAccount():return update_account()

@app.route('/forgotAccount', methods=['POST'])
def forgotStudents():return forgot()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5001)  # Consider removing debug=True in production
