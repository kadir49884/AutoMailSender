#!/usr/bin/env python3
"""Test maili gönder"""

import os
from dotenv import load_dotenv
from mail_sender import MailSender

load_dotenv()

print("="*60)
print("📧 TEST MAİLİ GÖNDERİLİYOR")
print("="*60)
print()

# Railway URL kontrolü
railway_url = os.getenv('RAILWAY_PUBLIC_URL')
print(f"🌐 Railway URL: {railway_url}")
print()

# Mail gönder
sender = MailSender()
test_email = "okan49911@gmail.com"

print(f"📨 Mail gönderiliyor: {test_email}")
print("⏳ Lütfen bekle...")
print()

success = sender.send_mail(test_email, 'welcome', display_name=None)

if success:
    print("="*60)
    print("✅ MAİL GÖNDERİLDİ!")
    print("="*60)
    print()
    print("📱 ŞİMDİ NE YAP:")
    print("1. Gmail'i aç → okan49911@gmail.com")
    print("2. Vidlo mailini bul")
    print("3. 'Install App 📲' butonuna tıkla")
    print("4. ❌ Ngrok AÇILMAYACAK!")
    print("5. ✅ Play Store AÇILACAK!")
    print()
    print("📊 Tıkladıktan sonra stats'a bak:")
    print(f"   {railway_url}/stats")
    print()
    print("="*60)
else:
    print("❌ Mail gönderilemedi!")
    print("SMTP hatası olabilir.")

