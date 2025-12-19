#!/usr/bin/env python3
"""Click tracking debug"""

import sqlite3

def check_clicks():
    """Click tracking durumunu kontrol et"""
    
    print("="*60)
    print("🔍 CLICK TRACKING DEBUG")
    print("="*60)
    print()
    
    conn = sqlite3.connect('mail_tracking.db')
    cursor = conn.cursor()
    
    # Son mailleri kontrol et
    cursor.execute('''
        SELECT to_email, template_name, tracking_id, opened, clicked, sent_date
        FROM sent_mails
        ORDER BY sent_date DESC
        LIMIT 5
    ''')
    
    print("📧 SON 5 MAİL:")
    print()
    for email, template, tracking_id, opened, clicked, sent_date in cursor.fetchall():
        print(f"Email: {email}")
        print(f"Template: {template}")
        print(f"Tracking ID: {tracking_id}")
        print(f"Açıldı: {'✅' if opened else '❌'}")
        print(f"Tıklandı: {'✅' if clicked else '❌'}")
        print(f"Tarih: {sent_date}")
        print()
        print(f"🔗 Manuel click URL'i:")
        print(f"https://automailsender-production.up.railway.app/click/{tracking_id}")
        print()
        print("-"*60)
        print()
    
    conn.close()
    
    print("💡 MANUEL TEST:")
    print("1. Yukarıdaki click URL'ini browser'da aç")
    print("2. Play Store'a yönlendirecek")
    print("3. Stats'ı yenile:")
    print("   https://automailsender-production.up.railway.app/stats")
    print("4. Click count artmalı!")
    print()
    print("="*60)

if __name__ == '__main__':
    check_clicks()

