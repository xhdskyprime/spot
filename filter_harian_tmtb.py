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
                    # Di SPOT, indeks ket ada di kolom ke-9 (index 8)
                    ket = cols[8].text.strip().upper()
                    if 'TMTB' in ket:
                        nama = cols[1].text.strip()
                        nip = cols[2].text.strip().replace("'", "")
                        results.append({
                            'Tanggal': date_str,
                            'NIP': nip,
                            'Nama': nama,
                            'Keterangan': 'TMTB'
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
    print("="*60)
    print(" MENFilter PEGAWAI TMTB DARI LAPORAN HARIAN ".center(60, "="))
    print("="*60)
    
    for f in files:
        data = process_file(f)
        all_data.extend(data)
        
    if all_data:
        df = pd.DataFrame(all_data)
        # Sort and Format NIP as string
        df['NIP'] = df['NIP'].astype(str)
        out_file = 'hasil_filter_tmtb.xlsx'
        df.to_excel(out_file, index=False)
        
        print("\n HASIL FILTER ".center(60, "-"))
        print(df.to_string(index=False))
        print("-" * 60)
        print(f" Selesai! Ditemukan total {len(all_data)} pegawai (TMTB).")
        print(f" Data telah disimpan dalam bentuk Excel di: {out_file}")
        print("="*60)
    else:
        print(" Selesai! Tidak ada pegawai dengan keterangan TMTB pada periode ini.")
        print("="*60)

if __name__ == '__main__':
    main()
