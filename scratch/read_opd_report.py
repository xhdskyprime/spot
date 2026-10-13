import os
from bs4 import BeautifulSoup

filepath = 'laporan opd/Laporan_OPD_April_2026_200201142025042002.xls'
print(f"Reading {filepath}...")
with open(filepath, 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'html.parser')

rows = soup.find_all('tr')
print(f"Total rows: {len(rows)}")

for idx, r in enumerate(rows):
    tds = r.find_all(['td', 'th'])
    txt = [td.get_text(strip=True) for td in tds]
    print(f"Row {idx}: {txt}")
