import pandas as pd
import requests
import json
import os
import time
import re
from datetime import datetime, timedelta

EXCEL_FILE = 'data_pegawai_temp.xlsx' if os.path.exists('data_pegawai_temp.xlsx') else 'data_pegawai.xlsx'
HASIL_FILE = 'hasil_api_pegawai.xlsx'
AUTH_FILE = 'auth.json'

URL_SEARCH = 'https://spot.tangerangkab.go.id/home/cari_pegawai/0'
URL_SUBMIT = 'https://spot.tangerangkab.go.id/kedinasan/piket/simpan'

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36'

def get_cookies_and_headers():
    if not os.path.exists(AUTH_FILE):
        return None, None
    
    with open(AUTH_FILE, 'r') as f:
        auth_data = json.load(f)
    
    # Ambil cookies dari Playwright auth.json
    cookies = {}
    if 'cookies' in auth_data:
        for c in auth_data['cookies']:
            cookies[c['name']] = c['value']
            
    headers = {
        'User-Agent': USER_AGENT,
        'Accept': '*/* ',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    # Cek apakah session cookies tersedia
    if not cookies:
        print("[ERROR] Cookie tidak ditemukan di auth.json. Silakan login ulang via: python otomatisasi_piket.py --login-only")
        return None, None
        
    return cookies, headers

def main():
    print("="*50)
    print(" MENGGUNAKAN API UNTUK PENGISIAN CEPAT (TANPA BROWSER)")
    print("="*50)
    
    cookies, headers = get_cookies_and_headers()
    if not cookies:
        print("[ERROR] File auth.json tidak ada! Harap jalankan: python otomatisasi_piket.py --login-only")
        return
        
    if not os.path.exists(EXCEL_FILE):
        print(f"[ERROR] File '{EXCEL_FILE}' tidak ditemukan.")
        return

    try:
        df = pd.read_excel(EXCEL_FILE)
        print(f"[INFO] {len(df)} baris data ditemukan di Excel.")
    except Exception as e:
        print(f"[ERROR] Gagal membaca Excel: {e}")
        return

    session = requests.Session()
    session.headers.update(headers)
    
    for k, v in cookies.items():
        session.cookies.set(k, v)
        
    # Cek apakah sesi valid dengan melakukan query singkat
    try:
        test_r = session.post(URL_SEARCH, data={'cari':'test', 'display':10, 'noncek':1}, timeout=10)
        if "<!--LOGINFORM-->" in test_r.text:
            print("[ERROR] Sesi Login sudah EXPIRED (Kadaluarsa)!")
            print(">> Silakan login ulang untuk mengambil kunci sesi baru: python otomatisasi_piket.py --login-only")
            return
    except Exception as e:
        print(f"[ERROR] Koneksi gagal: {e}")
        return

    print("\n" + "-"*50)
    print(" MEMULAI PROSES API ".center(50, " "))
    print("-"*50)

    status_list = []

    for index, row in df.iterrows():
        nama_excel = str(row.get('Nama', '')).strip()
        nip_excel = str(row.get('NIP', '')).strip()
        
        # Penanganan Tanggal (karena pandas sering mengubah format tanggal excel jadi Timestamp)
        tgl_raw = row.get('Tanggal', '')
        if pd.isna(tgl_raw):
            tgl_raw = row.get('Tanggal_Finger', '')
            
        if isinstance(tgl_raw, pd.Timestamp):
            tgl_finger = tgl_raw.strftime('%d/%m/%Y')
        else:
            tgl_finger = str(tgl_raw).strip()
            # Jika excel baca sebagai string YYYY-MM-DD HH:MM:SS
            if len(tgl_finger) >= 10 and '-' in tgl_finger[:10]:
                try:
                    tgl_finger = pd.to_datetime(tgl_finger, dayfirst=True).strftime('%d/%m/%Y')
                except:
                    pass

        jam_masuk = str(row.get('Jam_Masuk', '')).strip()
        jam_keluar = str(row.get('Jam_Keluar', '')).strip()
        
        tgl_bebas_raw = row.get('Tanggal_Bebas', '')
        if isinstance(tgl_bebas_raw, pd.Timestamp):
            tgl_bebas = tgl_bebas_raw.strftime('%d/%m/%Y')
        else:
            tgl_bebas = str(tgl_bebas_raw).strip()
            if len(tgl_bebas) >= 10 and '-' in tgl_bebas[:10]:
                try:
                    tgl_bebas = pd.to_datetime(tgl_bebas, dayfirst=True).strftime('%d/%m/%Y')
                except:
                    pass
        
        keterangan = str(row.get('Keterangan', 'Bebas piket')).strip()
        shift = str(row.get('Shift', '')).strip().lower()

        # Fallback defaults
        if tgl_bebas.lower() == 'nan' or not tgl_bebas:
            tgl_bebas = tgl_finger
        
        if keterangan.lower() == 'nan' or not keterangan:
            keterangan = 'Bebas piket'
            
        # skip nan jika kosong
        if (nama_excel.lower() == 'nan' or not nama_excel) and (nip_excel.lower() == 'nan' or not nip_excel):
            status_list.append("SKIPPED: Nama dan NIP kosong")
            continue

        label_proses = nama_excel if nama_excel and nama_excel.lower() != 'nan' else nip_excel
        
        # Tambahkan info shift di log jika ada
        shift_label = f" (Shift {shift.title()})" if shift and shift != 'nan' else ""
        print(f"[{index+1}/{len(df)}] Memproses: {label_proses[:20]:<20}{shift_label:<15}", end=" ")
        
        try:
            nip_found = nip_excel
            nama_found = nama_excel
            
            # Jika user HANYA kasih Nama (tanpa NIP), cari dulu di web
            if not nip_excel or nip_excel.lower() == 'nan':
                payload_search = {
                    'cari': nama_excel,
                    'display': 10,
                    'noncek': 1,
                    'manual': '',
                    'nipp': ''
                }
                res_search = session.post(URL_SEARCH, data=payload_search, timeout=10)
                matches = re.findall(r"Cokot\('(\d+)','([^']+)'\)", res_search.text)
                
                if not matches:
                    print(">> [ GAGAL: Nama tidak ditemukan di pencarian ]")
                    status_list.append("GAGAL: Nama tidak ditemukan di pencarian SPOT")
                    continue
                nip_found = matches[0][0]
                nama_found = matches[0][1]
            
            # Jika user HANYA nyertain NIP, pastikan Nama minimal diisi NIP atau kita bisa bypass
            if (not nama_found or nama_found.lower() == 'nan') and nip_found:
                nama_found = "NAMA DARI EXCEL" # Fallback ringan
                
            gabung = f"{nip_found} - {nama_found}"
            
            # 2. Tarik Jam Masuk & Keluar yang sebenarnya dari Server (Endpoint: getabsen)
            payload_absen = {
                'tgl': tgl_finger,
                'nip': nip_found
            }
            res_absen = session.post('https://spot.tangerangkab.go.id/kedinasan/piket/getabsen', data=payload_absen, timeout=10)
            
            # Ekstrak dari <option value="2026-02-10 07:50:48">
            absen_matches = re.findall(r'<option value="([^"]+)">', res_absen.text)
            absen_valid = [x for x in absen_matches if x.strip() != '']
            
            jam_masuk_server = ""
            jam_keluar_server = ""
            
            if len(absen_valid) > 0:
                if shift in ['pagi', 'siang', 'malam']:
                    # Logika Shift: Cari waktu terdekat dengan jadwal yang seharusnya!
                    try:
                        base_date = datetime.strptime(tgl_finger, "%d/%m/%Y")
                        dt_options = [datetime.strptime(a, "%Y-%m-%d %H:%M:%S") for a in absen_valid]
                        
                        if shift == 'pagi':
                            target_masuk = base_date.replace(hour=7, minute=0, second=0)
                            target_keluar = base_date.replace(hour=14, minute=0, second=0)
                        elif shift == 'siang':
                            target_masuk = base_date.replace(hour=14, minute=0, second=0)
                            target_keluar = base_date.replace(hour=21, minute=0, second=0)
                        else: # malam
                            target_masuk = base_date.replace(hour=21, minute=0, second=0)
                            # shift malam pulangnya besok pagi jam 7
                            target_keluar = (base_date + timedelta(days=1)).replace(hour=7, minute=0, second=0)
                            
                        # Pilih yang terdekat dengan target masuk & keluar mutlak
                        # (menggunakan nilai absolute difference dalam hitungan detik)
                        best_masuk = min(dt_options, key=lambda x: abs((x - target_masuk).total_seconds()))
                        best_keluar = min(dt_options, key=lambda x: abs((x - target_keluar).total_seconds()))
                        
                        jam_masuk_server = best_masuk.strftime("%Y-%m-%d %H:%M:%S")
                        jam_keluar_server = best_keluar.strftime("%Y-%m-%d %H:%M:%S")
                    except Exception as e:
                        # Fallback aman jika gagal parse datetime
                        jam_masuk_server = absen_valid[0]
                        jam_keluar_server = absen_valid[-1]
                else:
                    # Non-Shift (Standard / Default): Ambil paling pertama & paling terakhir dari semua opsi
                    jam_masuk_server = absen_valid[0]
                    jam_keluar_server = absen_valid[-1]
            
            # Khusus kalau di Excelnya kosong/Pilih dari dropdown, pakai yang dari server 
            final_jam_masuk = jam_masuk_server if jam_masuk_server else (jam_masuk if jam_masuk.lower() != 'nan' else '')
            final_jam_keluar = jam_keluar_server if jam_keluar_server else (jam_keluar if jam_keluar.lower() != 'nan' else '')
            
            if not final_jam_masuk or final_jam_masuk.startswith('Pilih'):
                print(">> [ GAGAL: Tidak ada absen finger di server / data Excel kosong ]")
                status_list.append("GAGAL: Absen finger tidak ditemukan")
                continue

            # 3. Submit Data
            payload_submit = {
                'nama': gabung,
                'nip': nip_found,
                'id': '',
                'tanggal_bp': tgl_bebas,
                'masuk': final_jam_masuk,
                'telat': '0:00:00',
                'keluar': final_jam_keluar,
                'cepat': '0:00:00',
                'tanggal': tgl_finger,
                'keterangan': keterangan
            }
            
            res_submit = session.post(URL_SUBMIT, data=payload_submit, timeout=10)
            
            # Cek apakah sukses
            if res_submit.status_code == 200:
                print(">> [ BERHASIL ]")
                status_list.append("BERHASIL")
            else:
                print(f">> [ GAGAL status code: {res_submit.status_code} ]")
                status_list.append(f"GAGAL: Status API {res_submit.status_code}")
                
        except Exception as e:
            error_short = str(e).split('\n')[0]
            print(f">> [ GAGAL: {error_short[:30]}... ]")
            status_list.append(f"GAGAL: {error_short}")
            
        time.sleep(1) # Jeda ringan
        
    df['Status_API'] = status_list
    df.to_excel(HASIL_FILE, index=False)
    
    print("\n" + "="*50)
    print(f" Selesai! Log hasil pengisian API disimpan:\n   -> {HASIL_FILE}")
    print("="*50 + "\n")

if __name__ == '__main__':
    main()
