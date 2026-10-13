@echo off
title SPOT Automation Dashboard - Setup and Run
cd /d d:\SPOT

echo ===================================================
echo   SPOT AUTOMATION DASHBOARD - SETUP ^& RUN
echo ===================================================

echo.
echo [1/3] Memeriksa dependensi Python...
py -c "import pandas, playwright, openpyxl, fastapi, uvicorn, requests, bs4" 2>nul
if %errorlevel% neq 0 (
    echo Dependensi Python belum lengkap. Menginstal sekarang...
    pip install pandas playwright openpyxl fastapi uvicorn requests beautifulsoup4
    echo Menginstal browser Playwright...
    playwright install
) else (
    echo [OK] Dependensi Python sudah lengkap.
)

echo.
echo [2/3] Memeriksa dependensi Frontend (Node.js)...
if not exist "frontend\node_modules\" (
    echo Folder node_modules tidak ditemukan. Menjalankan npm install...
    cd frontend
    call npm install
    cd ..
) else (
    echo [OK] Dependensi Frontend sudah terinstal.
)

echo.
echo [3/3] Menjalankan SPOT Automation Dashboard...
py start_dashboard.py

pause
