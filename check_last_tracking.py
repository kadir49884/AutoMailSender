"""Son mailin tracking ID'sini bulur"""
import sqlite3

conn = sqlite3.connect('mail_tracking.db')
cursor = conn.cursor()

cursor.execute('''
    SELECT tracking_id, to_email, clicked, opened
    FROM sent_mails 
    WHERE tracking_id IS NOT NULL
    ORDER BY id DESC 
    LIMIT 1
''')

result = cursor.fetchone()

if result:
    tracking_id, to_email, clicked, opened = result
    
    print("\n" + "="*70)
    print("🔍 SON MAİL")
    print("="*70)
    print(f"\nAlıcı: {to_email}")
    print(f"Açıldı: {'✅' if opened else '❌'}")
    print(f"Tıklandı: {'✅' if clicked else '❌'}")
    
    print(f"\n🔗 MANUEL TEST URL'LERİ:")
    print(f"\nClick (Railway):")
    print(f"https://automailsender-production.up.railway.app/click/{tracking_id}")
    
    print(f"\n💡 Bu URL'i browser'da aç:")
    print(f"   - Play Store'a gideceksin")
    print(f"   - Railway stats'a bak:")
    print(f"   https://automailsender-production.up.railway.app/stats")
    print(f"   - Click sayısı artacak!")
    
    print("\n" + "="*70 + "\n")
else:
    print("\n❌ Mail bulunamadı!\n")

conn.close()

