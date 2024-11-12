from database.db import get_db_connection

def login_user(email, hashed_password):
    if not email or not hashed_password:
        return {"success": False, "message": "Email and password are required."}

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)  # Use dictionary cursor for better readability
        
        # Fetch user based on email
        cursor.execute("SELECT * FROM Students WHERE email = %s", (email,))
        admin = cursor.fetchone()
        if admin:
            # Assuming you have stored hashed passwords
            if admin['password'] == hashed_password:
                return {"success": True, "message": "Login successful!"}
            else:
                return {"success": False, "message": "Invalid credentials."}
        else:
            return {"success": False, "message": "Admin not found."}

    except Exception as err:
        return {'success': False, 'message': 'An error occurred while logging in. Please try again.'}
    finally:
        cursor.close()
        connection.close()
