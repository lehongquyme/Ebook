import mysql.connector

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Replace with your MySQL password
    'database': 'ebook'
}
def get_db_connection():
    return mysql.connector.connect(**db_config)
def get_db_error():
    return mysql.connector.Error