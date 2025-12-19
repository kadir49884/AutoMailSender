#!/usr/bin/env python3
"""Railway sync durumunu kontrol et"""

import sqlite3

def check_databases():
    """Local ve Railway database'leri karşılaştır"""
    
    print("="*60)
    print("🔍 DATABASE KARŞILAŞTIRMASI")
    print("="*60)
    print()
    
    # Local database
    local_conn = sqlite3.connect('mail_tracking.db')
    local_cursor = local_conn.cursor()
    
    local_cursor.execute('SELECT COUNT(*) FROM sent_mails WHERE tracking_id IS NOT NULL')
    local_count = local_cursor.fetchone()[0]
    
    local_cursor.execute('SELECT to_email, template_name, tracking_id FROM sent_mails ORDER BY sent_date DESC LIMIT 3')
    local_recent = local_cursor.fetchall()
    
    print("📍 LOCAL DATABASE:")
    print(f"   Toplam kayıt: {local_count}")
    print(f"   Son 3 kayıt:")
    for email, template, tracking_id in local_recent:
        print(f"     - {email} ({template}) [{tracking_id[:8]}...]")
    
    print()
    print("="*60)
    print()
    print("🌐 RAILWAY DATABASE:")
    print("   Railway stats'ı kontrol et:")
    print("   https://automailsender-production.up.railway.app/stats")
    print()
    print("💡 Railway'de aynı kayıtları göreceksin!")
    print("   (Sync başarılıysa)")
    print()
    print("="*60)
    
    local_conn.close()

if __name__ == '__main__':
    check_databases()

