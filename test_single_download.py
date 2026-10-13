import os
import json
import requests
import re

# --- TESTER SINGLE DATA ---
AUTH_FILE = 'auth_download.json'

def test_single():
    print("="*60)
    print(" 🔎 TEST DOWNLOAD SATU NIP (PENGECEKAN MANUAL) ".center(60, " "))
    print("="*65)
    
    # 1. Ambil NIP yang VALID (Silakan ganti di sini jika salah)
    # Saya pakai NIP Dr Jana dari file HAR
    nip = '197105012025211011'
    tgl = 'Mei 2026'
    
    if not os.path.exists(AUTH_FILE):
        print("[!] File auth.json tidak ada.")
        return

    with open(AUTH_FILE, 'r') as f:
        auth_data = json.load(f)
    
    cookies = {c['name']: c['value'] for c in auth_data.get('cookies', [])}
    
    url = "https://spot.tangerangkab.go.id/laporan/kehadiran/bulanan/cetak"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
        'Referer': 'https://spot.tangerangkab.go.id/laporan/kehadiran/bulanan',
        'Origin': 'https://spot.tangerangkab.go.id',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    print(f"[PROCESS] Mencoba download NIP {nip} untuk {tgl}...")
    
    # par '1' (PDF) sering lebih aman untuk tes respons
    data = {'nip': nip, 'tgl': tgl, 'par': '1'}
    
    try:
        res = requests.post(url, cookies=cookies, headers=headers, data=data, timeout=30)
        
        print(f"[RESULT] Server merespon HTTP {res.status_code}")
        
        if res.status_code == 200:
            content_type = res.headers.get('Content-Type', '').lower()
            print(f"[INFO] Tipe Konten: {content_type}")
            
            if "pdf" in content_type or "excel" in content_type or len(res.content) > 5000:
                with open("test_hasil_single.pdf", "wb") as f:
                    f.write(res.content)
                print(f"[SUCCESS] BERHASIL! File disimpan ke: test_hasil_single.pdf")
                print(f"[INFO] Ukuran File: {len(res.content)} bytes")
            elif "text/html" in content_type:
                if "<!--LOGINFORM-->" in res.text:
                    print("[FAILED] Sesi Anda KADALUARSA (Dialihkan ke Login).")
                else:
                    print("[FAILED] Server membalas HTML (Bukan File). Kemungkinan data NIP/Tanggal salah.")
                    print("-" * 30)
                    print(res.text[:300]) # Intip isinya
            else:
                print(f"[FAILED] Respon tidak dikenal. Ukuran: {len(res.content)}")
    except Exception as e:
        print(f"[ERROR] Terjadi kegagalan koneksi: {e}")

if __name__ == "__main__":
    test_single()
