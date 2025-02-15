import sqlite3

def create_database():
    db = sqlite3.connect('blood_donation.db')
    cursor = db.cursor()

    # Create donors table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS donors (
            donor_id INTEGER PRIMARY KEY AUTOINCREMENT,
            jid TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            blood_group TEXT,
            contact_number TEXT,
            address TEXT,
            registration_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create donations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS donations (
            donation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            donor_id INTEGER,
            donation_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            location TEXT,
            FOREIGN KEY (donor_id) REFERENCES donors(donor_id)
        )
    ''')

    db.commit()
    db.close()
    print("Database created successfully!")

if __name__ == '__main__':
    create_database()