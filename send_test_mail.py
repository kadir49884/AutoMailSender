from mail_sender import MailSender
import os
import webbrowser

def show_all_users():
    sender = MailSender()
    users = sender.get_firebase_users()
    
    print("\nTüm Kullanıcılar:")
    print("-" * 70)
    for i, user in enumerate(users, 1):
        print(f"{i}. Email: {user['email']}")
        print(f"   Display Name: {user.get('display_name', 'Yok')}")
        print("-" * 70)
    print(f"\nToplam {len(users)} kullanıcı bulundu.")

def show_sent_users():
    sender = MailSender()
    all_users = sender.get_firebase_users()
    unsent_users = sender.get_unsent_firebase_users()
    sent_users = [u for u in all_users if u['email'] not in [un['email'] for un in unsent_users]]
    
    print("\nMail Gönderilen Kullanıcılar:")
    print("-" * 70)
    for i, user in enumerate(sent_users, 1):
        print(f"{i}. Email: {user['email']}")
        print(f"   Display Name: {user.get('display_name', 'Yok')}")
        print("-" * 70)
    print(f"\nToplam {len(sent_users)} kullanıcıya mail gönderilmiş.")

def show_unsent_users():
    sender = MailSender()
    template_names = sender.get_template_names()
    
    print("\nKullanılabilir Şablonlar:")
    print("-" * 35)
    for i, name in enumerate(template_names, 1):
        print(f"{i}. {name}")
    print("-" * 35)
    
    while True:
        try:
            choice = int(input("\nŞablon seçin (1-{}): ".format(len(template_names))))
            if 1 <= choice <= len(template_names):
                template_name = template_names[choice-1]
                break
            else:
                print("❌ Geçersiz seçim!")
        except ValueError:
            print("❌ Lütfen bir sayı girin!")
    
    unsent_users = sender.get_unsent_firebase_users(template_name)
    
    print(f"\n{template_name} şablonu için gönderilmeyen kullanıcılar:")
    print("-" * 70)
    for i, user in enumerate(unsent_users, 1):
        print(f"{i}. Email: {user['email']}")
        print(f"   Display Name: {user.get('display_name', 'Yok')}")
        print("-" * 70)
    print(f"\nToplam {len(unsent_users)} kullanıcıya mail gönderilmemiş.")

def send_to_unsent():
    sender = MailSender()
    template_names = sender.get_template_names()
    
    print("\nKullanılabilir Şablonlar:")
    print("-" * 35)
    for i, name in enumerate(template_names, 1):
        print(f"{i}. {name}")
    print("-" * 35)
    
    while True:
        try:
            choice = int(input("\nŞablon seçin (1-{}): ".format(len(template_names))))
            if 1 <= choice <= len(template_names):
                template_name = template_names[choice-1]
                break
            else:
                print("❌ Geçersiz seçim!")
        except ValueError:
            print("❌ Lütfen bir sayı girin!")
    
    unsent_users = sender.get_unsent_firebase_users(template_name)
    success_count = 0
    
    for user in unsent_users:
        if sender.send_mail(user['email'], template_name, user.get('display_name')):
            sender.mark_as_sent(user['email'], template_name, user.get('display_name'))
            success_count += 1
    
    print(f"\n✅ {success_count}/{len(unsent_users)} kullanıcıya {template_name} maili başarıyla gönderildi!")

def send_to_all():
    sender = MailSender()
    template_names = sender.get_template_names()
    
    print("\nKullanılabilir Şablonlar:")
    print("-" * 35)
    for i, name in enumerate(template_names, 1):
        print(f"{i}. {name}")
    print("-" * 35)
    
    while True:
        try:
            choice = int(input("\nŞablon seçin (1-{}): ".format(len(template_names))))
            if 1 <= choice <= len(template_names):
                template_name = template_names[choice-1]
                break
            else:
                print("❌ Geçersiz seçim!")
        except ValueError:
            print("❌ Lütfen bir sayı girin!")
    
    all_users = sender.get_firebase_users()
    success_count = 0
    
    for user in all_users:
        if sender.send_mail(user['email'], template_name, user.get('display_name')):
            sender.mark_as_sent(user['email'], template_name, user.get('display_name'))
            success_count += 1
    
    print(f"\n✅ {success_count}/{len(all_users)} kullanıcıya {template_name} maili başarıyla gönderildi!")

