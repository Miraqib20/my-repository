import pyodbc
from flask import Flask, render_template, request, redirect, url_for, session, flash
import hashlib
import re
import csv
from io import StringIO
from flask import Response
import pandas as pd

app = Flask(__name__)
app.secret_key = 'secret'

# Database connection function
def get_db_connection():
    conn= pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                          'SERVER=MirAqib\\MSSQLSERVER01;'
                          'DATABASE=Event;'
                          'UID=Aqib;'
                          'PWD=1234')
    return conn

# Home Route
@app.route('/')
def index():
    return render_template('index.html')

# Logout Route
@app.route('/logout')
def logout():
    session.clear()  # Clear all session data
    flash('You have been logged out.', 'info')
    return redirect(url_for('user_login'))  # Redirect to user login page after logout

# User Registration Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Input validation
        if not email or not username or not password:
            flash('All fields are required.', 'danger')
            return redirect(url_for('register'))
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email format.', 'danger')
            return redirect(url_for('register'))
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return redirect(url_for('register'))
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('register'))

        # Hash the password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        role = 'user'

        # Insert user into the database
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (email, username, password, role) VALUES (?, ?, ?, ?)",
                (email, username, hashed_password, role)
            )
            conn.commit()
            conn.close()
            flash('Registration successful!', 'success')
            return redirect(url_for('user_login'))  # Redirect to user login page
        except Exception as e:
            flash('Error during registration. Please try again.', 'danger')
            print(f"Error: {e}")
            return redirect(url_for('register'))
    return render_template('register.html')

# User Login Route
@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        email = request.form['email']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ? AND password = ? AND role = 'user'", (email, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]  # Assuming user_id is in the first column
            session['role'] = user[3]  # Assuming role is in the fourth column
            flash('Login successful!', 'success')
            return redirect(url_for('user_dashboard'))  # Redirect to user dashboard
        else:
            flash('Invalid credentials, please try again', 'danger')

    return render_template('user_login.html')  # Separate login template for users
