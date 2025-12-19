"""SMTP bağlantısını test eder ve gerçek mail gönderir"""
from mail_sender import MailSender
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

print("\n" + "="*70)
print("🔍 SMTP DEBUG - GERÇEK MAİL GÖNDERME TESTİ")
print("="*70 + "\n")

try:
    # Mail sender başlat
    print("1. Mail sender başlatılıyor...")
    sender = MailSender()
    print(f"   ✅ {len(sender.mail_accounts)} mail hesabı yüklendi\n")
    
    # Hesapları göster
    print("2. Aktif Mail Hesapları:")
    for i, acc in enumerate(sender.mail_accounts, 1):
        print(f"   {i}. {acc['email']}")
    print()
    
    # SMTP bağlantılarını test et
    print("3. SMTP Bağlantı Testi:")
    results = sender.test_smtp_connections()
    for result in results:
        status_icon = "✅" if result['status'] == 'success' else "❌"
        print(f"   {status_icon} {result['email']}: {result['message']}")
    print()
    
    # Mail gönder
    test_email = "okan49886@gmail.com"
    template = "welcome"
    
    print(f"4. Test Mail Gönderiliyor:")
    print(f"   Alıcı: {test_email}")
    print(f"   Template: {template}")
    print(f"   Gönderiliyor...\n")
    
    success = sender.send_mail(test_email, template, display_name=None)
    
    if success:
        print("\n✅ SMTP send_message() BAŞARILI!")
        print("   Mail gönderildi (teoride)")
        print("\n📬 Şimdi mail kutunu kontrol et:")
        print(f"   {test_email} adresine mail geldi mi?\n")
    else:
        print("\n❌ MAİL GÖNDERİLEMEDİ!")
        print("   Log'lara bak\n")
    
except Exception as e:
    print(f"\n❌ HATA: {str(e)}")
    import traceback
    traceback.print_exc()

print("="*70 + "\n")

