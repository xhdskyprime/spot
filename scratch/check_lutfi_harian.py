import os
import glob
from bs4 import BeautifulSoup
import pandas as pd

def parse_daily_reports():
    folder = 'laporan harian'
    files = glob.glob(os.path.join(folder, 'Laporan_Harian_*.xls'))
    # Sort files by date
    def get_date_key(f):
        fn = os.path.basename(f)
        dt_str = fn.replace('Laporan_Harian_', '').replace('.xls', '')
        parts = dt_str.split('-')
        return (int(parts[2]), int(parts[1]), int(parts[0])) # (YYYY, MM, DD)
    
    files.sort(key=get_date_key)
    
    records = []
    
    for f in files:
        fn = os.path.basename(f)
        date_str = fn.replace('Laporan_Harian_', '').replace('.xls', '')
        try:
            with open(f, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'html.parser')
                rows = soup.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 9:
                        nip = cols[2].text.strip().replace("'", "")
                        if nip == '199901062025041001':
                            nama = cols[1].text.strip()
                            masuk = cols[5].text.strip()
                            pulang = cols[7].text.strip()
                            ket = cols[8].text.strip()
                            records.append({
                                'Tanggal': date_str,
                                'Masuk': masuk,
                                'Pulang': pulang,
                                'Keterangan': ket
                            })
        except Exception as e:
            print(f"Error reading {fn}: {e}")
            
    df = pd.DataFrame(records)
    print(df.to_string(index=False))

parse_daily_reports()
