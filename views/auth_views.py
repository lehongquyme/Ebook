from datetime import datetime
import json
import logging
from flask import Blueprint, request, render_template, redirect, url_for, flash
from controllers.routes.auth_controller import login_user  # Import login controller function
from hashlib import md5
from database.db import get_db_connection

admin_blueprint = Blueprint('admin', __name__)

@admin_blueprint.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Handle admin login."""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = md5(password.encode()).hexdigest()  # Hash the password before sending
        response = login_user(email, hashed_password)
        
        if response.get('success'):
            flash('Login successful!', 'success')  
            return redirect(url_for('admin.home'))
        else:
            flash(response.get('message'), 'danger')
    return render_template('login/login.html')

@admin_blueprint.route('/admin/home')
def home():
    proposal_books = []
    rankings_books = []
    new_books = []
    visit_count_mobile = 0  
    visit_count_desktop = 0  
    visit_count_tablet = 0  

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Determine device type and device name based on user agent
        user_agent = request.user_agent.string.lower()
        device_type = 'desktop'  # Default to desktop
        device_name = 'Unknown'

        if 'iphone' in user_agent:
            device_type = 'mobile'
            device_name = f"iPhone {user_agent}"
        elif 'android' in user_agent:
            device_type = 'mobile'
            device_name = f"Android {user_agent}"
        elif 'ipad' in user_agent or 'tablet' in user_agent:
            device_type = 'tablet'
            device_name = f"iPad {user_agent}" if 'ipad' in user_agent else f"Tablet {user_agent}"
        elif 'macintosh' in user_agent or 'windows' in user_agent:
            device_type = 'desktop'
            device_name = f"Mac {user_agent}" if 'macintosh' in user_agent else f"Windows {user_agent}"

        print(f"Device type: {device_type}, Device name: {device_name}")

        # Fetch the current visit count and device name list for the device type
        cursor.execute("SELECT visit_count, device_name_list FROM SiteVisits WHERE device_type = %s;", (device_type,))
        result = cursor.fetchone()

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        entry = f"{device_name},{timestamp}"

        if result:
            # Update visit count
            visit_count = result['visit_count'] + 1
            device_name_list = json.loads(result['device_name_list']) if result['device_name_list'] else []

            # Add new visit entry to the device_name_list
            device_name_list.append(entry)

            cursor.execute(
                "UPDATE SiteVisits SET visit_count = %s, device_name_list = %s WHERE device_type = %s;",
                (visit_count, json.dumps(device_name_list), device_type)
            )
        else:
            # No previous entry for this device type, insert a new one
            cursor.execute(
                "INSERT INTO SiteVisits (visit_count, device_type, device_name_list) VALUES (1, %s, %s);",
                (device_type, json.dumps([entry]))
            )
            visit_count = 1

        conn.commit()  # Commit changes to the database

        # Fetch visit counts and device name lists for each device type
        cursor.execute("SELECT device_type, visit_count, device_name_list FROM SiteVisits;")
        device_counts = cursor.fetchall()

        for record in device_counts:
            if record['device_type'] == 'mobile':
                visit_count_mobile = record['visit_count']
            elif record['device_type'] == 'tablet':
                visit_count_tablet = record['visit_count']
            elif record['device_type'] == 'desktop':
                visit_count_desktop = record['visit_count']

        # Fetch proposed books
        cursor.execute("SELECT * FROM Books LIMIT 3;")
        proposal_books = cursor.fetchall()

        # Fetch top-ranked books based on borrow count
        cursor.execute("""
            SELECT 
                b.idBook,
                b.namebook,
                b.author,
                b.publisher,
                b.publicationyear,
                b.genre,
                b.description,
                b.image,
                COUNT(bd.idBook) AS borrow_count
            FROM Books b
            LEFT JOIN BorrowDetails bd ON b.idBook = bd.idBook
            GROUP BY b.idBook
            ORDER BY borrow_count DESC
            LIMIT 3;
        """)
        rankings_books = cursor.fetchall()

        # Fetch new books
        cursor.execute("SELECT * FROM Books ORDER BY publicationyear DESC LIMIT 3;")
        new_books = cursor.fetchall()

    except Exception as err:
        flash(f"Error loading books: {err}", "danger")
        logging.error(f"Error loading books: {err}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    # Calculate the total visit count from all devices
    total_visit_count = visit_count_mobile + visit_count_desktop + visit_count_tablet

    # Render the template with the fetched data and total visit count
    return render_template(
        'home/home.html',
        proposal_books=proposal_books,
        rankings_books=rankings_books,
        new_books=new_books,
        visit_count=total_visit_count
    )


@admin_blueprint.route('/admin/book/<int:book_id>')
def book_detail(book_id):
    """Fetches and displays book details based on book ID."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Execute query safely to prevent SQL injection
        cursor.execute("SELECT * FROM Books WHERE idBook = %s", (book_id,))
        book = cursor.fetchone()

        # Fetch chapters or any other related data for pagination
        cursor.execute("SELECT * FROM Chapters WHERE idBook = %s", (book_id,))
        chapters = cursor.fetchall()

        # Pagination logic for chapters (if needed)
        current_page = int(request.args.get('page', 1))  # Default to page 1 if not provided
          # Define the number of chapters to show per page
        total_chapters = len(chapters)
        total_pages = (total_chapters //1) + (1 if total_chapters % 1 > 0 else 0)

        # Slice the chapters list for pagination
        start = (current_page - 1) 
        end = start + 1
        chapters_paginated = chapters[start:end]

    except Exception as e:
        # Log the error message for debugging purposes
        print(f"Error retrieving book details: {e}")
        flash("Error retrieving book details.", "danger")
        book = None
        chapters_paginated = []

    finally:
        # Ensure that the database cursor and connection are properly closed
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
    # If no book is found, show a flash message and redirect to the admin home page
    if not book:
        flash("Sách không tồn tại", "danger")
        return redirect(url_for('admin.home'))
    
    # Render the book details template with book, chapters, pagination info
    return render_template('book/bookdetail.html', 
                           book=book, 
                           chapters=chapters_paginated,
                           current_page=current_page,
                           total_pages=total_pages)