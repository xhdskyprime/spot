import os
import glob
import pandas as pd
from bs4 import BeautifulSoup
from datetime import timedelta

def time_to_seconds(t_str):
    if not t_str or t_str == 'nan':
        return 0
    try:
        # Format HH:MM:SS
        parts = t_str.split(':')
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        return 0
    except:
        return 0

def seconds_to_hms(total_seconds):
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def process_opd_file(filepath):
    results = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
        
        rows = soup.find_all('tr')
        for row in rows:
            tds = row.find_all('td')
            if len(tds) < 13:
                continue
            
            texts = [td.get_text(strip=True) for td in tds]
            
            # Identify data row: index 2 should be NIP (numeric, long)
            nip = texts[2].replace("'", "")
            if not (nip.isdigit() and len(nip) >= 15):
                continue
            
            nama = texts[1]
            
            # TTWM-TI usually at index 6, TTWP-TI at index 12 (based on analysis)
            ttwm_ti_str = texts[6]
            ttwp_ti_str = texts[12]
            
            sec_wm = time_to_seconds(ttwm_ti_str)
            sec_wp = time_to_seconds(ttwp_ti_str)
            total_sec = sec_wm + sec_wp
            
            # Kriteria: > 5 jam (5 * 3600 = 18000 detik)
            if total_sec > 18000:
                results.append({
                    'NIP': nip,
                    'Nama': nama,
                    'TTWM-TI': ttwm_ti_str,
                    'TTWP-TI': ttwp_ti_str,
                    'Total Jam': seconds_to_hms(total_sec),
                    'Total Detik': total_sec
                })
    except Exception as e:
        print(f"[ERROR] Gagal proses {os.path.basename(filepath)}: {e}")
    
    return results

def main():
    folder = 'laporan opd'
    files = glob.glob(os.path.join(folder, '*.xls'))
    
    if not files:
        print(f"[ERROR] Tidak ada file .xls di folder '{folder}'.")
        return

    print("="*70)
    print(" ANALISA MASALAH OPD (> 5 JAM TTWM+TTWP TI) ".center(70, "="))
    print("="*70)
    
    all_masalah = []
    for f in files:
        print(f"Menganalisa: {os.path.basename(f)}...")
        data = process_opd_file(f)
        all_masalah.extend(data)
        
    if all_masalah:
        # Sort by total seconds descending
        df = pd.DataFrame(all_masalah)
        df = df.sort_values(by='Total Detik', ascending=False)
        
        # Remove helper column
        df_export = df.drop(columns=['Total Detik'])
        
        output_file = 'analisa_opd_masalah.xlsx'
        df_export.to_excel(output_file, index=False)
        
        print("\n" + "-"*70)
        print(df_export.head(30).to_string(index=False))
        if len(df_export) > 30:
            print(f"... dan {len(df_export) - 30} data lainnya.")
        print("-" * 70)
        print(f"\n[SUKSES] Total {len(all_masalah)} pegawai ditemukan dengan akumulasi > 5 jam.")
        print(f"[INFO] Hasil disimpan di: {output_file}")
    else:
        print("\n[INFO] Tidak ditemukan pegawai dengan akumulasi > 5 jam.")
    
    print("="*70)

if __name__ == '__main__':
    main()
