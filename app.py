from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, make_response
import sqlite3
import os
import random
import string
import io
import openpyxl
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)  

DATABASE = os.path.join(app.root_path, 'blood_donation.db')


def get_db():
    db = sqlite3.connect(DATABASE)
    return db


def create_database():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()

        # Create donors table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS donors (
                donor_id INTEGER PRIMARY KEY AUTOINCREMENT,
                jid TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                contact_number TEXT,
                address TEXT,
                location TEXT,
                registration_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS donations (
                donation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                donor_id INTEGER,
                donation_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                location TEXT,
                FOREIGN KEY (donor_id) REFERENCES donors(donor_id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS timer (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_date TIMESTAMP NOT NULL
            )
        ''')

        db.commit()
        db.close()
        print("Database created/checked successfully!")


def generate_unique_jid():
    """Generates a unique JID in the format "JMI-###" where ### is a 3-digit number."""
    db = get_db()
    try:
        cursor = db.cursor()
        cursor.execute("SELECT MAX(CAST(SUBSTR(jid, 4) AS INTEGER)) FROM donors WHERE jid LIKE 'JMI-%'") 
        last_jid_number = cursor.fetchone()[0]
        if last_jid_number is None:
            last_jid_number = 99 
        next_jid_number = last_jid_number + 1
        jid = f"JMI-{next_jid_number:03d}"  

       
        return jid

    except Exception as e:
        print(f"Error generating JID: {e}")
        db.rollback()
        return None  
    finally:
        db.close()


def get_timer_date():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT event_date FROM timer ORDER BY id DESC LIMIT 1")
    result = cursor.fetchone()
    db.close()
    return result[0] if result else "0000-00-00T00:00:00"  


@app.context_processor
def inject_get_timer_date():
    return dict(get_timer_date=get_timer_date)


@app.route('/')
def index():
    db = get_db()
    registration_count = db.execute("SELECT COUNT(*) FROM donors").fetchone()[0]
    donation_count = db.execute("SELECT COUNT(*) FROM donations").fetchone()[0]
    db.close()
    is_logged_in = session.get('is_logged_in', False)  # Check login status
    return render_template('index.html', registration_count=registration_count, donation_count=donation_count, is_logged_in=is_logged_in)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if not session.get('is_logged_in'):  ####!important Protect route: Only logged-in users can access
        return redirect(url_for('admin'))

    if request.method == 'POST':
        name = request.form['name']
        jid = generate_unique_jid()
        db = get_db()
        try:
            db.execute("INSERT INTO donors (jid, name) VALUES (?, ?)", (jid, name))
            db.commit()
            flash(f"Registration successful! Your JID is: {jid}", 'success')
            return redirect(url_for('register'))
        except sqlite3.IntegrityError:
            flash("Error: JID already exists. Please try again.", 'error')
            return render_template('register.html')
        finally:
            db.close()
    return render_template('register.html')

@app.route('/validate', methods=['GET', 'POST'])
def validate():
    if not session.get('is_logged_in'):  
        return redirect(url_for('admin'))

    if request.method == 'POST':
        jid = request.form['jid']
        mobile = request.form.get('mobile')
        address = request.form.get('address')
        name = request.form.get('name')

        db = get_db()
        donor = db.execute("SELECT donor_id, name FROM donors WHERE jid=?", (jid,)).fetchone()
        if donor:
            donor_id = donor[0]
            if name:
                db.execute("UPDATE donors SET name = ? WHERE jid = ?", (name, jid))
            if mobile:
                db.execute("UPDATE donors SET contact_number = ? WHERE jid = ?", (mobile, jid))
            if address:
                db.execute("UPDATE donors SET address = ? WHERE jid = ?", (address, jid))
            db.execute("INSERT INTO donations (donor_id, location) VALUES (?, ?)", (donor_id, request.form['location']))
            db.commit()
            flash("Donation recorded successfully!", 'success')
            return redirect(url_for('validate'))
        else:
            flash("Invalid JID.", 'error')
        db.close()
    return render_template('validate.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        #################valid users
        valid_users = [
            {'username': 'director_jmieti', 'password': 'password:@234'},
            {'username': 'admin1', 'password': 'admin123'},
            {'username': 'admin2', 'password': 'admin456'},
            {'username': 'admin3', 'password': 'admin789'}
        ]

        for user in valid_users:
            if username == user['username'] and password == user['password']:
                session['is_logged_in'] = True
                db = get_db()
                registration_count = db.execute("SELECT COUNT(*) FROM donors").fetchone()[0]
                donation_count = db.execute("SELECT COUNT(*) FROM donations").fetchone()[0]
                db.close()
                return redirect(url_for('admin'))

        flash("Invalid credentials.", 'error')
        return render_template('admin.html')

    return render_template('admin.html')


@app.route('/logout')
def logout():
    session.pop('is_logged_in', None)  
    return redirect(url_for('index'))

# Route to set the timer for the next blood donation camp
# @app.route('/set_timer', methods=['GET', 'POST'])
# def set_timer():
#     if not session.get('is_logged_in'):  # Protect route: Only logged-in users can access
#         return redirect(url_for('admin'))

#     if request.method == 'POST':
#         event_date = request.form['event_date']
#         db = get_db()
#         try:
#             # Clear previous timer entry
#             db.execute("DELETE FROM timer")
#             # Insert new timer entry
#             db.execute("INSERT INTO timer (event_date) VALUES (?)", (event_date,))
#             db.commit()
#             flash("Timer set successfully!", 'success')
#         except Exception as e:
#             flash(f"Error: {str(e)}", 'error')
#         finally:
#             db.close()
#         return redirect(url_for('set_timer'))
#     return render_template('set_timer.html')

#####Route to download donors list as Excel
@app.route('/download_donors_excel')
def download_donors_excel():
    if not session.get('is_logged_in'):  # Protect route
        return redirect(url_for('admin'))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT jid, name, contact_number, address, registration_timestamp FROM donors")
    donors = cursor.fetchall()
    db.close()

    #############Create Excel workbook in memory
    output = io.BytesIO()
    workbook = openpyxl.Workbook()
    sheet = workbook.active

    #################Write header row
    sheet.append(["JID", "Name", "Contact Number", "Address", "Registration Timestamp"])

    ##############rite data rows
    for donor in donors:
        sheet.append(donor)

    ##############Save workbook to BytesIO stream
    workbook.save(output)
    output.seek(0)

    ############# Create Flask response
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=donors.xlsx"
    response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return response

############### Route to get updated registration and donation counts
@app.route('/get_updated_data')
def get_updated_data():
    db = get_db()
    registration_count = db.execute("SELECT COUNT(*) FROM donors").fetchone()[0]
    donation_count = db.execute("SELECT COUNT(*) FROM donations").fetchone()[0]
    db.close()
    return jsonify({'registration_count': registration_count, 'donation_count': donation_count})

@app.route('/set_timer', methods=['GET', 'POST'])
def set_timer():
    if not session.get('is_logged_in'):  
        return redirect(url_for('admin'))

    db = get_db()
    cursor = db.cursor()

    ################Fetch the latest event date from the database
    cursor.execute("SELECT event_date FROM timer ORDER BY id DESC LIMIT 1")
    latest_event_date = cursor.fetchone()
    latest_event_date = latest_event_date[0] if latest_event_date else None

    if request.method == 'POST':
        event_date = request.form['event_date']  # Get the event date from the form
        try:
            ##########Clear previous timer entry
            db.execute("DELETE FROM timer")
            #########3Insert new timer entry
            db.execute("INSERT INTO timer (event_date) VALUES (?)", (event_date,))
            db.commit()
            flash("Timer set successfully!", 'success')
            #########Update the latest event date after setting a new one
            latest_event_date = event_date
        except Exception as e:
            flash(f"Error: {str(e)}", 'error')
        finally:
            db.close()
        return redirect(url_for('set_timer'))

    db.close()
    return render_template('set_timer.html', latest_event_date=latest_event_date)

if __name__ == '__main__':
    create_database()
    app.run(debug=True, host='0.0.0.0', port=5000)