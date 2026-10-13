import pandas as pd
import requests
import json
import os
import time
from bs4 import BeautifulSoup
import calendar

EXCEL_FILE = 'data_jadwal.xlsx'
HASIL_FILE = 'hasil_jadwal.xlsx'
AUTH_FILE = 'auth.json'

URL_PAGGING = 'https://spot.tangerangkab.go.id/utilitas/kehadiran/shift/pagging/0'
URL_SUBMIT = 'https://spot.tangerangkab.go.id/utilitas/kehadiran/shift/setHariKerja'

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36'

# Map huruf ke kode server SPOT
SHIFT_MAP = {
    'P': '1',   # Pagi
    'S': '2',   # Siang
    'M': '3',   # Malam
    'L': '99',  # Libur / Lepas
    'D': '0'    # Dinas / Default / Non-Shift
}

def get_cookies_and_headers():
    if not os.path.exists(AUTH_FILE):
        return None, None
    with open(AUTH_FILE, 'r') as f:
        auth_data = json.load(f)
    cookies = {}
    if 'cookies' in auth_data:
        for c in auth_data['cookies']:
            cookies[c['name']] = c['value']
    headers = {
        'User-Agent': USER_AGENT,
        'Accept': '*/* ',
        'X-Requested-With': 'XMLHttpRequest'
    }
    if not cookies:
        return None, None
    return cookies, headers

import argparse

