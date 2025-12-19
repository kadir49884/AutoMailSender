@echo off
title Randoo Mail Sender
color 0a

REM Projenin tam yolu
set PROJECT_PATH=C:\Users\kadir\OneDrive\Desktop\My_AI_Projects\AutoMailSender

REM Proje dizinine git
cd /d "%PROJECT_PATH%"

REM Gerekli dosyaların varlığını kontrol et
if not exist "%PROJECT_PATH%\venv" (
    echo Virtual environment bulunamadi! Lutfen once projeyi duzgun sekilde kurun.
    pause
    exit /b 1
)

if not exist "%PROJECT_PATH%\mail_gui.py" (
    echo mail_gui.py dosyasi bulunamadi!
    pause
    exit /b 1
)

if not exist "%PROJECT_PATH%\firebase-credentials.json" (
    echo firebase-credentials.json dosyasi bulunamadi!
    pause
    exit /b 1
)

if not exist "%PROJECT_PATH%\.env" (
    echo .env dosyasi bulunamadi!
    pause
    exit /b 1
)

echo Mail gonderme arayuzu baslatiliyor...

REM Virtual environment'ı aktifleştir ve uygulamayı başlat
call "%PROJECT_PATH%\venv\Scripts\activate.bat"
python "%PROJECT_PATH%\mail_gui.py"

if errorlevel 1 (
    echo Hata kodu: %errorlevel%
    pause
    exit /b %errorlevel%
)

deactivate
pause 