import hashlib
class Student:
    def __init__(self, idStudents, nameStudent, email, password, course, yearBirth, specialized, phone, gender,otp,otp_timestamp ,image_path=None):
        self.idStudents = idStudents
        self.nameStudent = nameStudent
        self.email = email
        self.password = password
        self.course = course
        self.yearBirth = yearBirth
        self.specialized = specialized
        self.phone = phone
        self.gender = gender
        self.otp = otp
        self.otp_timestamp = otp_timestamp
        self.image_path = image_path  # Add this line

    def to_dict(self):
        return {
            "idStudents": self.idStudents,
            "name": self.nameStudent,
            "email": self.email,
            "course": self.course,
            "yearBirth": self.yearBirth,
            "specialized": self.specialized,
            "phone": self.phone,
            "gender": self.gender,
            "otp":self.otp,
            "otp_timestamp":self.otp_timestamp,
            "image_path": self.image_path  # Include image_path in the dictionary
        }

    def check_password(self, password):
        return self.password == hashlib.md5(password.encode('utf-8')).hexdigest()