import sqlite3
from datetime import datetime

def initialize_database(db_name='emails.db'):
    """
    Initialize SQLite database and create the necessary table.
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT NOT NULL,
            subject TEXT,
            timestamp TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


def save_email_to_database(sender, subject, timestamp, db_name='emails.db'):
    """
    Save an email's details into the SQLite database.
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Emails (sender, subject, timestamp)
        VALUES (?, ?, ?)
    ''', (sender, subject, timestamp))
    conn.commit()
    conn.close()


def parse_and_store_emails(emails, db_name='emails.db'):
    """
    Parse emails and store their details into the database.
    """
    for email in emails:
        # Extract email details
        sender = email.get('headers', {}).get('From', 'Unknown Sender')
        subject = email.get('headers', {}).get('Subject', 'No Subject')
        timestamp = email.get('headers', {}).get('Date', 'Unknown Date')
        
        # Convert timestamp to a consistent format
        try:
            timestamp = datetime.strptime(timestamp, "%a, %d %b %Y %H:%M:%S %z").isoformat()
        except Exception:
            pass  # Use raw timestamp if parsing fails
        
        # Save to database
        save_email_to_database(sender, subject, timestamp, db_name)


# Example usage
if __name__ == '__main__':
    # Initialize the database
    initialize_database()

    # Sample data for demonstration purposes
    sample_emails = [
        {
            'headers': {
                'From': 'example1@gmail.com',
                'Subject': 'Test Email 1',
                'Date': 'Tue, 12 Dec 2024 10:00:00 +0000'
            }
        },
        {
            'headers': {
                'From': 'example2@gmail.com',
                'Subject': 'Test Email 2',
                'Date': 'Wed, 13 Dec 2024 12:30:00 +0000'
            }
        }
    ]

    # Parse and store the sample emails
    parse_and_store_emails(sample_emails)

    print("Emails have been saved to the database.")


