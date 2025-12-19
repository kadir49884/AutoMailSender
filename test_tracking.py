"""Son mailin tracking ID'sini bulur ve test eder"""
import sqlite3

conn = sqlite3.connect('mail_tracking.db')
cursor = conn.cursor()

cursor.execute('''
    SELECT tracking_id, to_email, opened, sent_date
    FROM sent_mails 
    WHERE tracking_id IS NOT NULL
    ORDER BY id DESC 
    LIMIT 1
''')

result = cursor.fetchone()

if result:
    tracking_id, to_email, opened, sent_date = result
    
    print("\n" + "="*70)
    print("🔍 SON GÖNDERİLEN MAİL")
    print("="*70)
    print(f"\nAlıcı: {to_email}")
    print(f"Tarih: {sent_date}")
    print(f"Açıldı mı: {'✅ EVET' if opened else '❌ HAYIR'}")
    print(f"\n🔗 TRACKING URL (Ngrok):")
    print(f"https://02d7c633d6ed.ngrok-free.app/track/{tracking_id}")
    print(f"\n💡 BU URL'İ BROWSER'DA AÇ!")
    print(f"   - Boş sayfa göreceksin")
    print(f"   - Flask log'unda 'Mail açıldı: {tracking_id[:30]}...' yazmalı")
    print(f"   - Stats sayfasını yenile")
    print(f"   - Açılma +1 artmalı!")
    print("\n" + "="*70 + "\n")
else:
    print("\n❌ Tracking ID'li mail bulunamadı!\n")

conn.close()

