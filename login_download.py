import os
import time
from playwright.sync_api import sync_playwright

# --- CONFIG ---
AUTH_DOWNLOAD_FILE = 'auth_download.json'
URL_START = 'https://spot.tangerangkab.go.id/laporan/kehadiran/bulanan'

def login_for_download():
    print("="*65)
    print(" LOGIN SYSTEM FOR BATCH DOWNLOAD (DEDICATED) ".center(65, " "))
    print("="*65)
    
    with sync_playwright() as p:
        print("[INFO] Membuka jendela login...")
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        # Buka langsung ke halaman laporan agar sesi lari ke sana
        page.goto(URL_START)
        
        print("\n" + "!"*55)
        print(" SILAKAN LOGIN SECARA MANUAL DI BROWSER ".center(55, " "))
        print(" Sampai muncul tabel data laporan bulanan. ".center(55, " "))
        print("!"*55 + "\n")
        
        # Tunggu user di terminal
        input(">> JIKA SUDAH BERHASIL MASUK, TEKAN [ENTER] DI SINI...")
        
        # Simpan sesi ke file yang berbeda
        context.storage_state(path=AUTH_DOWNLOAD_FILE)
        print(f"\n[SUKSES] Sesi login khusus download disimpan ke: {AUTH_DOWNLOAD_FILE}")
        print("Sekarang Anda bisa menjalankan 'py batch_download_laporan.py' dengan aman.")
        print("="*55 + "\n")
        
        browser.close()

if __name__ == "__main__":
    login_for_download()
