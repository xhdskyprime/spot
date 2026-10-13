import requests
import json
import os
import sys
from datetime import datetime

import time

AUTH_FILE = 'auth.json'
URL_SYNC = 'https://spot.tangerangkab.go.id/utilitas/sinkronisasi/pagging'
URL_HISTORY = 'https://spot.tangerangkab.go.id/utilitas/sinkronisasi/history?page=1'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36'

def get_session():
    if not os.path.exists(AUTH_FILE):
        print(f"[ERROR] {AUTH_FILE} not found.")
        return None
    
    with open(AUTH_FILE, 'r') as f:
        auth_data = json.load(f)
    
    cookies = {c['name']: c['value'] for c in auth_data.get('cookies', [])}
    session = requests.Session()
    session.cookies.update(cookies)
    session.headers.update({
        'User-Agent': USER_AGENT,
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://spot.tangerangkab.go.id',
        'Referer': 'https://spot.tangerangkab.go.id/utilitas/sinkronisasi'
    })
    return session

def wait_for_job(session, job_id, timeout=30):
    """
    Melakukan polling ke history sinkronisasi SPOT hingga Job dengan `job_id` berstatus 'done' (100%).
    """
    start_time = time.time()
    job_str = str(job_id)
    print(f"[INFO] Menunggu Job {job_id} dalam antrian server SPOT...")
    while time.time() - start_time < timeout:
        try:
            res = session.get(URL_HISTORY, timeout=10)
            if res.status_code == 200:
                data = res.json()
                rows = data.get('rows', [])
                for row in rows:
                    if str(row.get('id')) == job_str:
                        status = str(row.get('status', '')).lower()
                        progress = str(row.get('progress', ''))
                        if status == 'done' or progress == '1':
                            print(f"[SUCCESS] Job {job_id} selesai diproses oleh SPOT (Status: {status}, Progress: 100%).")
                            return True
                        elif status in ('error', 'failed'):
                            print(f"[WARNING] Job {job_id} gagal diproses oleh server SPOT (Status: {status}).")
                            return False
                        else:
                            print(f"[INFO] Job {job_id} status: {status} (Progress: {progress}). Menunggu...")
                            break
        except Exception as e:
            print(f"[DEBUG] Gagal mengecek status antrian: {e}")
        
        time.sleep(1.5)
    
    print(f"[WARNING] Timeout ({timeout}s) menunggu Job {job_id} selesai.")
    return True

def perform_sync(nip, start_date, end_date, kunkom='11', kununit='83'):
    session = get_session()
    if not session:
        return False

    payload = {
        'kunkom': kunkom,
        'kununit': kununit,
        'unit1': '',
        'unit2': '',
        'unit3': '',
        'unit4': '',
        'awal': start_date, # Format DD/MM/YYYY
        'akhir': end_date,  # Format DD/MM/YYYY
        'nip': nip
    }

    try:
        response = session.post(URL_SYNC, data=payload, timeout=300)
        res_text = response.text.strip()
        if "OK!" in response.text or res_text.startswith("{"):
            job_id = None
            if res_text.startswith("{"):
                try:
                    res_json = response.json()
                    job_ids = res_json.get("job_ids", [])
                    if job_ids:
                        job_id = job_ids[0]
                except Exception:
                    pass
            
            if job_id:
                print(f"[SUCCESS] {nip if nip else 'Unit'}: Request sinkronisasi terkirim (Job ID: {job_id}).")
                wait_for_job(session, job_id)
            else:
                print(f"[SUCCESS] {nip if nip else 'Unit'}: Sinkronisasi Berhasil (Direct)")
                time.sleep(2)
            return True
        else:
            print(f"[WARNING] {nip if nip else 'Unit'}: Respon tidak terduga. {response.text[:100]}")
            return False
    except Exception as e:
        print(f"[ERROR] {nip}: Gagal - {e}")
        return False

if __name__ == "__main__":
    import argparse
    import pandas as pd
    
    parser = argparse.ArgumentParser(description='SPOT Attendance Synchronization via API')
    parser.add_argument('start', nargs='?', type=str, help='Start date (DD/MM/YYYY)')
    parser.add_argument('end', nargs='?', type=str, help='End date (DD/MM/YYYY)')
    parser.add_argument('--nip', type=str, help='Specific NIP to sync')
    parser.add_argument('--file', type=str, default='data_sinkronisasi.xlsx', help='Excel file with list of NIPs')
    parser.add_argument('--db', action='store_true', help='Use NIPs from pegawai.json database')
    parser.add_argument('--kunkom', type=str, default='11', help='Kunkom ID')
    parser.add_argument('--kununit', type=str, default='83', help='Kununit ID')
    
    args = parser.parse_args()

    start = args.start or datetime.now().strftime("01/%m/%Y")
    end = args.end or datetime.now().strftime("%d/%m/%Y")
    
    print("="*50)
    print("   SINKRONISASI DATA PRESENSI (API)")
    print("="*50)
    print(f"Periode: {start} s/d {end}")
    
    if args.nip:
        perform_sync(args.nip, start, end, args.kunkom, args.kununit)
    elif args.db:
        db_file = 'pegawai.json'
        if os.path.exists(db_file):
            try:
                with open(db_file, 'r') as f:
                    data = json.load(f)
                nips = [p['NIP'] for p in data if p.get('NIP') and p['NIP'] != '-']
                print(f"Ditemukan {len(nips)} NIP di {db_file}")
                for i, nip in enumerate(nips):
                    print(f"[{i+1}/{len(nips)}] ", end="")
                    perform_sync(nip, start, end, args.kunkom, args.kununit)
            except Exception as e:
                print(f"[ERROR] Gagal membaca database {db_file}: {e}")
        else:
            print(f"[ERROR] File database {db_file} tidak ditemukan.")
    elif os.path.exists(args.file):
        try:
            df = pd.read_excel(args.file)
            nips = df['NIP'].dropna().unique()
            print(f"Ditemukan {len(nips)} NIP di {args.file}")
            for i, nip in enumerate(nips):
                nip_str = str(nip).split('.')[0] # handle float
                print(f"[{i+1}/{len(nips)}] ", end="")
                perform_sync(nip_str, start, end, args.kunkom, args.kununit)
        except Exception as e:
            print(f"[ERROR] Gagal membaca file {args.file}: {e}")
    else:
        # Mencoba sinkronisasi satu unit (NIP Kosong)
        print(f"[INFO] NIP tidak diisi. Mencoba sinkronisasi seluruh unit ({args.kununit})...")
        perform_sync("", start, end, args.kunkom, args.kununit)
    
    print("\n[INFO] Selesai.")
