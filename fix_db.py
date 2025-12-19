"""mail_tracking.db database'ine tracking kolonlarını ekler"""
import sqlite3
import os

db_path = 'mail_tracking.db'

if not os.path.exists(db_path):
    print(f"❌ {db_path} bulunamadı!")
    exit(1)

print(f"\n🔄 {db_path} güncelleniyor...\n")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Mevcut kolonları kontrol et
    cursor.execute("PRAGMA table_info(sent_mails)")
    columns = [row[1] for row in cursor.fetchall()]
    
    print(f"📋 Mevcut kolonlar: {columns}\n")
    
    # tracking_id kolonu yoksa ekle
    if 'tracking_id' not in columns:
        print("➕ tracking_id kolonu ekleniyor...")
        cursor.execute("ALTER TABLE sent_mails ADD COLUMN tracking_id TEXT")
        conn.commit()
        print("✅ tracking_id eklendi!")
    else:
        print("✓ tracking_id zaten var")
    
    # opened kolonu yoksa ekle
    if 'opened' not in columns:
        print("➕ opened kolonu ekleniyor...")
        cursor.execute("ALTER TABLE sent_mails ADD COLUMN opened INTEGER DEFAULT 0")
        conn.commit()
        print("✅ opened eklendi!")
    else:
        print("✓ opened zaten var")
    
    # opened_date kolonu yoksa ekle
    if 'opened_date' not in columns:
        print("➕ opened_date kolonu ekleniyor...")
        cursor.execute("ALTER TABLE sent_mails ADD COLUMN opened_date TIMESTAMP")
        conn.commit()
        print("✅ opened_date eklendi!")
    else:
        print("✓ opened_date zaten var")
    
    # Güncellenmiş kolonları göster
    cursor.execute("PRAGMA table_info(sent_mails)")
    new_columns = [row[1] for row in cursor.fetchall()]
    
    print(f"\n📋 Güncellenmiş kolonlar: {new_columns}")
    
    # İstatistikler
    cursor.execute("SELECT COUNT(*) FROM sent_mails")
    total = cursor.fetchone()[0]
    
    print(f"\n📊 Toplam kayıt: {total}")
    print("\n🎉 Database başarıyla güncellendi!")
    print("\nŞimdi Flask'ı yeniden başlat ve /stats sayfasını yenile!")
    
except Exception as e:
    print(f"❌ Hata: {str(e)}")
    conn.rollback()
finally:
    conn.close()

