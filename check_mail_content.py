"""Mail içeriğini kontrol eder - tracking pixel var mı?"""
from mail_sender import MailSender
import os

sender = MailSender()

# Test mail içeriği oluştur
template = sender.templates['welcome']
tracking_id = "TEST-ID-12345"
display_name = "Test User"

# HTML içeriği hazırla
html_content = sender.html_template.format(
    title=template['title'].format(display_name=display_name),
    content="\n".join(template['content']),
    action_title=template['action_title'],
    action_text="\n".join(template['action_text']),
    button_text=template['button_text']
)

# Tracking pixel ekle
tracking_url = os.getenv('RAILWAY_PUBLIC_URL', 'http://localhost:5000')
tracking_pixel = f'<img src="{tracking_url}/track/{tracking_id}" width="1" height="1" style="display:none;" />'
html_content = html_content.replace('</body>', f'{tracking_pixel}</body>')

print("\n" + "="*70)
print("📧 MAİL İÇERİĞİ KONTROLÜ")
print("="*70 + "\n")

print(f"🔗 Tracking URL: {tracking_url}")
print(f"🆔 Tracking ID: {tracking_id}\n")

if tracking_url in html_content and tracking_id in html_content:
    print("✅ TRACKING PIXEL MAİL İÇİNDE VAR!")
    
    # Pixel'i bul ve göster
    start_idx = html_content.find('<img src="' + tracking_url)
    end_idx = html_content.find('/>', start_idx) + 2
    pixel_html = html_content[start_idx:end_idx]
    
    print(f"\n📌 Pixel HTML:")
    print(pixel_html)
    print()
else:
    print("❌ TRACKING PIXEL MAİL İÇİNDE YOK!")
    print("   send_mail() fonksiyonunda sorun var!\n")

# Mail'i dosyaya kaydet
with open('test_mail_preview.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("💾 Mail içeriği kaydedildi: test_mail_preview.html")
print("   Bu dosyayı browser'da aç ve 'View Source' ile tracking pixel'i kontrol et!")
print("\n" + "="*70 + "\n")

