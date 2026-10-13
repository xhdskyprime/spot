import pandas as pd
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import time
import os
import argparse

# Konfigurasi File Excel
EXCEL_FILE = 'data_pegawai.xlsx'
HASIL_FILE = 'hasil_data_pegawai.xlsx'
URL = 'https://spot.tangerangkab.go.id/kedinasan/piket'
AUTH_FILE = 'auth.json'

def parse_arguments():
    parser = argparse.ArgumentParser(description="Otomatisasi Input Piket SPOT")
    parser.add_argument('--headless', action='store_true', help="Jalankan murni dengan CLI tanpa membuka jendela browser (membutuhkan file auth.json)")
    parser.add_argument('--login-only', action='store_true', help="Hanya buka jendela browser untuk login dan menyimpan sesi ke auth.json")
    return parser.parse_args()

def login_and_save_session():
    print("\n[MODE LOGIN ONLY]")
    print(f"Membuka halaman {URL}...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto(URL)
        
        print("\n" + "="*50)
        print("Sila login secara manual di browser yang terbuka.")
        print("Jika sudah berhasil masuk ke Halaman Dashboard/Piket,")
        print("kembali ke terminal ini dan tekan ENTER untuk menyimpan sesi.")
        print("="*50 + "\n")
        
        input("Tekan ENTER di sini JIKA SUDAH BERHASIL LOGIN...")
        
        context.storage_state(path=AUTH_FILE)
        print(f"\n[SUKSES] Sesi login telah disimpan ke dalam {AUTH_FILE}!")
        print("Mulai sekarang kamu bisa memproses data lewat CLI murni dengan: python otomatisasi_piket.py --headless")
        browser.close()

def main():
    args = parse_arguments()

    if args.login_only:
        login_and_save_session()
        return

    print("\n" + "="*50)
    print(" BOT OTOMATISASI JADWAL SHIFT SPOT (CLI MODE)")
    print("="*50)

    if args.headless and not os.path.exists(AUTH_FILE):
        print(f"\n[ERROR] Mode --headless gagal: File {AUTH_FILE} tidak ditemukan.")
        print("Kamu harus login sekali dulu untuk menggunakan mode CLI dengan cara:")
        print("python otomatisasi_piket.py --login-only\n")
        return

    # Cek apakah file excel ada
    if not os.path.exists(EXCEL_FILE):
        print(f"[ERROR] File '{EXCEL_FILE}' tidak ditemukan.")
        return

    # Baca data excel
    try:
        df = pd.read_excel(EXCEL_FILE)
        print(f"[INFO] {len(df)} baris data ditemukan di file Excel.")
    except Exception as e:
        print(f"[ERROR] Gagal membaca excel: {e}")
        return

    # Siapkan list untuk menyimpan status
    status_list = []
    
    with sync_playwright() as p:
        if args.headless:
            print("[INFO] Menjalankan browser di background (Headless Mode)...")
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(storage_state=AUTH_FILE)
        else:
            print("[INFO] Menjalankan browser secara visual...")
            browser = p.chromium.launch(headless=False, slow_mo=500)
            if os.path.exists(AUTH_FILE):
                context = browser.new_context(storage_state=AUTH_FILE)
            else:
                context = browser.new_context()

        page = context.new_page()
        page.goto(URL)

        if not args.headless and not os.path.exists(AUTH_FILE):
            print("\n>> PERHATIAN: Kamu belum menyimpan sesi login.")
            print(">> Silakan login manual dengan cepat di browser!")
            print(">> Menunggu 30 detik...\n")
            time.sleep(30)
            # Simpan otomatis setelah 30 dtk agar nanti bisa --headless
            context.storage_state(path=AUTH_FILE)
            print(f"[INFO] Sesi disimpan ke {AUTH_FILE} untuk penggunaan berikutnya.")

        print("\n" + "-"*50)
        print(" MEMULAI PENGISIAN DATA ".center(50, " "))
        print("-"*50)

        # Mulai loop untuk setiap baris di Excel
        for index, row in df.iterrows():
            # Menggunakan NIP jika ada, jika tidak pakai Nama
            identitas = str(row['NIP']) if pd.notna(row.get('NIP')) and str(row['NIP']).strip() != '' else str(row['Nama'])
            tanggal = str(row['Tanggal'])
            
            # Nilai default sesuai kesepakatan (Otomatis)
            tgl_finger = tanggal
            jam_masuk = "08:30"
            jam_keluar = "16:30"
            tgl_bebas = tanggal
            keterangan = "Piket Rutin"

            print(f"[{index+1}/{len(df)}] Memproses: {identitas:<25}", end=" ")

            try:
                # 1. Klik Tambah Data (Warna hijau)
                page.get_by_role("button", name="Tambah Data").click(timeout=10000)
                time.sleep(1)

                # 2. Klik ikon pencarian () sebelah Nama Pegawai
                try:
                    page.locator(".fa-search").first.click(timeout=5000)
                except:
                    page.locator("span[class*='search']").first.click(timeout=5000)
                
                time.sleep(1)

                # 3. Modal Pilih Pegawai
                search_input = page.locator("input[type='text']").last
                search_input.fill(identitas)
                
                # Kita tekan enter untuk cari karena tombol kadang tertunda
                page.keyboard.press("Enter")
                time.sleep(1)
                
                page.get_by_role("button", name="Proses").click(timeout=5000)
                time.sleep(2)

                # 4. Pilih Hasil
                page.get_by_role("button", name="Pilih").first.click(timeout=5000)
                time.sleep(1)

                # 5. Tanggal Finger
                page.locator("input[name='tanggal_finger']").fill(tgl_finger)
                page.keyboard.press("Escape")
                time.sleep(1) 

                # 6. Jam Masuk
                page.locator("select[name='jam_masuk']").select_option(label=jam_masuk)

                # 7. Jam Keluar
                page.locator("select[name='jam_keluar']").select_option(label=jam_keluar)

                # 8. Tanggal Bebas Piket
                page.locator("input[name='tanggal_bebas_piket']").fill(tgl_bebas)
                page.keyboard.press("Escape")

                # 9. Keterangan
                page.locator("textarea[name='keterangan']").fill(keterangan)

                # 10. Simpan
                page.get_by_role("button", name="Simpan").click()
                time.sleep(3)
                
                print(">> [ BERHASIL ]")
                status_list.append("BERHASIL")

            except Exception as e:
                # Jika error panjang, kita buat error singkat ke CLI, tapi tulis ke log
                print(">> [ GAGAL ]")
                
                # Format log error (agar bisa dibaca di excel)
                error_msg = str(e).split('\n')[0] # Ambil baris pertama error
                status_list.append(f"GAGAL: {error_msg}")
                
                page.reload()
                time.sleep(5)

        # Simpan status dari df
        df['Status_Otomatisasi'] = status_list
        df.to_excel(HASIL_FILE, index=False)
        print("\n" + "="*50)
        print(f" Selesai! Log hasil pengisian disimpan di Excel baru:\n   -> {HASIL_FILE}")
        print("="*50 + "\n")

        # Cek apakah perlu nunggu ditutup
        if not args.headless:
            print("Browser akan ditutup otomatis dalam 5 detik.")
            time.sleep(5)
            
        browser.close()

if __name__ == '__main__':
    main()
