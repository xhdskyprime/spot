import os
import glob
import pandas as pd
from bs4 import BeautifulSoup

def process_file(filepath):
    filename = os.path.basename(filepath)
    # Pisahkan Tanggal dari nama file (misal Laporan_Harian_11-04-2026.xls)
    date_str = filename.replace('Laporan_Harian_', '').replace('.xls', '')
    
    results = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
            
            rows = soup.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 9:
                    datang = cols[5].text.strip()
                    pulang = cols[7].text.strip()
                    ket = cols[8].text.strip()
                    
                    # 1. Cek TMTB
                    if 'TMTB' in ket.upper():
                        results.append({
                            'Tanggal': date_str,
                            'NIP': cols[2].text.strip().replace("'", ""),
                            'Nama': cols[1].text.strip(),
                            'Masalah': 'TMTB',
                            'Detail': ket
                        })
                    
                    # 2. Datang Kosong & Ket Kosong
                    elif datang == "" and ket == "":
                        results.append({
                            'Tanggal': date_str,
                            'NIP': cols[2].text.strip().replace("'", ""),
                            'Nama': cols[1].text.strip(),
                            'Masalah': 'Datang Kosong',
                            'Detail': 'Jam Datang & Keterangan Kosong'
                        })
                        
                    # 3. Pulang Kosong & Ket Kosong
                    elif pulang == "" and ket == "":
                        results.append({
                            'Tanggal': date_str,
                            'NIP': cols[2].text.strip().replace("'", ""),
                            'Nama': cols[1].text.strip(),
                            'Masalah': 'Pulang Kosong',
                            'Detail': 'Jam Pulang & Keterangan Kosong'
                        })
    except Exception as e:
        print(f"Gagal memproses {filename}: {e}")
        
    return results

def main():
    folder = 'laporan harian'
    files = glob.glob(os.path.join(folder, '*.xls'))
    
    if not files:
        print("Tidak ada file laporan harian berformat .xls di folder tersebut.")
        return

    all_data = []
    print("="*70)
    print(" FILTER MASALAH ABSENSI HARIAN ".center(70, "="))
    print("="*70)
    
    for f in files:
        data = process_file(f)
        all_data.extend(data)
        
    if all_data:
        df = pd.DataFrame(all_data)
        df['NIP'] = df['NIP'].astype(str)
        out_file = 'filter harian masalah.xlsx'
        df.to_excel(out_file, index=False)
        
        print("\n HASIL FILTER ".center(70, "-"))
        # Print first 20 rows to console
        print(df.head(20).to_string(index=False))
        if len(df) > 20:
            print(f"... and {len(df) - 20} more rows.")
        print("-" * 70)
        print(f" Selesai! Ditemukan total {len(all_data)} record bermasalah.")
        print(f" Data telah disimpan dalam bentuk Excel di: {out_file}")
        print("="*70)
    else:
        print(" Selesai! Tidak ditemukan masalah absen pada periode ini.")
        print("="*70)

if __name__ == '__main__':
    main()
