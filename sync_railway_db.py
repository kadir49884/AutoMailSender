#!/usr/bin/env python3
"""Railway database'ini local'e senkronize eder"""

import sqlite3
import os
from datetime import datetime

def sync_databases():
    """Railway ve local database'leri birleştirir"""
    
    # Database yolları
    local_db = 'mail_tracking.db'
    railway_db = 'railway_backup.db'  # Railway'den indirilen DB
    
    if not os.path.exists(railway_db):
        print(f"❌ {railway_db} bulunamadı!")
        print("📥 Railway'den database'i indirmen gerekiyor.")
        return
    
    # Bağlantılar
    local_conn = sqlite3.connect(local_db)
    railway_conn = sqlite3.connect(railway_db)
    
    local_cursor = local_conn.cursor()
    railway_cursor = railway_conn.cursor()
    
    print("🔄 Senkronizasyon başlıyor...\n")
    
    # Railway'deki tracking verilerini al
    railway_cursor.execute('''
        SELECT tracking_id, opened, opened_date, clicked, clicked_date
        FROM sent_mails
        WHERE (opened = 1 OR clicked = 1) AND tracking_id IS NOT NULL
    ''')
    
    tracking_updates = railway_cursor.fetchall()
    
    updated_count = 0
    for tracking_id, opened, opened_date, clicked, clicked_date in tracking_updates:
        # Local'de bu tracking_id var mı?
        local_cursor.execute('SELECT id FROM sent_mails WHERE tracking_id = ?', (tracking_id,))
        result = local_cursor.fetchone()
        
        if result:
            # Güncelle
            local_cursor.execute('''
                UPDATE sent_mails
                SET opened = ?, opened_date = ?, clicked = ?, clicked_date = ?
                WHERE tracking_id = ?
            ''', (opened, opened_date, clicked, clicked_date, tracking_id))
            updated_count += 1
            print(f"✅ Güncellendi: {tracking_id[:8]}... (Açıldı: {opened}, Tıklandı: {clicked})")
    
    local_conn.commit()
    
    print(f"\n{'='*60}")
    print(f"✅ Senkronizasyon tamamlandı!")
    print(f"📊 Güncellenen kayıt: {updated_count}")
    print(f"{'='*60}")
    
    local_conn.close()
    railway_conn.close()

if __name__ == '__main__':
    sync_databases()

