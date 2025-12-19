# Vidlo Mail Dashboard - Railway Deploy

## 🚀 Railway'e Deploy Etme Adımları

### 1. Railway Projesi Oluştur
```bash
# Railway CLI yükle (isteğe bağlı)
npm i -g @railway/cli

# Railway'e login
railway login
```

### 2. Gerekli Dosyalar
✅ `app.py` - Flask uygulaması
✅ `mail_sender.py` - Mail gönderim sistemi
✅ `templates/` - HTML şablonları
✅ `requirements.txt` - Python bağımlılıkları
✅ `Procfile` - Railway start komutu
✅ `runtime.txt` - Python versiyonu
✅ `.gitignore` - Git ignore dosyası
✅ `firebase-credentials.json` - Firebase credentials
✅ `.env` - Environment variables

### 3. Environment Variables (Railway Dashboard'da ekle)
```env
GMAIL_USER_1=reliableproducts114@gmail.com
GMAIL_APP_PASSWORD_1=enuilfqrjxyofzdw

GMAIL_USER_2=reliableproducts115@gmail.com
GMAIL_APP_PASSWORD_2=maeuykjemyozlhic

GMAIL_USER_3=reliableproducts116@gmail.com
GMAIL_APP_PASSWORD_3=mnsdcbmmzvvilncc
```

### 4. Deploy
```bash
# Git repository oluştur
git init
git add .
git commit -m "Initial commit"

# Railway'e deploy
railway up
```

### 5. Firebase Credentials Ekle
Railway Dashboard'da:
1. Variables sekmesine git
2. "RAW Editor" tıkla
3. `firebase-credentials.json` içeriğini yapıştır

### 6. Domain Ayarla
Railway otomatik bir domain verir:
- `your-project.up.railway.app`

## 📊 Kullanım

### Dashboard: `/`
- İstatistikler
- Mail gönderme formu
- İlerleme takibi

### Kullanıcılar: `/users`
- Firebase kullanıcı listesi

### Veritabanı: `/database`
- Gönderilen mailler

## ⚙️ Özellikler

✅ Real-time progress tracking
✅ Background mail sending
✅ Spam önlemleri (30-90 sn arası bekleme)
✅ Hard bounce handling
✅ Blacklist sistemi
✅ Multi-account support
✅ Template sistemi

## 🔧 Günlük Limitler

- 3 hesap × 500 = **1500 mail/gün**
- Otomatik hesap rotasyonu
- Hard bounce'lar kara listeye eklenir
- 4000 mail için ~3 gün gerekir

## 📝 Notlar

1. İlk deploy 5-10 dakika sürebilir
2. Log'ları Railway Dashboard'dan takip edin
3. Database SQLite (Railway restart'ta silinir)
4. Persistent storage için PostgreSQL eklenebilir

## 🆘 Sorun Giderme

**Hata: Module not found**
→ `requirements.txt` kontrol et, `railway up` tekrar çalıştır

**Hata: Port error**
→ Railway otomatik PORT atar, kod `PORT` env var'ını kullanıyor

**Mail gönderilmiyor**
→ Environment variables'ları kontrol et
→ Gmail "Less secure apps" açık mı kontrol et (App Password kullan)

## 🔒 Güvenlik

- `.env` dosyası git'e eklenmesin
- Firebase credentials Railway'de secret olarak sakla
- HTTPS otomatik aktif (Railway)

