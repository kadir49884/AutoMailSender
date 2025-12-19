"""Direkt mail gönderir - GUI olmadan"""
from mail_sender import MailSender
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

print("\n" + "="*70)
print("📧 DİREKT MAİL GÖNDERME (GUI'siz)")
print("="*70 + "\n")

# Mail bilgileri
TO_EMAIL = "okan49886@gmail.com"
TEMPLATE = "welcome"

try:
    print("1. Mail sender başlatılıyor...")
    sender = MailSender()
    print(f"   ✅ {len(sender.mail_accounts)} mail hesabı hazır\n")
    
    print("2. Mail gönderiliyor...")
    print(f"   Alıcı: {TO_EMAIL}")
    print(f"   Template: {TEMPLATE}\n")
    
    success = sender.send_mail(TO_EMAIL, TEMPLATE, display_name=None)
    
    if success:
        print("\n" + "="*70)
        print("✅ MAİL BAŞARIYLA GÖNDERİLDİ!")
        print("="*70)
        print(f"\n📬 Şimdi {TO_EMAIL} adresini kontrol et:")
        print("   - Gelen Kutusu")
        print("   - SPAM / JUNK Klasörü ⚠️")
        print(f"\nGönderen hesapları kontrol et:")
        for acc in sender.mail_accounts:
            print(f"   - from:{acc['email']}")
        print("\n" + "="*70 + "\n")
    else:
        print("\n" + "="*70)
        print("❌ MAİL GÖNDERİLEMEDİ!")
        print("="*70)
        print("\nLog dosyasını kontrol et: mail_logs.log\n")
    
except Exception as e:
    print(f"\n❌ HATA: {str(e)}")
    import traceback
    traceback.print_exc()
    print()

