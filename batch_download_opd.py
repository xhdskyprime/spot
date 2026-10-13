import os
import json
import requests
import time
import pandas as pd
from datetime import datetime

# --- KONFIGURASI ---
AUTH_FILE = 'auth.json'
SAVE_DIR = 'laporan opd'
# DEFAULT SKPD (Jika tidak dikirim dari dashboard)
DEF_SKPD1 = "4.02.01.01" # Dinas Kesehatan
DEF_SKPD2 = "4.02.01.01.0010" # RSUD Tigaraksa

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36'

def load_auth_to_session(session):
    if not os.path.exists(AUTH_FILE): return False
    with open(AUTH_FILE, 'r') as f:
        data = json.load(f)
    if 'cookies' in data:
        for c in data['cookies']:
            session.cookies.set(c['name'], c['value'], domain=c.get('domain', 'spot.tangerangkab.go.id'), path=c.get('path', '/'))
        return True
    return False

def translate_month_to_english(periode_str):
    if not periode_str: return periode_str
    parts = periode_str.strip().split(' ')
    if len(parts) != 2: return periode_str
    month_name, year = parts[0], parts[1]
    translation = {
        'Januari': 'January',
        'Februari': 'February',
        'Maret': 'March',
        'April': 'April',
        'Mei': 'May',
        'Juni': 'June',
        'Juli': 'July',
        'Agustus': 'August',
        'September': 'September',
        'Oktober': 'October',
        'November': 'November',
        'Desember': 'December'
    }
    eng_month = translation.get(month_name, month_name)
    return f"{eng_month} {year}"

def download_opd(session, skpd1, skpd2, periode, nip="", retries=3, timeout=120):
    # periode format should be "Month Year" e.g. "April 2026"
    url = "https://spot.tangerangkab.go.id/laporan/kehadiran/opd/pagging"
    
    # Translate month name to English for SPOT report compatibility
    periode_eng = translate_month_to_english(periode)
    
    # Map friendly IDs if needed (from batch_download_harian pattern)
    kunkom_val = "11" if skpd1 == "4.02.01.01" else skpd1
    kununit_val = "83" if skpd2 == "4.02.01.01.0010" else skpd2

    data = {
        'kunkom': kunkom_val,
        'kununit': kununit_val,
        'unit1': '',
        'unit2': '',
        'unit3': '',
        'unit4': '',
        'tgl': periode_eng,
        'nama': nip,
        'status': '1',
        'param': '3' # 3 is usually Excel
    }
    
    headers = {
        'User-Agent': USER_AGENT,
        'Referer': 'https://spot.tangerangkab.go.id/laporan/kehadiran/opd',
        'Origin': 'https://spot.tangerangkab.go.id'
    }
    
    last_err = ""
    for attempt in range(retries):
        try:
            res = session.post(url, headers=headers, data=data, timeout=timeout)
            
            if res.status_code == 200:
                if b"<!--LOGINFORM-->" in res.content: return "EXPIRED"
                
                # Create safe filename
                safe_period = periode.replace(' ', '_').replace('"', '').replace("'", "")
                name_part = f"_{nip}" if nip else ""
                filename = f"Laporan_OPD_{safe_period}{name_part}.xls"
                filepath = os.path.join(SAVE_DIR, filename)
                
                with open(filepath, 'wb') as f:
                    f.write(res.content)
                return True
            else:
                last_err = f"HTTP_{res.status_code}"
        except Exception as e:
            last_err = str(e)
            
        if attempt < retries - 1:
            print(f"[Retry {attempt+1}/{retries}: {last_err}]", end=" ", flush=True)
            time.sleep(2 * (attempt + 1))
            
    return last_err

def main(periode=None, skpd1=DEF_SKPD1, skpd2=DEF_SKPD2, nip=""):
    if not os.path.exists(SAVE_DIR): os.makedirs(SAVE_DIR)
    
    session = requests.Session()
    if not load_auth_to_session(session):
        print("[ERROR] auth.json tidak ditemukan. Harap login terlebih dahulu!")
        return

    # Jika periode tidak diberikan, gunakan bulan sekarang
    if not periode:
        bulan_indo = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
        now = datetime.now()
        periode = f"{bulan_indo[now.month - 1]} {now.year}"
    
    print("="*50)
    print("   DOWNLOAD LAPORAN OPD (EXCEL)")
    print("="*50)
    print(f"Periode : {periode}")
    print(f"SKPD    : {skpd1} / {skpd2}")
    print(f"NIP/Nama: {nip if nip else 'ALL'}")
    print("-" * 50)

    print(f"[INFO] Memulai download...", end=" ")
    result = download_opd(session, skpd1, skpd2, periode, nip)
    
    if result == True:
        print(">> [ BERHASIL ]")
        print(f"\n[INFO] File disimpan di folder: {SAVE_DIR}")
    elif result == "EXPIRED":
        print(">> [ GAGAL: Sesi Login Habis ]")
    else:
        print(f">> [ GAGAL: {result} ]")
    
    print("="*50)

if __name__ == "__main__":
    import sys
    # Usage: py batch_download_opd.py "April 2026" "skpd1" "skpd2" "nip"
    p = sys.argv[1] if len(sys.argv) > 1 else None
    s1 = sys.argv[2] if len(sys.argv) > 2 else DEF_SKPD1
    s2 = sys.argv[3] if len(sys.argv) > 3 else DEF_SKPD2
    n = sys.argv[4] if len(sys.argv) > 4 else ""
    
    main(p, s1, s2, n)
