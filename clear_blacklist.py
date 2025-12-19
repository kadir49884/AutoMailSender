"""Belirli bir mail adresini kara listeden çıkarır"""
import sqlite3
import sys

db_path = 'mail_tracking.db'

if len(sys.argv) < 2:
    print("\n❌ Kullanım: python clear_blacklist.py <email>")
    print("   VEYA: python clear_blacklist.py ALL (tüm kara listeyi temizle)")
    print("\nÖrnek: python clear_blacklist.py okan49911@gmail.com\n")
    sys.exit(1)

email = sys.argv[1]

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    if email.upper() == 'ALL':
        # Tüm kara listeyi temizle
        cursor.execute("DELETE FROM blacklist")
        conn.commit()
        count = cursor.rowcount
        print(f"\n✅ Tüm kara liste temizlendi! ({count} kayıt silindi)\n")
    else:
        # Belirli mail'i kara listeden çıkar
        cursor.execute("SELECT reason FROM blacklist WHERE email = ?", (email,))
        result = cursor.fetchone()
        
        if result:
            reason = result[0]
            cursor.execute("DELETE FROM blacklist WHERE email = ?", (email,))
            conn.commit()
            print(f"\n✅ Mail kara listeden çıkarıldı!")
            print(f"   Email: {email}")
            print(f"   Sebep: {reason}\n")
        else:
            print(f"\n❌ Bu mail kara listede değil: {email}\n")
    
except Exception as e:
    print(f"\n❌ Hata: {str(e)}\n")
    conn.rollback()
finally:
    conn.close()

