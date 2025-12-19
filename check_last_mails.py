"""Son gönderilen mailleri kontrol eder"""
import sqlite3

conn = sqlite3.connect('mail_tracking.db')
cursor = conn.cursor()

cursor.execute('''
    SELECT to_email, from_email, template_name, sent_date, tracking_id 
    FROM sent_mails 
    ORDER BY id DESC 
    LIMIT 5
''')

results = cursor.fetchall()

print("\n" + "="*70)
print("📧 SON 5 GÖNDERİLEN MAİL")
print("="*70 + "\n")

for i, (to_email, from_email, template, sent_date, tracking_id) in enumerate(results, 1):
    print(f"{i}. {to_email}")
    print(f"   Gönderen: {from_email}")
    print(f"   Template: {template}")
    print(f"   Tarih: {sent_date}")
    print(f"   Tracking ID: {tracking_id[:30] if tracking_id else 'YOK'}...")
    print()

conn.close()

