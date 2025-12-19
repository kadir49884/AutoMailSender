import os
import json
import smtplib
import sqlite3
import random
import time
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from dotenv import load_dotenv
import logging
import firebase_admin
from firebase_admin import credentials, auth

# Firebase yapılandırması
def init_firebase():
    """Firebase'i environment variable'dan yükle"""
    firebase_creds = os.getenv('FIREBASE_CREDENTIALS_JSON')
    if firebase_creds:
        # Environment variable'dan JSON yükle
        cred_dict = json.loads(firebase_creds)
        cred = credentials.Certificate(cred_dict)
    else:
        # Local development için dosyadan yükle
        cred = credentials.Certificate('firebase-credentials.json')
    
    firebase_admin.initialize_app(cred)

# Firebase'i başlat
init_firebase()

# .env dosyasından Gmail bilgilerini al
load_dotenv()

class MailSender:
    def __init__(self):
        # Mail hesaplarını dinamik olarak yükle
        self.mail_accounts = []
        self.load_mail_accounts()
        
        self.current_account_index = 0
        self.daily_limit_per_account = 500  # Her hesap için günlük limit
        self.min_delay = 30     # Minimum bekleme süresi (30 saniye)
        self.max_delay = 90    # Maximum bekleme süresi (90 saniye)
        
        # Veritabanı yolu (Railway persistent volume veya local)
        data_dir = os.getenv('DATA_DIR', '.')
        if data_dir != '.' and not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)
        self.db_path = os.path.join(data_dir, 'mail_tracking.db')
        
        # HTML şablonunu yükle
        with open('templates/email_template.html', 'r', encoding='utf-8') as f:
            self.html_template = f.read()
        
        # Mail şablonlarını yükle
        self.templates = self.load_templates()
        
        # Veritabanını oluştur/bağlan
        self.init_database()
        
        # Loglama ayarları
        logging.basicConfig(
            filename='mail_logs.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
    def load_mail_accounts(self):
        """Aktif Gmail hesaplarını yükler"""
        for i in range(1, 5):  # 1'den 4'e kadar
            user = os.getenv(f'GMAIL_USER_{i}')
            password = os.getenv(f'GMAIL_APP_PASSWORD_{i}')
            
            if user and password and not user.startswith('#'):
                self.mail_accounts.append({
                    'email': user,
                    'password': password,
                    'daily_count': 0,
                    'last_used': None,
                    'smtp': None
                })
                logging.info(f"Mail hesabı yüklendi: {user}")
        
        if not self.mail_accounts:
            raise Exception("Hiç aktif mail hesabı bulunamadı! En az bir hesap aktif olmalıdır.")
        
        logging.info(f"Toplam {len(self.mail_accounts)} aktif mail hesabı yüklendi")
        
    def get_smtp_connection(self, account):
        """Hesap için yeni bir SMTP bağlantısı oluşturur"""
        try:
            if account['smtp']:
                try:
                    # Bağlantıyı test et
                    account['smtp'].noop()
                    return account['smtp']
                except:
                    # Bağlantı kopmuşsa kapat
                    try:
                        account['smtp'].quit()
                    except:
                        pass
                    account['smtp'] = None
            
            # Yeni bağlantı oluştur
            smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            smtp.login(account['email'], account['password'])
            account['smtp'] = smtp
            logging.info(f"Yeni SMTP bağlantısı açıldı: {account['email']}")
            return smtp
            
        except Exception as e:
            logging.error(f"SMTP bağlantı hatası ({account['email']}): {str(e)}")
            account['smtp'] = None
            return None
    
    def close_smtp_connections(self):
        """Tüm SMTP bağlantılarını kapatır"""
        for account in self.mail_accounts:
            if account['smtp']:
                try:
                    account['smtp'].quit()
                    logging.info(f"SMTP bağlantısı kapatıldı: {account['email']}")
                except:
                    pass
                account['smtp'] = None
    
    def test_smtp_connections(self):
        """Tüm mail hesaplarının SMTP bağlantılarını test eder"""
        results = []
        for account in self.mail_accounts:
            result = {
                'email': account['email'],
                'status': 'unknown',
                'message': ''
            }
            
            try:
                # Yeni SMTP bağlantısı oluştur ve test et
                smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10)
                smtp.login(account['email'], account['password'])
                smtp.noop()  # Bağlantıyı test et
                smtp.quit()
                
                result['status'] = 'success'
                result['message'] = 'Bağlantı başarılı ✅'
                logging.info(f"SMTP test başarılı: {account['email']}")
                
            except smtplib.SMTPAuthenticationError:
                result['status'] = 'error'
                result['message'] = 'Kimlik doğrulama hatası (Şifre yanlış) ❌'
                logging.error(f"SMTP auth hatası: {account['email']}")
                
            except Exception as e:
                result['status'] = 'error'
                result['message'] = f'Bağlantı hatası: {str(e)[:50]}... ❌'
                logging.error(f"SMTP test hatası ({account['email']}): {str(e)}")
            
            results.append(result)
        
        return results
    
    def load_templates(self):
        """templates klasöründeki tüm JSON dosyalarını yükler"""
        templates = {}  # Boş sözlük oluştur
        templates_dir = "templates"
        
        for filename in os.listdir(templates_dir):
            if filename.endswith(".json"):
                template_name = os.path.splitext(filename)[0]
                with open(os.path.join(templates_dir, filename), 'r', encoding='utf-8') as f:
                    templates[template_name] = json.load(f)
                logging.info(f"Mail şablonu yüklendi: {template_name}")
        
        return templates  # Sözlüğü döndür
    
    def get_db_connection(self):
        """Her thread için yeni bir veritabanı bağlantısı oluşturur"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Veritabanını oluşturur ve gerekirse günceller"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Sent mails tablosu
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sent_mails (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    to_email TEXT NOT NULL,
                    from_email TEXT NOT NULL,
                    template_name TEXT NOT NULL,
                    sent_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    display_name TEXT
                )
            ''')
            
            # Kara liste tablosu
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS blacklist (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL UNIQUE,
                    reason TEXT NOT NULL,
                    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            logging.info("Veritabanı tabloları oluşturuldu")
            
        except Exception as e:
            logging.error(f"Veritabanı oluşturma hatası: {str(e)}")
            conn.rollback()
        finally:
            conn.close()
    
    def add_to_blacklist(self, email, reason):
        """Mail adresini kara listeye ekler"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO blacklist (email, reason) VALUES (?, ?)', (email, reason))
            conn.commit()
            logging.info(f"Mail adresi kara listeye eklendi: {email} (Sebep: {reason})")
            return True
        except sqlite3.IntegrityError:
            # Mail adresi zaten kara listede
            logging.info(f"Mail adresi zaten kara listede: {email}")
            return False
        except Exception as e:
            logging.error(f"Kara listeye ekleme hatası: {str(e)}")
            return False
        finally:
            conn.close()
    
    def is_blacklisted(self, email):
        """Mail adresinin kara listede olup olmadığını kontrol eder"""
        conn = self.get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT reason FROM blacklist WHERE email = ?', (email,))
            result = cursor.fetchone()
            return result[0] if result else None
        finally:
            conn.close()
    
    def record_sent_mail(self, to_email, from_email, template_name, display_name=None):
        """Gönderilen maili veritabanına kaydeder"""
        conn = self.get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO sent_mails (to_email, from_email, template_name, sent_date, display_name)
                VALUES (?, ?, ?, ?, ?)
            ''', (to_email, from_email, template_name, datetime.now(), display_name))
            conn.commit()
        finally:
            conn.close()
    
    def is_mail_sent(self, email, template_name):
        """Belirtilen mail+template kombinasyonunun gönderilip gönderilmediğini kontrol eder"""
        # Artık her zaman False döndürüyoruz çünkü tekrar gönderime izin veriyoruz
        return False
    
    def get_sent_users(self, template_name):
        """Belirtilen template için mail gönderilmiş kullanıcıları getirir"""
        conn = self.get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT DISTINCT to_email, display_name, from_email, sent_date 
                FROM sent_mails 
                WHERE template_name = ?
                ORDER BY sent_date DESC
            ''', (template_name,))
            sent_users = cursor.fetchall()
            return [{
                'email': email, 
                'display_name': display_name,
                'from_email': from_email,
                'sent_date': sent_date
            } for email, display_name, from_email, sent_date in sent_users]
        finally:
            conn.close()
    
    def get_unsent_firebase_users(self, template_name):
        """Belirtilen template için henüz mail gönderilmemiş Firebase kullanıcılarını getirir"""
        try:
            all_users = self.get_firebase_users()
            sent_users = self.get_sent_users(template_name)
            sent_emails = [user['email'] for user in sent_users]
            
            unsent_users = [user for user in all_users if user['email'] not in sent_emails]
            logging.info(f"Toplam {len(all_users)} kullanıcıdan {len(unsent_users)} tanesine {template_name} maili gönderilmemiş")
            return unsent_users
            
        except Exception as e:
            logging.error(f"Mail gönderilmemiş kullanıcıları alma hatası: {str(e)}")
            return []
    
    def get_display_name(self, email, username=None):
        """Görüntülenecek ismi belirler. Önce username'e bakar, yoksa mail adresinden alır."""
        if username and username.strip():
            return username.strip()
        return email.split('@')[0].capitalize()
        
    def get_firebase_users(self):
        """Firebase'den tüm kullanıcıları alır"""
        try:
            # Sayfalama ile tüm kullanıcıları al
            users = []
            page = auth.list_users()
            while page:
                for user in page.users:
                    if user.email:  # Sadece email'i olan kullanıcıları al
                        users.append({
                            'email': user.email,
                            'display_name': user.display_name if user.display_name else None
                        })
                page = page.get_next_page()
            
            logging.info(f"Firebase'den {len(users)} kullanıcı alındı")
            return users
            
        except Exception as e:
            logging.error(f"Firebase kullanıcı listesi alınırken hata: {str(e)}")
            return []
    
    def get_today_sent_count(self):
        """Bugün gönderilen mail sayısını döndürür"""
        conn = self.get_db_connection()
        try:
            cursor = conn.cursor()
            today = datetime.now().date()
            cursor.execute('''
                SELECT COUNT(*) FROM sent_mails 
                WHERE date(sent_date) = date(?)
            ''', (today,))
            result = cursor.fetchone()[0]
            return result
        finally:
            conn.close()
    
    def get_next_account(self, to_email=None):
        """
        Sıradaki uygun mail hesabını seçer
        - Kullanıcıya en az mail atan hesabı seçer
        - Aynı hesabın art arda mail atmasını engeller
        """
        if not to_email:
            return self.mail_accounts[self.current_account_index]

        # Veritabanı bağlantısı
        conn = self.get_db_connection()
        cursor = conn.cursor()

        try:
            # Her hesabın bu kullanıcıya attığı mail sayısını al
            account_stats = []
            for i, account in enumerate(self.mail_accounts):
                cursor.execute('''
                    SELECT COUNT(*) FROM sent_mails 
                    WHERE from_email = ? AND to_email = ?
                ''', (account['email'], to_email))
                sent_count = cursor.fetchone()[0]
                
                # Son maili ne zaman attı?
                cursor.execute('''
                    SELECT MAX(sent_date) FROM sent_mails 
                    WHERE from_email = ?
                    ORDER BY sent_date DESC
                    LIMIT 1
                ''', (account['email'],))
                last_sent = cursor.fetchone()[0]
                
                # Hesap günlük limiti aşmamışsa listeye ekle
                if account['daily_count'] < self.daily_limit_per_account:
                    account_stats.append({
                        'index': i,
                        'account': account,
                        'sent_count': sent_count,
                        'last_sent': last_sent
                    })

            if not account_stats:
                logging.warning("Kullanılabilir hesap bulunamadı!")
                return None

            # En son mail atma zamanına göre sırala
            account_stats.sort(key=lambda x: (x['last_sent'] or '1970-01-01'))
            
            # En az mail atan hesapları bul
            min_sent = min(stat['sent_count'] for stat in account_stats)
            least_sending_accounts = [
                stat for stat in account_stats 
                if stat['sent_count'] == min_sent
            ]

            # En az mail atanlar arasından en uzun süredir mail atmayanı seç
            selected = least_sending_accounts[0]
            self.current_account_index = selected['index']
            
            logging.info(f"Seçilen hesap: {selected['account']['email']} (Kullanıcıya gönderilen: {min_sent})")
            return selected['account']

        except Exception as e:
            logging.error(f"Hesap seçme hatası: {str(e)}")
            return None

        finally:
            conn.close()
    
    def can_send_mail(self):
        """Mail gönderme limitlerini kontrol eder"""
        # Kullanılabilir hesap var mı kontrol et
        account = self.get_next_account()
        return account is not None
    
    def wait_between_mails(self):
        """Anti-spam için mailler arası rastgele bekleme süresi ekler"""
        delay = random.uniform(self.min_delay, self.max_delay)
        time.sleep(delay)
    
    def get_template_names(self):
        """Mevcut mail şablonlarının isimlerini döndürür"""
        template_names = list(self.templates.keys())
        
        # Özel sıralama: welcome ve new_update önce gelsin
        if 'welcome' in template_names:
            template_names.remove('welcome')
            template_names.insert(0, 'welcome')
            
        if 'new_update' in template_names:
            template_names.remove('new_update')
            template_names.insert(1, 'new_update')
            
        return template_names

    def send_mail(self, to_email, template_name, display_name=None):
        """Belirtilen mail adresine seçili şablonu kullanarak mail gönderir"""
        max_retries = 3  # Maksimum deneme sayısı
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Uygun hesabı seç
                account = self.get_next_account(to_email)
                if not account:
                    logging.warning("Uygun hesap bulunamadı!")
                    return False
                
                # Her mail gönderimi için yeni SMTP bağlantısı al
                smtp = self.get_smtp_connection(account)
                if not smtp:
                    logging.error(f"SMTP bağlantısı kurulamadı: {account['email']}")
                    retry_count += 1
                    continue
                
                template = self.templates[template_name]
                display_name = self.get_display_name(to_email, display_name)
                
                # Mail içeriğini hazırla
                msg = MIMEMultipart('alternative')
                msg['Subject'] = template['subject']
                msg['From'] = account['email']
                msg['To'] = to_email
                msg['List-Unsubscribe'] = f'<mailto:petrichorgm@gmail.com?subject=Unsubscribe>'
                msg['List-Unsubscribe-Post'] = 'List-Unsubscribe=One-Click'
                
                # Plain text versiyonu oluştur
                plain_text = f"""
{template['title'].format(display_name=display_name)}

{chr(10).join(template['content'])}

{template['action_title']}
{chr(10).join(template['action_text'])}

Install Vidlo Video Chat:
https://play.google.com/store/apps/details?id=com.PetrichorGames.RandooVideoChat

---
If you have any questions, contact us at petrichorgm@gmail.com
To unsubscribe, reply with 'Unsubscribe' in the subject line.
© 2024 Vidlo Video Chat. All rights reserved.
                """.strip()
                
                # HTML içeriği hazırla
                html_content = self.html_template.format(
                    title=template['title'].format(display_name=display_name),
                    content="\n".join(template['content']),
                    action_title=template['action_title'],
                    action_text="\n".join(template['action_text']),
                    button_text=template['button_text']
                )
                
                # Plain text önce, sonra HTML (mail clientlar en iyisini seçer)
                msg.attach(MIMEText(plain_text, 'plain'))
                msg.attach(MIMEText(html_content, 'html'))
                
                # Store görselini ekle
                with open('assets/storeimage.png', 'rb') as f:
                    img = MIMEImage(f.read())
                    img.add_header('Content-ID', '<storeimage>')
                    img.add_header('Content-Disposition', 'inline', filename='Randoo Video Chat.png')
                    msg.attach(img)
                
                try:
                    # Maili gönder
                    smtp.send_message(msg)
                    
                    # Veritabanına kaydet
                    self.record_sent_mail(to_email, account['email'], template_name, display_name)
                    
                    # Hesap istatistiklerini güncelle
                    account['daily_count'] += 1
                    account['last_used'] = datetime.now()
                    
                    logging.info(f"Mail başarıyla gönderildi: {to_email} (Gönderen: {account['email']})")
                    return True
                    
                except smtplib.SMTPRecipientsRefused as e:
                    error_code = list(e.recipients.values())[0][0]
                    if error_code == 550:
                        logging.error(f"Hard bounce - Mail adresi bulunamadı: {to_email}")
                        self.add_to_blacklist(to_email, "Hard bounce - Mail adresi bulunamadı")
                        return False
                    elif error_code == 552:
                        logging.error(f"Soft bounce - Mail kutusu dolu: {to_email}")
                        return False
                    elif error_code == 553:
                        logging.error(f"Hard bounce - Geçersiz mail adresi: {to_email}")
                        self.add_to_blacklist(to_email, "Hard bounce - Geçersiz mail adresi")
                        return False
                    else:
                        raise e
                        
                except smtplib.SMTPResponseException as e:
                    if e.smtp_code == 421:
                        logging.error(f"SMTP sunucusu bağlantıyı reddetti: {e.smtp_error}")
                        account['smtp'] = None  # Bağlantıyı sıfırla
                        retry_count += 1
                        continue
                    else:
                        raise e
                
            except Exception as e:
                retry_count += 1
                error_msg = f"Mail gönderme hatası (Deneme {retry_count}/{max_retries}): {str(e)}"
                logging.error(error_msg)
                
                if retry_count < max_retries:
                    retry_delay = random.uniform(20, 40)
                    logging.info(f"Yeniden deneme öncesi {retry_delay:.1f} saniye bekleniyor...")
                    time.sleep(retry_delay)
                    continue
                else:
                    logging.error(f"Mail gönderilemedi ({max_retries} deneme sonrası): {to_email}")
                    return False

    def send_mail_to_all_users(self, template_name):
        """Tüm Firebase kullanıcılarına belirtilen şablonu kullanarak mail gönderir"""
        all_users = self.get_firebase_users()
        success_count = 0
        
        for user in all_users:
            if not self.can_send_mail():
                logging.warning("Günlük mail limiti aşıldı! Gönderim durduruluyor.")
                break
                
            if self.send_mail(user['email'], template_name, user.get('display_name')):
                success_count += 1
                
        logging.info(f"Toplu mail gönderimi tamamlandı. Başarılı: {success_count}/{len(all_users)}")
        return success_count

    def get_database_content(self):
        """Veritabanındaki tüm kayıtları getirir"""
        conn = self.get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT to_email, template_name, sent_date, display_name, from_email 
                FROM sent_mails 
                ORDER BY sent_date DESC
            ''')
            records = cursor.fetchall()
            return records
        finally:
            conn.close()