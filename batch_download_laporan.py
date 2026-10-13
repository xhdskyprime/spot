import os
import json
import requests
import pandas as pd
import time
import re

# --- KONFIGURASI ---
AUTH_FILE = 'auth.json'
SAVE_DIR = 'laporan bulanan'
EXCEL_FILE = 'data_download_laporan.xlsx'

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

def download_file(session, nip, tgl, fmt, retries=3, timeout=120):
    url = "https://spot.tangerangkab.go.id/laporan/kehadiran/bulanan/cetak"
    par_val = '2' if str(fmt).lower() == 'excel' else '1'
    
    # Translate month name to English for SPOT report compatibility
    tgl_eng = translate_month_to_english(tgl)
    
    data = {'nip': nip, 'tgl': tgl_eng, 'par': par_val}
    headers = {
        'User-Agent': USER_AGENT,
        'Referer': 'https://spot.tangerangkab.go.id/laporan/kehadiran/bulanan',
        'Origin': 'https://spot.tangerangkab.go.id'
    }
    
    last_err = ""
    for attempt in range(retries):
        try:
            res = session.post(url, headers=headers, data=data, timeout=timeout)
            
            if res.status_code == 200:
                if b"<!--LOGINFORM-->" in res.content:
                    return "EXPIRED"
                
                # Cek apakah isinya benar-benar file atau HTML error
                content_type = res.headers.get('Content-Type', '').lower()
                if "text/html" in content_type:
                    return "FAIL_HTML (Data tidak ada / NIP salah)"

                ext = 'xls' if par_val == '2' else 'pdf'
                # Bersihkan karakter aneh di tgl agar valid untuk nama file Windows
                tgl_safe = str(tgl).replace(' ', '_').replace(':', '-').replace('/', '-')
                filename = f"Laporan_{nip}_{tgl_safe}.{ext}"
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

def main():
    print("="*65)
    print(" BATCH DOWNLOAD LAPORAN BULANAN (REQUESTS MODE - STABLE) ".center(65, " "))
    print("="*65)
    
    if not os.path.exists(SAVE_DIR): os.makedirs(SAVE_DIR)
    session = requests.Session()
    if not load_auth_to_session(session):
        print("[ERROR] auth.json tidak ditemukan. Login dulu!")
        return

    try:
        df = pd.read_excel(EXCEL_FILE)
    except Exception as e:
        print(f"[ERROR] Gagal baca Excel: {e}")
        return

    total = len(df)
    success_count = 0
    
    for idx, row in df.iterrows():
        nip = str(row.get('NIP', '')).strip()
        
        # Penanganan Tanggal (Bisa string atau Timestamp)
        tgl_raw = row.get('BulanTahun', '')
        if isinstance(tgl_raw, pd.Timestamp):
            tgl = tgl_raw.strftime('%B %Y')
        else:
            tgl = str(tgl_raw).strip()
            
        fmt = str(row.get('Format', 'excel')).strip()
        
        if not nip or nip == 'nan' or nip == '': continue

            
        print(f"[{idx+1}/{total}] Download NIP {nip} | {tgl}...", end=" ")
        result = download_file(session, nip, tgl, fmt)
        
        if result == True:
            print(">> [ BERHASIL ]")
            success_count += 1
        elif result == "EXPIRED":
            print(">> [ GAGAL: Login Expired ]")
            break
        else:
            print(f">> [ GAGAL: {result} ]")
            
        time.sleep(1)

    print("\n" + "="*65)
    print(" DONE!")
    print(f"   - Berhasil didownload: {success_count} file")
    print(f"   - Hasil di folder: {os.path.abspath(SAVE_DIR)}")
    print("="*65 + "\n")

if __name__ == "__main__":
    main()
