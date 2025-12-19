"""Kara listeyi kontrol eder"""
import sqlite3
import sys

db_path = 'mail_tracking.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("\n" + "="*70)
print("📛 KARA LİSTE DURUMU")
print("="*70)

# Kara listedeki tüm mailler
cursor.execute("SELECT email, reason, added_date FROM blacklist ORDER BY added_date DESC")
results = cursor.fetchall()

if results:
    print(f"\n❌ Kara listede {len(results)} mail var:\n")
    for i, (email, reason, date) in enumerate(results, 1):
        print(f"{i}. {email}")
        print(f"   Sebep: {reason}")
        print(f"   Tarih: {date}\n")
else:
    print("\n✅ Kara liste boş!\n")

print("="*70 + "\n")

conn.close()

