Event Management System
This is a web-based event management system built using Python, Flask, and SQL Server. It provides features for both users and admins, including user registration, event viewing, event registration, and an admin dashboard for event creation, editing, and deletion.

Features
User Features:
User Registration: New users can register with email, username, and password.
User Login: Registered users can log in using their email and password.
Event Viewing: Users can view a list of upcoming events.
Event Registration: Users can register for events, providing details like username, email, and phone number.
Admin Features:
Admin Login: Admin users can log in using their credentials.
Event Management: Admins can create, edit, or delete events.
Export Participants: Admins can export participant data in CSV format.
Security:
Password Hashing: User passwords are hashed using SHA-256 for secure storage.
Session Management: Users and admins are authenticated and their sessions are managed securely.
Technologies Used
Flask: A lightweight web framework used for building the application.
SQL Server: A relational database system for storing user and event data.
pyodbc: A Python library used to connect to the SQL Server database.
HTML/CSS: Used for creating the user interface.
Requirements
Python 3.7 or higher
Flask
pyodbc
SQL Server (or any compatible database with an ODBC driver)
HTML/CSS for frontend templates
Install Dependencies
bash
Copy code
pip install Flask pyodbc pandas
Setup
Database Setup: Ensure that you have SQL Server running and create the following tables in your database (replace Event with your actual database name):
sql
Copy code
URL Routes
/: Home Page
/register: User registration page
/user_login: User login page
/user_dashboard: User dashboard with event listing
/view_events/<int:event_id>: View event details
/register_for_event/<int:event_id>: Register for an event
/admin/login: Admin login page
/admin/dashboard: Admin dashboard with event management
/admin/create_event: Create a new event (admin)
/admin/edit_event/<int:event_id>: Edit an event (admin)
/admin/delete_event/<int:event_id>: Delete an event (admin)
/admin/export_participants: Export event participants in CSV formatFile Structure
plaintext
Copy code
/your_project_directory
    /templates
        index.html
        user_login.html
        register.html
        user_dashboard.html
        registration_form.html
        admin_login.html
        admin_dashboard.html
        create_event.html
        edit_event.html
    /static
        (CSS and JS files, if any)
    app.py
    README.md
Notes
Password Hashing: User passwords are hashed using the SHA-256 algorithm. Ensure that users' passwords are securely stored.
Session Handling: Admin and user sessions are managed using Flask's session object, which uses cookies to track user sessions.
Error Handling: Basic error handling is implemented using Flask's flash() function to show messages to users.
