#!/usr/bin/env python3
"""Hybrid sistem testi: Local mail gönder, Railway tracking"""

import os
from dotenv import load_dotenv
from mail_sender import MailSender

# .env yükle
load_dotenv()

def test():
    print("="*60)
    print("🧪 HYBRİD SİSTEM TESTİ")
    print("="*60)
    print()
    
    # Railway URL kontrolü
    railway_url = os.getenv('RAILWAY_PUBLIC_URL', '')
    print(f"🌐 Railway URL: {railway_url}")
    
    if 'ngrok' in railway_url.lower():
        print("❌ UYARI: Hala Ngrok URL'i var!")
        print("✏️ .env dosyasında RAILWAY_PUBLIC_URL'i şuna değiştir:")
        print("   RAILWAY_PUBLIC_URL=https://automailsender-production.up.railway.app")
        return
    
    if not railway_url or 'railway' not in railway_url.lower():
        print("❌ HATA: Railway URL bulunamadı!")
        print("✏️ .env dosyasına ekle:")
        print("   RAILWAY_PUBLIC_URL=https://automailsender-production.up.railway.app")
        return
    
    print("✅ Railway URL doğru!\n")
    
    # Mail gönder
    sender = MailSender()
    test_email = input("📧 Test mail adresi gir (örn: okan49911@gmail.com): ").strip()
    
    if not test_email:
        print("❌ Mail adresi girilmedi!")
        return
    
    print(f"\n📨 Mail gönderiliyor: {test_email}")
    print("⏳ Lütfen bekle...")
    
    success = sender.send_mail(test_email, 'welcome', display_name=None)
    
    if success:
        print("\n" + "="*60)
        print("✅ MAİL GÖNDERİLDİ!")
        print("="*60)
        print()
        print("📱 ŞİMDİ NE YAP:")
        print("1. Gmail'i aç ve maili bul")
        print("2. 'Install App 📲' butonuna tıkla")
        print("3. Play Store açılacak (Ngrok açılmayacak!)")
        print("4. Stats'ı kontrol et:")
        print(f"   {railway_url}/stats")
        print()
        print("⏰ Stats güncellemesi 1-2 saniye içinde görünecek!")
        print("="*60)
    else:
        print("\n❌ Mail gönderilemedi!")
        print("💡 SMTP bağlantılarını kontrol et:")
        print("   python mail_gui.py → Mail Bağlantısı Test Et")

if __name__ == '__main__':
    test()

