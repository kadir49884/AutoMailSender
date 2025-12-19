import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QComboBox, QPushButton, QTextEdit, 
                             QLineEdit, QProgressBar, QMessageBox, QFrame, QScrollArea)
from PySide6.QtCore import Qt, QThread, Signal
from mail_sender import MailSender
import threading
from datetime import datetime
import logging
import random
import time

class MailSenderThread(QThread):
    progress = Signal(int)
    status = Signal(str)
    result = Signal(str)
    finished = Signal()
    error = Signal(str)
    
    def __init__(self, sender, template_name, emails, parent=None):
        super().__init__(parent)
        self.sender = sender
        self.template_name = template_name
        self.emails = emails
        self.is_running = True
    
    def run(self):
        try:
            total = len(self.emails)
            success_count = 0
            blacklisted_count = 0
            daily_limit = len(self.sender.mail_accounts) * self.sender.daily_limit_per_account
            
            # Listeyi tersine çeviriyoruz
            reversed_emails = list(reversed(self.emails))
            
            for i, user in enumerate(reversed_emails):
                if not self.is_running:
                    break
                    
                if not self.sender.can_send_mail():
                    self.error.emit(f"Günlük mail gönderim limiti ({daily_limit}) aşıldı!\nYarın devam edebilirsiniz.")
                    break
                
                # Kara liste kontrolü
                email = user['email']
                if self.sender.is_blacklisted(email):
                    blacklisted_count += 1
                    continue
                
                if self.sender.send_mail(email, self.template_name, user.get('display_name')):
                    success_count += 1
                
                self.progress.emit(int((i + 1) / total * 100))
                self.status.emit(f"İşleniyor... {success_count}/{total} (Kara listede: {blacklisted_count}) (Her mail arası 30-90 sn bekleme var)")
                
                if i < total - 1 and self.is_running:
                    self.sender.wait_between_mails()
            
            if self.is_running:
                result = f"\n✅ {success_count}/{total} kullanıcıya '{self.template_name}' maili başarıyla gönderildi!\n"
                if blacklisted_count > 0:
                    result += f"ℹ️ {blacklisted_count} mail adresi kara listede olduğu için atlanıldı."
                self.result.emit(result)
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.status.emit("Hazır")
            self.progress.emit(0)
            self.finished.emit()
    
    def stop(self):
        self.is_running = False