def main():
    parser = argparse.ArgumentParser(description="Otomatisasi Jadwal")
    parser.add_argument('--file', type=str, default='data_jadwal.xlsx', help="File Excel input")
    args = parser.parse_args()

    EXCEL_FILE = args.file
    
    print("="*50)
    print(" BOT OTOMATISASI JADWAL SHIFT SPOT")
    print("="*50)
    
    cookies, headers = get_cookies_and_headers()
    if not cookies:
        print("[ERROR] File auth.json tidak ada! Harap jalankan: py otomatisasi_piket.py --login-only")
        return
        
    if not os.path.exists(EXCEL_FILE):
        print(f"[ERROR] File '{EXCEL_FILE}' tidak ditemukan.")
        return

    try:
        df = pd.read_excel(EXCEL_FILE)
        # Convert semua kolom jadi string biar aman, kecuali Nan
        for col in df.columns:
            df[col] = df[col].astype(str).replace('nan', '')
            
        print(f"[INFO] {len(df)} baris data/pegawai ditemukan di Excel.")
    except Exception as e:
        print(f"[ERROR] Gagal membaca Excel: {e}")
        return

    session = requests.Session()
    session.headers.update(headers)
    for k, v in cookies.items():
        session.cookies.set(k, v)

    URL_JADWAL = 'https://spot.tangerangkab.go.id/utilitas/kehadiran/shift'

    print("\n[PROSES] Mengambil konfigurasi default SKPD/Unit (Loading...)")
    res_jadwal = session.get(URL_JADWAL, timeout=15)
    
    # Cek session mati
    if 'Login' in res_jadwal.text and 'navbar' not in res_jadwal.text.lower():
        print(">> [ GAGAL FATAL: Sesi login sudah KADALUWARSA / Habis! ]")
        print("Silahkan jalankan ulang: python otomatisasi_piket.py --login-only")
        return

    soup_jadwal = BeautifulSoup(res_jadwal.text, 'html.parser')
    
    def get_val(sel_id):
        sel = soup_jadwal.find(id=sel_id)
        if not sel: return ''
        opt = sel.find('option', selected=True)
        if opt: return opt.get('value', '')
        opt2 = sel.find('option')
        if opt2: return opt2.get('value', '')
        return ''

    skpd_payload = {
        'kunkom': get_val('kunkom_scr'),
        'kununit': get_val('kununit_scr'),
        'unit1': get_val('unit1_scr'),
        'unit2': get_val('unit2_scr'),
        'unit3': get_val('unit3_scr'),
        'unit4': get_val('unit4_scr')
    }

    status_list = []

    for index, row in df.iterrows():
        nip = str(row.get('NIP', '')).strip()
        nama = str(row.get('Nama', '')).strip()
        
        # Penanganan Tanggal (Bisa String MM-YYYY atau pandas Timestamp)
        val_bt = row.get('Bulan_Tahun', '')
        if pd.isna(val_bt) or str(val_bt).strip() == '':
            status_list.append("SKIPPED: Bulan_Tahun kosong")
            continue
            
        if isinstance(val_bt, pd.Timestamp):
            bulan_int = val_bt.month
            tahun_int = val_bt.year
            bulan_tahun = f"{bulan_int:02d}-{tahun_int}"
        else:
            bulan_tahun = str(val_bt).strip()
            # Jika formatnya YYYY-MM-DD
            if len(bulan_tahun) >= 10 and '-' in bulan_tahun[:5]:
                try:
                    dt = pd.to_datetime(bulan_tahun)
                    bulan_int = dt.month
                    tahun_int = dt.year
                    bulan_tahun = f"{bulan_int:02d}-{tahun_int}"
                except:
                    pass
            
        if not nip:
            status_list.append("SKIPPED: NIP kosong")
            continue
            
        print(f"[{index+1}/{len(df)}] Memproses {nama} ({nip}) - Bulan: {bulan_tahun}")
        
        # Validasi bulan tahun (Harus MM-YYYY)
        try:
            if '-' not in bulan_tahun:
                raise ValueError
            b, t = bulan_tahun.split('-')
            bulan_int = int(b)
            tahun_int = int(t)
        except:
            print(f">> [ GAGAL: Format Bulan_Tahun salah ({bulan_tahun}), harus MM-YYYY ]")
            status_list.append("GAGAL: Format Bulan Salah")
            continue
        
        # Mapping nama bulan ke Bahasa Indonesia
        bulan_indo = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
        nama_bulan = bulan_indo[bulan_int - 1]
        tgl_filter = f"{nama_bulan} {tahun_int}"
        
        # 1. Cari user di halaman pagging untuk ambil id_hk
        payload_pagging = {
            'nama': nip,
            'tgl': tgl_filter,
            'status': 1,
            'display': 'All' # Pakai ALL untuk mencegah server nakal menyembunyikan pegawai
        }
        payload_pagging.update(skpd_payload)
        res_pagging = session.post(URL_PAGGING, data=payload_pagging, timeout=15)
        
        # Ekstrak id_hk milik user TERSEBUT saja
        soup = BeautifulSoup(res_pagging.text, 'html.parser')
        
        id_hk = '9' # Default failover
        found = False
        
        # Cari tr (row tabel) yang mengandung NIP si target
        for tr in soup.find_all('tr'):
            if nip in tr.text:
                found = True
                hk_input = tr.find('input', id='hk1')
                if hk_input:
                    id_hk = hk_input.get('value', '9')
                else:
                    id_hk = '9'
                break
                
        if not found:
            # Fallback jika tr tidak ditemukan secara pasti, cari input apapun
            hk_inputs = soup.find_all('input', {'id': lambda x: x and x.startswith('hk')})
            if not hk_inputs:
                print(">> [ GAGAL: Data pegawai ini tidak muncul di tabel jadwal SPO. Cek NIP atau SKPD! ]")
                status_list.append("GAGAL: Pegawai tidak ada di daftar jadwal")
                continue
            else:
                id_hk = hk_inputs[0].get('value', '9')
                found = True
        
        # 2. Iterate dari tanggal 1 sampai 31 dari Excel
        success_count = 0
        fail_count = 0
        
        for tgl_hari in range(1, 32):
            # Cek versi string maupun integer karena pandas sering membaca header tanggal sebagai integer
            val = row.get(str(tgl_hari))
            if pd.isna(val) or str(val).strip().lower() == 'nan':
                val = row.get(tgl_hari)

            if pd.isna(val) or str(val).strip().lower() == 'nan' or val is None:
                continue

            shift_code = str(val).strip().upper()
                
            if shift_code not in SHIFT_MAP:
                print(f"  -> Tgl {tgl_hari}: GAGAL (Kode '{shift_code}' tidak dikenal. Pakai P/S/M/L/D)")
                fail_count += 1
                continue
                
            # Bentuk tanggal format YYYY-MM-DD
            try:
                # Validasi apakah tanggal beneran ada di bulan itu (misal Feb gaada tgl 31)
                tgl_str = f"{tahun_int}-{bulan_int:02d}-{tgl_hari:02d}"
                # test
                datetime_obj = time.strptime(tgl_str, "%Y-%m-%d")
            except ValueError:
                continue # Tanggal tidak valid untuk bulan ini
                
            val_shift = SHIFT_MAP[shift_code]
            
            # 3. Request ke API
            payload_set = {
                'nip': nip,
                'tgl': tgl_str,
                'id_hk': id_hk,
                'hr': val_shift
            }
            res_set = session.post(URL_SUBMIT, data=payload_set, timeout=10)
            
            # response sukses format JSON: {"status":"sukses","msg":"Data Berhasil Diproses."}
            if res_set.status_code == 200 and 'sukses' in res_set.text.lower():
                success_count += 1
            else:
                fail_count += 1
                
            time.sleep(0.5) # Jeda per tanggal
            
        print(f"  >> [ SELESAI: {success_count} Berhasil, {fail_count} Gagal ]")
        status_list.append(f"SUKSES {success_count} hari")

    df['Status_API'] = status_list
    df.to_excel(HASIL_FILE, index=False)
    
    print("\n" + "="*50)
    print(f" Selesai! Log hasil setting jadwal:\n   -> {HASIL_FILE}")
    print("="*50 + "\n")

if __name__ == '__main__':
    main()
