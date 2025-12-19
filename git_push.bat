@echo off
echo === Git Push to GitHub ===

git init
git remote remove origin 2>nul
git remote add origin https://github.com/kadir49884/AutoMailSender.git
git add .
git commit -m "Flask web dashboard for Railway deployment"
git branch -M main
git push -u origin main

echo.
echo === Push completed! ===
pause

