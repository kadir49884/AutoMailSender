import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from mail_sender import MailSender
import threading
import logging
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Global değişkenler
sender = None
current_job = None
job_status = {
    'running': False,
    'progress': 0,
    'total': 0,
    'success': 0,
    'failed': 0,
    'current_template': None,
    'current_account': None,
    'started_at': None,
    'message': 'Hazır'
}

def init_sender():
    """Mail sender'ı başlatır"""
    global sender
    if sender is None:
        try:
            sender = MailSender()
            logging.info("Mail sender başarıyla başlatıldı")
        except Exception as e:
            logging.error(f"Mail sender başlatma hatası: {str(e)}")
            raise

@app.route('/')
def index():
    """Ana sayfa"""
    try:
        init_sender()
        stats = {
            'total_accounts': len(sender.mail_accounts),
            'daily_limit': len(sender.mail_accounts) * sender.daily_limit_per_account,
            'sent_today': sender.get_today_sent_count(),
            'templates': sender.get_template_names()
        }
        return render_template('index.html', stats=stats, status=job_status)
    except Exception as e:
        return f"Hata: {str(e)}", 500

@app.route('/users')
def users():
    """Kullanıcı listesi"""
    try:
        init_sender()
        all_users = sender.get_firebase_users()
        return render_template('users.html', users=all_users, total=len(all_users))
    except Exception as e:
        return f"Hata: {str(e)}", 500

@app.route('/database')
def database():
    """Veritabanı içeriği"""
    try:
        init_sender()
        records = sender.get_database_content()
        return render_template('database.html', records=records, total=len(records))
    except Exception as e:
        return f"Hata: {str(e)}", 500

@app.route('/send', methods=['POST'])
def send_mails():
    """Mail gönderim işlemini başlatır"""
    global current_job, job_status
    
    if job_status['running']:
        return jsonify({'error': 'Zaten bir gönderim devam ediyor'}), 400
    
    template_name = request.form.get('template')
    send_type = request.form.get('send_type', 'unsent')  # 'all' veya 'unsent'
    
    if not template_name:
        return jsonify({'error': 'Template seçilmedi'}), 400
    
    # Background thread'de mail gönder
    current_job = threading.Thread(target=send_mails_background, args=(template_name, send_type))
    current_job.start()
    
    return jsonify({'success': True, 'message': 'Mail gönderimi başlatıldı'})

def send_mails_background(template_name, send_type):
    """Background'da mail gönderir"""
    global job_status
    
    try:
        job_status['running'] = True
        job_status['current_template'] = template_name
        job_status['started_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        job_status['message'] = 'Mail listesi hazırlanıyor...'
        
        # Kullanıcı listesini al
        if send_type == 'all':
            users = sender.get_firebase_users()
        else:
            users = sender.get_unsent_firebase_users(template_name)
        
        job_status['total'] = len(users)
        job_status['success'] = 0
        job_status['failed'] = 0
        
        # Listeyi tersine çevir
        users = list(reversed(users))
        
        for i, user in enumerate(users):
            if not job_status['running']:
                break
            
            email = user['email']
            
            # Kara liste kontrolü
            if sender.is_blacklisted(email):
                job_status['failed'] += 1
                continue
            
            # Limit kontrolü
            if not sender.can_send_mail():
                job_status['message'] = 'Günlük limit aşıldı!'
                break
            
            # Mail gönder
            result = sender.send_mail(email, template_name, user.get('display_name'))
            if result:
                job_status['success'] += 1
                # Son kullanılan hesabı bul
                for account in sender.mail_accounts:
                    if account.get('last_used'):
                        job_status['current_account'] = account['email']
                        break
            else:
                job_status['failed'] += 1
            
            job_status['progress'] = i + 1
            job_status['message'] = f'İşleniyor... {i+1}/{len(users)}'
            
            # Bekleme süresi
            if i < len(users) - 1:
                sender.wait_between_mails()
        
        job_status['message'] = f'Tamamlandı! Başarılı: {job_status["success"]}, Başarısız: {job_status["failed"]}'
        
    except Exception as e:
        job_status['message'] = f'Hata: {str(e)}'
        logging.error(f"Mail gönderim hatası: {str(e)}")
    finally:
        job_status['running'] = False

@app.route('/status')
def status():
    """İş durumunu döndürür"""
    return jsonify(job_status)

@app.route('/stop', methods=['POST'])
def stop():
    """Mail gönderimini durdurur"""
    global job_status
    job_status['running'] = False
    job_status['message'] = 'Durduruldu'
    return jsonify({'success': True})

@app.route('/test_smtp', methods=['GET'])
def test_smtp():
    """SMTP bağlantılarını test eder"""
    try:
        init_sender()
        results = sender.test_smtp_connections()
        
        # Genel durum
        all_success = all(r['status'] == 'success' for r in results)
        
        return jsonify({
            'success': True,
            'all_connected': all_success,
            'results': results,
            'message': '✅ Tüm hesaplar bağlı!' if all_success else '⚠️ Bazı hesaplarda sorun var!'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Test hatası: {str(e)}'
        }), 500

@app.route('/track/<tracking_id>')
def track_open(tracking_id):
    """Mail açılma tracking endpoint (1x1 pixel döndürür)"""
    try:
        init_sender()
        # Mail açılma kaydını güncelle
        sender.mark_email_opened(tracking_id)
        logging.info(f"Mail açıldı: {tracking_id}")
    except Exception as e:
        logging.error(f"Tracking hatası: {str(e)}")
    
    # 1x1 transparan pixel döndür
    pixel = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    return pixel, 200, {'Content-Type': 'image/png', 'Cache-Control': 'no-cache, no-store, must-revalidate'}

@app.route('/stats')
def stats():
    """Mail açılma istatistiklerini gösterir"""
    try:
        init_sender()
        open_rate_stats = sender.get_open_rate_stats()
        return render_template('stats.html', stats=open_rate_stats)
    except Exception as e:
        return f"Hata: {str(e)}", 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