# View Event Route (added this if you plan to view event details)
@app.route('/view_events/<int:event_id>')
def view_events(event_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch event details based on event_id (use the correct column name 'id')
    cursor.execute("SELECT * FROM Events WHERE id = ?", (event_id,))
    event = cursor.fetchone()

    conn.close()

    if event:
        return render_template('view_events.html', event=event)
    else:
        flash('Event not found', 'danger')
        return redirect(url_for('user_dashboard'))


# User Dashboard Route
@app.route('/user_dashboard')
def user_dashboard():
    if 'user_id' not in session:
        flash('You must be logged in to access the dashboard', 'danger')
        return redirect(url_for('user_login'))  # Redirect to user login page if not logged in

    conn = get_db_connection()
    cursor = conn.cursor()

    # Use the correct column names directly in the SQL query
    cursor.execute("""
        SELECT 
            id, 
            name, 
            description, 
            venue, 
            date, 
            time, 
            registration_limit 
        FROM Events
    """)
    events = cursor.fetchall()

    conn.close()  # Close connection after use
 
    return render_template('user_dashboard.html', events=events)



# Register for Event Route
@app.route('/register_for_event/<int:event_id>', methods=['GET', 'POST'])
def register_for_event(event_id):
    if 'user_id' not in session:
        flash('You must be logged in to register for events.', 'danger')
        return redirect(url_for('user_login'))  # Redirect to user login page if not logged in
    
    user_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch event details to display on the registration page
    cursor.execute("SELECT * FROM Events WHERE id = ?", (event_id,))
    event = cursor.fetchone()

    if not event:
        flash('Event not found.', 'danger')
        return redirect(url_for('user_dashboard'))  # Redirect to the user dashboard if event doesn't exist

    # If form is submitted via POST, handle registration
    if request.method == 'POST':
        # Get the registration details from the form
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']

        # Check if the user is already registered for the event
        cursor.execute("SELECT * FROM Registrations WHERE user_id = ? AND event_id = ?", (user_id, event_id))
        existing_registration = cursor.fetchone()

        if existing_registration:
            flash('You are already registered for this event!', 'info')
        else:
            # Insert the registration into the Registrations table
            cursor.execute("INSERT INTO Registrations (user_id, event_id, username, email, phone) VALUES (?, ?, ?, ?, ?)",
                           (user_id, event_id, username, email, phone))
            conn.commit()
            flash('Registration successful!', 'success')

        return redirect(url_for('user_dashboard'))  # Redirect to the user dashboard after registration

    conn.close()

    # Render the registration form with event details
    return render_template('registration_form.html', event=event)
# Admin Login Route
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        # Use .get() to avoid KeyError if key is missing
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Username and password are required!', 'danger')
            return render_template('admin_login.html')

        # Establish DB connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admins WHERE username = ? AND password = ?", (username, password))
        admin = cursor.fetchone()
        conn.close()

        if admin:
            session['role'] = 'admin'
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('admin_login.html')
@app.route('/admin/create_event', methods=['GET', 'POST'])
def create_event():
    # Check if the user is an admin
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('admin_login'))  # Ensure only admins can access this page

    if request.method == 'POST':
        # Handle the form submission
        event_name = request.form['name']
        event_description = request.form['description']
        event_venue = request.form['venue']
        event_date = request.form['date']
        event_time = request.form['time']
        registration_limit = request.form['registration_limit']

        # Establish a connection to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert the new event into the Events table
        cursor.execute("""
            INSERT INTO Events (name, description, venue, date, time, registration_limit)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (event_name, event_description, event_venue, event_date, event_time, registration_limit))
        conn.commit()

        # Close the database connection
        conn.close()

        # Flash a success message and redirect to the admin dashboard
        flash('Event created successfully!', 'success')
        return redirect(url_for('admin_dashboard'))  # Redirect to dashboard after success

    return render_template('create_event.html')
# Admin Dashboard Route
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'role' not in session or session['role'] != 'admin':
        flash('You must be an admin to access this page.', 'danger')
        return redirect(url_for('admin_login'))

    # Fetch events to display from the database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events")  # Assuming you have an 'events' table
    events = cursor.fetchall()
    conn.close()

    return render_template('admin_dashboard.html', events=events)

# Admin Create Event Route

# Admin Edit Event Route
@app.route('/admin/edit_event/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('admin_login'))  # Redirect to admin login page if not admin
    
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        # Get updated event details from form
        event_name = request.form['event_name']
        event_date = request.form['event_date']
        event_description = request.form['event_description']
        
        # Update event in the database
        cursor.execute("""
        UPDATE events
        SET event_name = ?, event_date = ?, event_description = ?
        WHERE id = ?
        """, (event_name, event_date, event_description, event_id))
        conn.commit()
        conn.close()
        
        flash('Event updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    # Fetch the event details for the form
    cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
    event = cursor.fetchone()
    conn.close()

    return render_template('edit_event.html', event=event)


# Admin Logout Route
@app.route('/admin/logout')
def admin_logout():
    session.pop('role', None)
    session.pop('username', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('admin_login'))

# Admin Delete Event Route
@app.route('/admin/delete_event/<int:event_id>')
def delete_event(event_id):
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('admin_login'))  # Redirect to admin login page if not admin
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
    conn.commit()
    conn.close()
    flash('Event deleted successfully!', 'success')
    
    return redirect(url_for('admin_dashboard'))
@app.route('/admin/export_participants')
def export_participants():
    if 'role' not in session or session['role'] != 'admin':
        flash('You must be an admin to access this page.', 'danger')
        return redirect(url_for('admin_login'))

    # Fetch participant data from the database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM participants")  # Assuming you have a 'participants' table
    participants = cursor.fetchall()
    conn.close()

    # Prepare CSV output
    output = StringIO()
    writer = csv.writer(output)
    
    # Write headers
    writer.writerow([column[0] for column in cursor.description])  # Write column headers

    # Write data
    for participant in participants:
        writer.writerow(participant)

    output.seek(0)

    # Send the CSV file as a response
    return Response(
        output,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=participants.csv'}
    )
if __name__ == '__main__':
    app.run(debug=True)
