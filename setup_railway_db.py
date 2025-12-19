"""Railway database'ini hazırlar"""
import os

print("\n" + "="*70)
print("🚀 RAILWAY DATABASE KURULUMU")
print("="*70 + "\n")

# Railway environment variable'ını simüle et
os.environ['DATA_DIR'] = '/data'

# Railway volume yoksa local'de /data oluştur (test için)
if not os.path.exists('data'):
    os.makedirs('data')
    print("✅ data/ klasörü oluşturuldu (Railway /data simülasyonu)\n")

from mail_sender import MailSender

print("1. Mail sender başlatılıyor (Railway mode)...")
sender = MailSender()

print(f"   ✅ Database hazır: {sender.db_path}")
print(f"   ✅ {len(sender.mail_accounts)} mail hesabı yüklendi")
print(f"   ✅ {len(sender.templates)} template yüklendi\n")

# Database yapısını kontrol et
import sqlite3
conn = sqlite3.connect(sender.db_path)
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM sent_mails")
sent_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM blacklist")
blacklist_count = cursor.fetchone()[0]

print("2. Database Durumu:")
print(f"   Gönderilen mailler: {sent_count}")
print(f"   Kara liste: {blacklist_count}")

conn.close()

print("\n" + "="*70)
print("✅ RAILWAY DATABASE HAZIR!")
print("="*70)
print("\n📝 Şimdi yapılacaklar:")
print("   1. Bu database'i Railway'e deploy et")
print("   2. Railway dashboard'dan mail gönder")
print("   3. Tracking otomatik çalışacak!\n")
print("="*70 + "\n")

