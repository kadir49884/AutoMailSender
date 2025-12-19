"""Click tracking test"""
from mail_sender import MailSender

TO_EMAIL = "okan49911@gmail.com"
TEMPLATE = "welcome"

print("\n🚀 CLICK TRACKING TEST\n")

sender = MailSender()
success = sender.send_mail(TO_EMAIL, TEMPLATE)

if success:
    print("✅ Mail gönderildi!")
    print(f"📬 {TO_EMAIL} adresini aç")
    print("🎯 Button'a tıkla")
    print("📊 Stats sayfasını yenile: http://localhost:5000/stats")
    print("✅ Click rate artacak!\n")
else:
    print("❌ Mail gönderilemedi!\n")

