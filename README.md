Blood Donation Management System

Introduction

The Blood Donation Management System is a Flask-based web application designed to manage donor registrations, record blood donations, and provide administrative functionalities. It enables real-time tracking of donations and allows administrators to manage the database efficiently.

Features

User Registration: Donors can be registered with a unique JID.

Donation Tracking: Maintain records of blood donations linked to registered donors.

Admin Authentication: Secure login for administrators to manage registrations and donations.

Excel Export: Download donor details as an Excel file.

Session Management: Protects routes using session-based authentication.

Database Management: Uses SQLite for persistent data storage.

Event Timer: Stores and retrieves the next blood donation camp date.

Technologies Used

Backend: Python, Flask, SQLite

Frontend: HTML, CSS, Jinja2 Templates

Libraries:

Flask (for web framework)

SQLite3 (for database management)

Openpyxl (for Excel file generation)

Jinja2 (for dynamic templating)

Session & Authentication Management

Installation

Prerequisites

Python 3.x installed



Access the home page: Displays registration and donation statistics.

Admin Login: Authenticate using predefined credentials to manage donor data.

Register a Donor: Input donor details and generate a unique JID.

Validate & Record Donations: Update donor details and log donations.

Download Donor List: Export all donor data to an Excel file.

Additional admin users can be added in the admin route of app.py.

API Endpoints

Endpoint

Method

Description

/

GET

Home page with statistics

/register

GET, POST

Register new donors

/validate

GET, POST

Validate donors and record donations

/admin

GET, POST

Admin login page

/logout

GET

Logout admin session

/download_donors_excel

GET

Download donors list as an Excel file

/get_updated_data

GET

Fetch latest registration & donation counts

Security & Best Practices

Session Management: User authentication with session-based protection.

Database Security: Proper input validation to prevent SQL injection.

Environment Variables: Store sensitive credentials in a .env file.

Future Enhancements

Implement user roles with different levels of access.

Add email and SMS notifications for registered donors.

Develop a mobile-friendly UI.

Enhance search and filtering functionalities for donor records.

This project is licensed under the MIT License - see the LICENSE file for details.