class SingleMailThread(QThread):
    status = Signal(str)
    result = Signal(str)
    finished = Signal()
    error = Signal(str)
    
    def __init__(self, sender, email, template_name, parent=None):
        super().__init__(parent)
        self.sender = sender
        self.email = email
        self.template_name = template_name
    
    def run(self):
        try:
            self.status.emit(f"Mail gönderiliyor: {self.email}")
            
            # Önce kara liste kontrolü yap
            blacklist_reason = self.sender.is_blacklisted(self.email)
            if blacklist_reason:
                error_msg = f"❌ Mail gönderilemedi!\n\n"
                error_msg += f"Email: {self.email}\n"
                error_msg += f"Sebep: Bu mail adresi kara listede!\n"
                error_msg += f"Kara liste sebebi: {blacklist_reason}"
                self.result.emit(error_msg)
                self.error.emit("Mail adresi kara listede!")
                return
            
            # Firebase'den kullanıcı bilgilerini al (varsa display_name için)
            # Tekli mail göndermede Firebase'de olup olmadığı önemli değil
            display_name = None
            try:
                users = self.sender.get_firebase_users()
                user = next((u for u in users if u['email'] == self.email), None)
            display_name = user['display_name'] if user else None
            except Exception as e:
                # Firebase hatası olsa bile devam et
                logging.warning(f"Firebase kullanıcı bilgisi alınamadı: {str(e)}")
            
            success = self.sender.send_mail(self.email, template_name=self.template_name, display_name=display_name)
            
            if success:
                success_msg = f"✅ Mail başarıyla gönderildi!\n\n"
                success_msg += f"Email: {self.email}\n"
                success_msg += f"Template: {self.template_name}\n"
                success_msg += f"Display Name: {display_name or 'N/A'}\n"
                success_msg += f"Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
                
                self.result.emit(success_msg)
                
                # Tekli mail göndermede spam önlemi yok
                # Kullanıcı test için hemen tekrar gönderebilir
            else:
                # Log dosyasından son hatayı al
                try:
                    with open('mail_logs.log', 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        last_error = lines[-1] if lines else "Bilinmeyen hata"
                    error_detail = last_error.split(': ')[-1].strip()
                except:
                    error_detail = "Log dosyası okunamadı"
                
                error_msg = f"❌ Mail gönderilemedi!\n\n"
                error_msg += f"Email: {self.email}\n"
                error_msg += f"Hata: {error_detail}"
                self.result.emit(error_msg)
                self.error.emit("Mail gönderilemedi!")
                
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            error_msg = f"❌ Beklenmeyen hata!\n\n"
            error_msg += f"Hata: {str(e)}\n\n"
            error_msg += f"Detay:\n{error_detail}"
            self.result.emit(error_msg)
            self.error.emit(f"Hata: {str(e)}")
        finally:
            self.status.emit("Hazır")
            self.finished.emit()

class MailSenderGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.sender = MailSender()
        self.mail_thread = None
        self.initUI()
    
    def initUI(self):
        # Font ayarları
        bold_font = self.font()
        bold_font.setBold(True)
        
        self.setWindowTitle("Randoo Mail Gönderim Sistemi")
        self.setMinimumWidth(900)
        self.setMinimumHeight(900)
        
        # Ana widget ve layout
        central_widget = QWidget()
        
        # Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(850)
        scroll.setWidget(central_widget)
        self.setCentralWidget(scroll)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Mail şablonu seçimi
        template_frame = QFrame()
        template_frame.setFrameStyle(QFrame.StyledPanel)
        template_layout = QHBoxLayout(template_frame)
        
        template_label = QLabel("Mail Şablonu:")
        template_label.setFont(bold_font)
        self.template_combo = QComboBox()
        self.template_combo.setFont(bold_font)
        self.template_combo.addItems(self.sender.get_template_names())
        self.template_combo.currentTextChanged.connect(self.show_template_preview)
        
        self.toggle_button = QPushButton("▼ Gizle")
        self.toggle_button.setFont(bold_font)
        self.toggle_button.clicked.connect(self.toggle_preview)
        
        template_layout.addWidget(template_label)
        template_layout.addWidget(self.template_combo, 1)
        template_layout.addWidget(self.toggle_button)
        
        main_layout.addWidget(template_frame)
        
        # Önizleme alanı
        self.preview_frame = QFrame()
        self.preview_frame.setFrameStyle(QFrame.StyledPanel)
        preview_layout = QVBoxLayout(self.preview_frame)
        
        preview_label = QLabel("Mail Önizleme:")
        preview_label.setFont(bold_font)
        self.preview_area = QTextEdit()
        self.preview_area.setReadOnly(True)
        self.preview_area.setMinimumHeight(200)
        
        preview_layout.addWidget(preview_label)
        preview_layout.addWidget(self.preview_area)
        
        main_layout.addWidget(self.preview_frame)
        
        # İşlem butonları
        buttons_frame = QFrame()
        buttons_frame.setFrameStyle(QFrame.StyledPanel)
        buttons_layout = QVBoxLayout(buttons_frame)
        
        # Listeleme butonları
        list_buttons_layout = QHBoxLayout()
        
        self.list_buttons = [
            QPushButton("Tüm Mail Listesi"),
            QPushButton("Mail Gönderilenler"),
            QPushButton("Mail Gönderilmeyenler"),
            QPushButton("Veritabanı İçeriği")
        ]
        
        for button in self.list_buttons:
            button.setFont(bold_font)
            list_buttons_layout.addWidget(button)
            button.setMinimumWidth(200)
        
        self.list_buttons[0].clicked.connect(self.show_all_users)
        self.list_buttons[1].clicked.connect(self.show_sent_users)
        self.list_buttons[2].clicked.connect(self.show_unsent_users)
        self.list_buttons[3].clicked.connect(self.show_database_content)
        
        buttons_layout.addLayout(list_buttons_layout)
        
        # Gönderme butonları
        send_buttons_layout = QHBoxLayout()
        
        self.send_unsent_button = QPushButton("Mail Gönderilmeyenlere Gönder")
        self.send_all_button = QPushButton("Tüm Listeye Mail Gönder")
        
        self.send_unsent_button.setFont(bold_font)
        self.send_all_button.setFont(bold_font)
        
        self.send_unsent_button.clicked.connect(self.send_to_unsent)
        self.send_all_button.clicked.connect(self.send_to_all)
        
        send_buttons_layout.addWidget(self.send_unsent_button)
        send_buttons_layout.addWidget(self.send_all_button)
        
        buttons_layout.addLayout(send_buttons_layout)
        
        main_layout.addWidget(buttons_frame)
        
        # Tek mail gönderme
        single_mail_frame = QFrame()
        single_mail_frame.setFrameStyle(QFrame.StyledPanel)
        single_mail_layout = QHBoxLayout(single_mail_frame)
        
        self.single_mail_entry = QLineEdit()
        self.single_mail_entry.setPlaceholderText("Mail adresi girin...")
        self.single_mail_entry.setFont(bold_font)
        
        send_single_button = QPushButton("Gönder")
        send_single_button.setFont(bold_font)
        send_single_button.clicked.connect(self.send_to_single)
        
        single_mail_layout.addWidget(self.single_mail_entry)
        single_mail_layout.addWidget(send_single_button)
        
        main_layout.addWidget(single_mail_frame)
        
        # Sonuç alanı
        results_frame = QFrame()
        results_frame.setFrameStyle(QFrame.StyledPanel)
        results_layout = QVBoxLayout(results_frame)
        
        self.result_area = QTextEdit()
        self.result_area.setReadOnly(True)
        self.result_area.setMinimumHeight(300)
        self.result_area.setFont(bold_font)
        
        self.progress_bar = QProgressBar()
        self.status_label = QLabel("Hazır")
        self.status_label.setFont(bold_font)
        
        results_layout.addWidget(self.result_area)
        results_layout.addWidget(self.progress_bar)
        results_layout.addWidget(self.status_label)
        
        main_layout.addWidget(results_frame)
        
        # İlk şablonu göster
        self.show_template_preview()
    
    def toggle_preview(self):
        if self.preview_frame.isVisible():
            self.preview_frame.hide()
            self.toggle_button.setText("▶ Göster")
        else:
            self.preview_frame.show()
            self.toggle_button.setText("▼ Gizle")
    
    def show_template_preview(self):
        template_name = self.template_combo.currentText()
        template = self.sender.templates[template_name]
        
        preview = f"""Konu: {template['subject']}
        
Başlık: {template['title'].format(display_name='[Kullanıcı Adı]')}

İçerik:
{chr(10).join(template['content'])}

{template['action_title']}:
{chr(10).join(template['action_text'])}

Buton: {template['button_text']}
"""
        
        self.preview_area.setText(preview)
    
    def show_all_users(self):
        users = self.sender.get_firebase_users()
        result = f"\nToplam {len(users)} kullanıcı bulundu.\n" + "-" * 70 + "\n"
        
        for i, user in enumerate(users, 1):
            result += f"{i}. Email: {user['email']}\n"
            result += f"   Display Name: {user.get('display_name', 'Yok')}\n"
            result += "-" * 70 + "\n"
        
        self.result_area.setText(result)
        self.status_label.setText("Hazır")
    
    def show_sent_users(self):
        all_users = self.sender.get_firebase_users()
        template_name = self.template_combo.currentText()
        sent_users = self.sender.get_sent_users(template_name)
        
        result = f"\n{template_name} şablonu için mail gönderilen kullanıcılar:\n" + "-" * 70 + "\n"
        result += f"Toplam {len(sent_users)} kullanıcıya mail gönderilmiş.\n" + "-" * 70 + "\n"
        
        for i, user in enumerate(sent_users, 1):
            result += f"{i}. Email: {user['email']}\n"
            result += f"   Display Name: {user.get('display_name', 'Yok')}\n"
            result += "-" * 70 + "\n"
        
        self.result_area.setText(result)
    
    def show_unsent_users(self):
        template_name = self.template_combo.currentText()
        unsent_users = self.sender.get_unsent_firebase_users(template_name)
        
        result = f"\n{template_name} şablonu için mail gönderilmeyen kullanıcılar:\n" + "-" * 70 + "\n"
        result += f"Toplam {len(unsent_users)} kullanıcıya mail gönderilmemiş.\n" + "-" * 70 + "\n"
        
        for i, user in enumerate(unsent_users, 1):
            result += f"{i}. Email: {user['email']}\n"
            result += f"   Display Name: {user.get('display_name', 'Yok')}\n"
            result += "-" * 70 + "\n"
        
        self.result_area.setText(result)
    
    def send_to_unsent(self):
        template_name = self.template_combo.currentText()
        template = self.sender.templates[template_name]
        daily_limit = len(self.sender.mail_accounts) * self.sender.daily_limit_per_account
        
        reply = QMessageBox.question(
            self, 
            "Onay",
            f"'{template['subject']}' mailini henüz almamış kullanıcılara göndermek istediğinize emin misiniz?\n\n" +
            "Not: Spam önlemleri nedeniyle:\n" +
            "- Her mail arası 30-90 saniye bekleme olacaktır\n" +
            f"- Günlük maksimum {daily_limit} mail gönderilecektir ({len(self.sender.mail_accounts)} aktif hesap × {self.sender.daily_limit_per_account})",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            unsent_users = self.sender.get_unsent_firebase_users(template_name)
            if not unsent_users:
                QMessageBox.information(self, "Bilgi", f"Tüm kullanıcılara '{template_name}' maili gönderilmiş!")
                return
            
            if self.mail_thread and self.mail_thread.isRunning():
                QMessageBox.warning(self, "Uyarı", "Zaten bir mail gönderimi devam ediyor!")
                return
            
            self.mail_thread = MailSenderThread(self.sender, template_name, unsent_users)
            self.mail_thread.progress.connect(self.progress_bar.setValue)
            self.mail_thread.status.connect(self.status_label.setText)
            self.mail_thread.result.connect(self.result_area.setText)
            self.mail_thread.error.connect(lambda msg: QMessageBox.warning(self, "Uyarı", msg))
            self.mail_thread.finished.connect(self.show_database_content)
            self.mail_thread.start()
    
    def send_to_all(self):
        template_name = self.template_combo.currentText()
        template = self.sender.templates[template_name]
        daily_limit = len(self.sender.mail_accounts) * self.sender.daily_limit_per_account
        
        reply = QMessageBox.question(
            self,
            "Onay",
            f"TÜM kullanıcılara '{template['subject']}' mailini göndermek istediğinize emin misiniz?\n\n" +
            "Not: Spam önlemleri nedeniyle:\n" +
            "- Her mail arası 30-90 saniye bekleme olacaktır\n" +
            f"- Günlük maksimum {daily_limit} mail gönderilecektir ({len(self.sender.mail_accounts)} aktif hesap × {self.sender.daily_limit_per_account})",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            all_users = self.sender.get_firebase_users()
            
            if self.mail_thread and self.mail_thread.isRunning():
                QMessageBox.warning(self, "Uyarı", "Zaten bir mail gönderimi devam ediyor!")
                return
            
            self.mail_thread = MailSenderThread(self.sender, template_name, all_users)
            self.mail_thread.progress.connect(self.progress_bar.setValue)
            self.mail_thread.status.connect(self.status_label.setText)
            self.mail_thread.result.connect(self.result_area.setText)
            self.mail_thread.error.connect(lambda msg: QMessageBox.warning(self, "Uyarı", msg))
            self.mail_thread.finished.connect(self.show_database_content)
            self.mail_thread.start()
    
    def send_to_single(self):
        # Önceki thread hala çalışıyorsa uyar
        if hasattr(self, 'single_thread') and self.single_thread.isRunning():
            QMessageBox.information(self, "Bilgi", "Bir mail gönderimi devam ediyor. Lütfen bekleyin...")
            return
        
        email = self.single_mail_entry.text().strip()
        if not email:
            QMessageBox.critical(self, "Hata", "Lütfen bir e-posta adresi girin!")
            return
        
        template_name = self.template_combo.currentText()
        if not template_name:
            QMessageBox.critical(self, "Hata", "Lütfen bir şablon seçin!")
            return
        
        # Tekli mail göndermede duplicate kontrolü yapma - her zaman gönder
        # (Kullanıcı test için aynı mail'e birden fazla kez gönderebilir)
        
        self.single_thread = SingleMailThread(self.sender, email, template_name)
        self.single_thread.status.connect(self.status_label.setText)
        self.single_thread.result.connect(self.result_area.setText)
        self.single_thread.error.connect(lambda msg: QMessageBox.warning(self, "Uyarı", msg))
        self.single_thread.finished.connect(lambda: self.single_mail_entry.clear())
        self.single_thread.finished.connect(self.show_database_content)
        self.single_thread.start()
    
    def show_database_content(self):
        """Veritabanı içeriğini gösterir"""
        records = self.sender.get_database_content()
        result = f"Toplam {len(records)} kayıt bulundu.\n"
        result += "-" * 70 + "\n"
        
        for i, record in enumerate(records, 1):
            email, template_name, sent_date, display_name, from_email = record
            
            # Her gönderen mailin gönderme sayısını al
            try:
                conn = self.sender.get_db_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT COUNT(*) 
                    FROM sent_mails 
                    WHERE from_email = ? AND to_email = ?
                ''', (from_email, email))
                send_count = cursor.fetchone()[0]
            except Exception as e:
                send_count = 0
            finally:
                if 'conn' in locals():
                    conn.close()
            
            result += f"{i}. Email: {email}\n"
            result += f"   Template: {template_name}\n"
            result += f"   Gönderim Tarihi: {sent_date}\n"
            result += f"   Display Name: {display_name}\n"
            result += f"   Gönderen Gmail, Gönderme sayısı: {from_email} , {send_count}\n"
            result += "-" * 70 + "\n"
        
        self.result_area.setText(result)
        self.status_label.setText("Hazır")
    
    def closeEvent(self, event):
        if self.mail_thread and self.mail_thread.isRunning():
            reply = QMessageBox.question(
                self,
                "Onay",
                "Mail gönderimi devam ediyor. Çıkmak istediğinize emin misiniz?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.mail_thread.stop()
                self.mail_thread.wait()
                event.accept()
            else:
                event.ignore()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MailSenderGUI()
    window.show()
    sys.exit(app.exec()) 