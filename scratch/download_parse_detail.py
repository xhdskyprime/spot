import os
import json
import requests
from bs4 import BeautifulSoup

AUTH_FILE = 'auth.json'
with open(AUTH_FILE, 'r') as f:
    auth_data = json.load(f)
cookies = {c['name']: c['value'] for c in auth_data.get('cookies', [])}

session = requests.Session()
session.cookies.update(cookies)
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36'
})

url = "https://spot.tangerangkab.go.id/laporan/kehadiran/bulanan/cetak"
payload = {
    'nip': '200201142025042002',
    'tgl': 'April 2026',
    'par': '2' # Excel
}

print("Downloading detailed report from SPOT...")
res = session.post(url, data=payload, timeout=30)
if res.status_code == 200:
    print("Download successful. Parsing content...")
    soup = BeautifulSoup(res.text, 'html.parser')
    rows = soup.find_all('tr')
    print(f"Total rows: {len(rows)}")
    
    for r in rows:
        tds = r.find_all('td')
        txt = [td.get_text(strip=True) for td in tds]
        if len(txt) >= 8 and txt[0].isdigit():
            day_num = txt[0]
            date_str = txt[1]
            check_in = txt[2]
            check_out = txt[4]
            late_min = txt[5]
            early_min = txt[6]
            desc = txt[7] if len(txt) > 7 else ""
            print(f"Day {day_num:2} | {date_str:<12} | In: {check_in:<8} | Out: {check_out:<8} | Late: {late_min:<5} | Early: {early_min:<5} | Desc: {desc}")
else:
    print(f"Failed to download: HTTP {res.status_code}")
