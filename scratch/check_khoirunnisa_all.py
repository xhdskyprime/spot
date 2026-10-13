import os
import json
import requests
from bs4 import BeautifulSoup

def list_all():
    auth_path = "auth.json"
    if not os.path.exists(auth_path):
        print("auth.json not found")
        return
    with open(auth_path, 'r') as f:
        auth_data = json.load(f)
    cookies = {c['name']: c['value'] for c in auth_data.get('cookies', [])}
    
    tgl_filter = "Mei 2026"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    session = requests.Session()
    session.headers.update(headers)
    for k, v in cookies.items():
        session.cookies.set(k, v)
        
    try:
        res_pagging = session.post(
            "https://spot.tangerangkab.go.id/utilitas/kehadiran/shift/pagging/0",
            data={
                'kunkom': '11',
                'kununit': '83',
                'unit1': '', 'unit2': '', 'unit3': '', 'unit4': '',
                'nama': '',
                'tgl': tgl_filter,
                'status': 1,
                'display': 'All'
            }, timeout=15
        )
        
        soup = BeautifulSoup(res_pagging.text, 'html.parser')
        rows = soup.find_all('tr')
        print(f"Total rows found: {len(rows)}")
        
        for tr in rows:
            tds = tr.find_all('td')
            if len(tds) >= 4:
                text = tr.text
                if "khoirunnisa" in text.lower() or "200201142025042002" in text:
                    print(f"FOUND: {tr.text[:200]}")
                    # Print daily shifts
                    day = 1
                    for td in tds:
                        title = td.get('title', '')
                        text_code = td.text.strip().upper()
                        if "Tgl" in title or (td.get('style') and 'width:24px' in td.get('style').replace(' ', '')):
                            print(f"  Day {day:02d}: Code='{text_code}' | Info='{title}'")
                            day += 1
                    return
        print("Not found anywhere in UPTD RSUD Tigaraksa (11/83) shift list.")
    except Exception as e:
        print(f"Error: {e}")

list_all()
