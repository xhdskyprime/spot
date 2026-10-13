import json
import os
import requests
import re

# --- SESI CHECKER ---
AUTH_FILE = 'auth.json'

def check_status():
    print("="*50)
    print(" 🛠️  SPOT SESSION CHECKER ".center(50, " "))
    print("="*50)

    if not os.path.exists(AUTH_FILE):
        print(" [X] Error: 'auth.json' tidak ditemukan.")
        print(" [!] Silakan jalankan 'py otomatisasi_piket.py --login-only' dulu.")
        print("="*50 + "\n")
        return

    try:
        with open(AUTH_FILE, 'r') as f:
            data = json.load(f)
        
        # Ekstrak cookie
        cookies = {c['name']: c['value'] for c in data.get('cookies', [])}
        
        # Test ke halaman Piket
        url = "https://spot.tangerangkab.go.id/kedinasan/piket"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36'
        }
        
        res = requests.get(url, cookies=cookies, headers=headers, timeout=15)
        
        if res.status_code == 200:
            # Jika ada form login, berarti session expired
            if "<!--LOGINFORM-->" in res.text:
                print(" [!] STATUS : KADALUARSA (EXPIRED)")
                print(" [!] SOLUSI : Segera login ulang di browser.")
            else:
                # Coba cari nama user di halaman
                nama_match = re.search(r"class=\"user-name\">([^<]+)</span>", res.text)
                user_info = nama_match.group(1).strip() if nama_match else "User Terdeteksi"
                
                print(f" [V] STATUS : AKTIF (VALID)")
                print(f" [V] USER   : {user_info}")
                print(f" [V] SIAP   : Sesi ini dapat digunakan untuk download batch!")
        else:
            print(f" [X] Error  : Server SPOT merespon HTTP {res.status_code}")
            
    except Exception as e:
        print(f" [X] Error  : Terjadi gangguan koneksi: {e}")

    print("="*50 + "\n")

if __name__ == "__main__":
    check_status()
