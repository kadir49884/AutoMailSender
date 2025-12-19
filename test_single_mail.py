"""Tekli mail göndermeyi test eder"""
from mail_sender import MailSender

print("\n" + "="*70)
print("🧪 TEKLİ MAİL GÖNDERME TESTİ")
print("="*70 + "\n")

try:
    # Mail sender başlat
    print("1. Mail sender başlatılıyor...")
    sender = MailSender()
    print("   ✅ Mail sender başarıyla başlatıldı\n")
    
    # Test mail adresi
    test_email = "okan49911@gmail.com"
    template_name = "welcome"
    
    print(f"2. Test mail gönderiliyor:")
    print(f"   Mail: {test_email}")
    print(f"   Template: {template_name}\n")
    
    # Kara liste kontrolü
    blacklist_reason = sender.is_blacklisted(test_email)
    if blacklist_reason:
        print(f"   ❌ Mail kara listede!")
        print(f"   Sebep: {blacklist_reason}\n")
    else:
        print(f"   ✅ Mail kara listede değil\n")
    
    # Mail gönder
    print("3. Mail gönderiliyor...\n")
    success = sender.send_mail(test_email, template_name, display_name=None)
    
    if success:
        print("\n✅ MAİL BAŞARIYLA GÖNDERİLDİ!")
    else:
        print("\n❌ MAİL GÖNDERİLEMEDİ!")
        print("   Log dosyasını kontrol et: mail_logs.log")
    
except Exception as e:
    print(f"\n❌ HATA: {str(e)}")
    import traceback
    print("\nDetaylı Hata:")
    traceback.print_exc()

print("\n" + "="*70 + "\n")

