import sqlite3

conn = sqlite3.connect('mail_tracking.db')
cursor = conn.cursor()
cursor.execute('SELECT tracking_id, to_email FROM sent_mails ORDER BY sent_date DESC LIMIT 1')
tracking_id, email = cursor.fetchone()
conn.close()

print(f"\nEmail: {email}")
print(f"Tracking ID: {tracking_id}")
print(f"\nClick URL:")
print(f"https://automailsender-production.up.railway.app/click/{tracking_id}")

