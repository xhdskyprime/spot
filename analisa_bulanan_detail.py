import os
import glob
import pandas as pd
from bs4 import BeautifulSoup

def process_monthly_detail(filepath):
    """
    Memproses file excel laporan bulanan detail (format HTML table).
    """
    results = []
    try:
        # Laporan SPOT biasanya HTML yang disave sebagai .xls/xlsx
        with open(filepath, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
        
        rows = soup.find_all('tr')
        nip = "Unknown"
        nama = "Unknown"
        
        # Cari info NIP dan Nama di header biasanya ada di baris-baris awal
        text_content = soup.get_text()
        nip_match = [line for line in text_content.split('\n') if 'NIP' in line]
        if nip_match: nip = nip_match[0].split(':')[-1].strip()
        
        nama_match = [line for line in text_content.split('\n') if 'Nama' in line]
        if nama_match: nama = nama_match[0].split(':')[-1].strip()

        issues = []
        for row in rows:
            tds = row.find_all('td')
            if len(tds) < 8: continue
            
            txt = [td.get_text(strip=True) for td in tds]
            # Baris data biasanya diawali dengan tanggal 1, 2, 3...
            if not txt[0].isdigit(): continue
            
            tgl = txt[0]
            jam_masuk = txt[3]
            jam_pulang = txt[4]
            keterangan = txt[7] if len(txt) > 7 else ""

            # Logika deteksi masalah
            if jam_masuk == "" and jam_pulang == "" and "Libur" not in keterangan:
                issues.append(f"Tgl {tgl}: Bolos (Kosong)")
            elif jam_masuk == "" and "Libur" not in keterangan:
                issues.append(f"Tgl {tgl}: Masuk Kosong")
            elif jam_pulang == "" and "Libur" not in keterangan:
                issues.append(f"Tgl {tgl}: Pulang Kosong")
            
        if issues:
            return {
                'NIP': nip,
                'Nama': nama,
                'Jumlah Masalah': len(issues),
                'Detail Masalah': "; ".join(issues)
            }
    except Exception as e:
        print(f"[ERROR] Gagal proses {os.path.basename(filepath)}: {e}")
    return None

def main():
    folder = 'laporan bulanan'
    files = glob.glob(os.path.join(folder, '*.xlsx')) + glob.glob(os.path.join(folder, '*.xls'))
    
    if not files:
        print(f"[ERROR] Tidak ada file laporan bulanan di folder '{folder}'.")
        return

    print("="*80)
    print(" ANALISA DETAIL LAPORAN BULANAN ".center(80, "="))
    print("="*80)
    
    all_results = []
    for f in files:
        print(f"Menganalisa Detail: {os.path.basename(f)}...")
        res = process_monthly_detail(f)
        if res: all_results.append(res)
        
    if all_results:
        df = pd.DataFrame(all_results)
        output = 'hasil_analisa_detail_bulanan.xlsx'
        df.to_excel(output, index=False)
        print("\n" + "-"*80)
        print(df.to_string(index=False))
        print("-" * 80)
        print(f"\n[SUKSES] Analisa selesai. {len(all_results)} pegawai bermasalah ditemukan.")
        print(f"[INFO] Hasil disimpan di: {output}")
    else:
        print("\n[INFO] Tidak ditemukan masalah pada laporan detail yang di-scan.")
    
    print("="*80)

if __name__ == '__main__':
    main()