def preview_mail():
    sender = MailSender()
    template_names = sender.get_template_names()
    
    print("\nKullanılabilir Şablonlar:")
    print("-" * 35)
    for i, name in enumerate(template_names, 1):
        print(f"{i}. {name}")
    print("-" * 35)
    
    while True:
        try:
            choice = int(input("\nŞablon seçin (1-{}): ".format(len(template_names))))
            if 1 <= choice <= len(template_names):
                template_name = template_names[choice-1]
                break
            else:
                print("❌ Geçersiz seçim!")
        except ValueError:
            print("❌ Lütfen bir sayı girin!")
    
    template = sender.templates[template_name]
    
    # HTML önizleme dosyasını oluştur
    preview_html = f"""<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8">
        <title>Mail Preview - {template_name}</title>
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; text-align: center;">
            <h2 style="color: #2E7D32; font-size: 32px; margin-bottom: 30px;">{template['title'].format(display_name='Test User')}</h2>
            
            <div style="font-size: 18px; margin-bottom: 40px; line-height: 1.8;">
                {template['content'][0]}
            </div>
            
            <div style="background-color: #f5f5f5; padding: 30px; border-radius: 12px; margin: 40px 0;">
                <h3 style="color: #2E7D32; font-size: 24px; margin-bottom: 20px;">{template['action_title']}</h3>
                {"".join(f"<p>{line}</p>" for line in template['action_text'])}
            </div>
            
            <a href="https://play.google.com/store/apps/details?id=com.PetrichorGames.RandooVideoChat" 
               style="display: inline-block; background-color: #2E7D32; color: white; padding: 15px 35px; text-decoration: none; border-radius: 30px; margin: 20px 0; font-weight: bold; font-size: 16px;">
                {template['button_text']}
            </a>
            <br>
            <img src="assets/storeimage.png" alt="Randoo Video Chat Store" 
                 style="width: 100%; max-width: 507px; height: auto; margin-top: 30px; border-radius: 12px;">
            
            <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #eeeeee; font-size: 13px; color: #666666;">
                <p>If you have any questions, feel free to contact us at <a href="mailto:petrichorgm@gmail.com" style="color: #0066cc; text-decoration: none;">petrichorgm@gmail.com</a></p>
                <p>Click <a href="#" style="color: #0066cc; text-decoration: none;">here</a> to unsubscribe from our mailing list</p>
                <p>© 2024 Randoo Video Chat. All rights reserved.</p>
            </div>
        </div>
    </body>
</html>"""
    
    # Önizleme dosyasını kaydet
    with open('preview_mail.html', 'w', encoding='utf-8') as f:
        f.write(preview_html)
    
    # Tarayıcıda aç
    webbrowser.open('preview_mail.html')
    print("\n✅ Mail önizleme tarayıcıda açıldı!")

if __name__ == "__main__":
    while True:
        print("\n=== Randoo Mail Gönderim Sistemi ===")
        print("1. Tüm Mail Listesi")
        print("2. Mail Gönderilenler")
        print("3. Mail Gönderilmeyenler")
        print("4. Mail Gönderilmeyenlere Mail Gönder")
        print("5. Tüm Listeye Mail Gönder")
        print("6. Mail Önizleme")
        print("7. Çıkış")
        print("=" * 35)
        
        choice = input("\nSeçiminiz (1-7): ")
        
        if choice == "1":
            show_all_users()
        elif choice == "2":
            show_sent_users()
        elif choice == "3":
            show_unsent_users()
        elif choice == "4":
            send_to_unsent()
        elif choice == "5":
            send_to_all()
        elif choice == "6":
            preview_mail()
        elif choice == "7":
            print("\nProgram sonlandırılıyor...")
            break
        else:
            print("\n❌ Geçersiz seçim! Lütfen 1-7 arası bir sayı girin.") 