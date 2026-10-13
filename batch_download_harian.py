import os
import json
import requests
import time
import pandas as pd
from datetime import datetime, timedelta

# --- KONFIGURASI ---
AUTH_FILE = 'auth.json'
SAVE_DIR = 'laporan harian'
EXCEL_FILE = 'data_download_harian.xlsx'

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

def download_harian(session, skpd1, skpd2, tgl, nip="", retries=3, timeout=120):
    url = "https://spot.tangerangkab.go.id/laporan/kehadiran/harian/pagging"
    kunkom_val = "11" if skpd1 == "4.02.01.01" else skpd1
    kununit_val = "83" if skpd2 == "4.02.01.01.0010" else skpd2

    data = {
        'kunkom': kunkom_val,
        'kununit': kununit_val,
        'unit1': '',
        'unit2': '',
        'unit3': '',
        'unit4': '',
        'tgl': tgl,
        'nama': nip,
        'status': '1',
        'param': '3'
    }
    headers = {
        'User-Agent': USER_AGENT,
        'Referer': 'https://spot.tangerangkab.go.id/laporan/kehadiran/harian',
        'Origin': 'https://spot.tangerangkab.go.id'
    }
    
    last_err = ""
    for attempt in range(retries):
        try:
            res = session.post(url, headers=headers, data=data, timeout=timeout)
            
            if res.status_code == 200:
                if b"<!--LOGINFORM-->" in res.content: return "EXPIRED"
                
                content_type = res.headers.get('Content-Type', '').lower()
                # If server gives html, it might either be EXPIRED error or just html with excel mime structure. So we do not fail it here.

                tgl_safe = tgl.replace('/', '-')
                name_part = f"_{nip}" if nip else ""
                filename = f"Laporan_Harian_{tgl_safe}{name_part}.xls"
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

def main(start_date_str=None, end_date_str=None, skpd1="4.02.01.01", skpd2="4.02.01.01.0010"):
    if not os.path.exists(SAVE_DIR): os.makedirs(SAVE_DIR)
    session = requests.Session()
    if not load_auth_to_session(session):
        print("[ERROR] auth.json tidak ditemukan. Login dulu!")
        return

    tasks = []
    # Mode Rentang Tanggal (CLI Args)
    if start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, "%d/%m/%Y")
            end_date = datetime.strptime(end_date_str, "%d/%m/%Y")
            curr = start_date
            while curr <= end_date:
                tasks.append({'tgl': curr.strftime("%d/%m/%Y"), 'skpd1': skpd1, 'skpd2': skpd2, 'nip': ''})
                curr += timedelta(days=1)
        except Exception as e:
            print(f"[ERROR] Format tanggal salah (%d/%m/%Y): {e}")
            return
            
    # Mode Excel (Default jika tidak ada args)
    elif os.path.exists(EXCEL_FILE):
        print(f"[INFO] Membaca data dari {EXCEL_FILE}...")
        try:
            df = pd.read_excel(EXCEL_FILE)
            for _, row in df.iterrows():
                tasks.append({
                    'tgl': str(row.get('Tanggal', '')).strip(),
                    'skpd1': str(row.get('SKPD1', skpd1)),
                    'skpd2': str(row.get('SKPD2', skpd2)),
                    'nip': str(row.get('NIP', '')).strip() if pd.notna(row.get('NIP')) else ''
                })
        except Exception as e:
            print(f"[ERROR] Gagal baca Excel: {e}")
            return
    else:
        print("[ERROR] Masukkan rentang tanggal atau upload data_download_harian.xlsx")
        return

    success_count = 0
    total = len(tasks)
    for idx, t in enumerate(tasks):
        if not t['tgl'] or t['tgl'] == 'nan' or t['tgl'] == '': continue
        print(f"[{idx+1}/{total}] Download {t['tgl']} {'(NIP: '+t['nip']+')' if t['nip'] else ''}...", end=" ")
        
        result = download_harian(session, t['skpd1'], t['skpd2'], t['tgl'], t['nip'])
        
        if result == True:
            print(">> [ OK ]")
            success_count += 1
        elif result == "EXPIRED":
            print(">> [ SESI HABIS ]")
            break
        else:
            print(f">> [ GAGAL: {result} ]")
        time.sleep(1)

    print("\n" + "="*50)
    print(f" Selesai! {success_count} file disimpan di:\n   -> {os.path.abspath(SAVE_DIR)}")
    print("="*50 + "\n")

if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3:
        # Args: start_date end_date skpd1 skpd2
        s = sys.argv[1]
        e = sys.argv[2]
        s1 = sys.argv[3] if len(sys.argv) > 3 else "4.02.01.01"
        s2 = sys.argv[4] if len(sys.argv) > 4 else "4.02.01.01.0010"
        main(s, e, s1, s2)
    else:
        # Defaults to Excel mode if no range args
        main()
