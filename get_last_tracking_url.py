"""Son gönderilen mailin tracking URL'ini gösterir"""
import sqlite3

conn = sqlite3.connect('mail_tracking.db')
cursor = conn.cursor()

cursor.execute('''
    SELECT to_email, from_email, tracking_id, sent_date, opened
    FROM sent_mails 
    WHERE tracking_id IS NOT NULL
    ORDER BY id DESC 
    LIMIT 1
''')

result = cursor.fetchone()

if result:
    to_email, from_email, tracking_id, sent_date, opened = result
    
    print("\n" + "="*70)
    print("📧 SON GÖNDERİLEN MAİL (Tracking ID'li)")
    print("="*70)
    print(f"\nAlıcı: {to_email}")
    print(f"Gönderen: {from_email}")
    print(f"Tarih: {sent_date}")
    print(f"Açıldı mı: {'✅ EVET' if opened else '❌ HAYIR'}")
    print(f"\n🔗 TRACKING URL:")
    print(f"https://automailsender-production.up.railway.app/track/{tracking_id}")
    print(f"\n💡 Bu URL'i browser'da aç:")
    print(f"   - Boş sayfa göreceksin (1x1 pixel)")
    print(f"   - Stats sayfasını yenile")
    print(f"   - Açılma sayısı +1 artmalı!")
    print("\n" + "="*70 + "\n")
else:
    print("\n❌ Tracking ID'li mail bulunamadı!\n")

conn.close()

