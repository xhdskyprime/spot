from bs4 import BeautifulSoup
import os

filepath = 'laporan bulanan/Laporan_200201142025042002_April_2026.xlsx'
if not os.path.exists(filepath):
    filepath = 'laporan bulanan/Laporan_200201142025042002_April_2026.xls'

print(f"Reading {filepath}...")
with open(filepath, 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'html.parser')

rows = soup.find_all('tr')
print(f"Total rows: {len(rows)}")

header = []
for row in rows:
    tds = row.find_all(['td', 'th'])
    txt = [td.get_text(strip=True) for td in tds]
    if len(txt) == 0: continue
    
    # Print general info
    if 'Nama' in txt or 'NIP' in txt:
        print(f"Info: {txt}")
    
    # Header row
    if 'No' in txt and 'Tanggal' in txt:
        header = txt
        print(f"Header: {txt}")
        continue
        
    if len(txt) >= 8 and txt[0].isdigit():
        # Data row
        # print day, date, check-in, rest, check-out, lateness, early, status
        day_num = txt[0]
        date_str = txt[1]
        check_in = txt[2]
        check_out = txt[4]
        late_min = txt[5]
        early_min = txt[6]
        desc = txt[7] if len(txt) > 7 else ""
        print(f"Day {day_num:2} | {date_str:<12} | In: {check_in:<8} | Out: {check_out:<8} | Late: {late_min:<5} | Early: {early_min:<5} | Desc: {desc}")
