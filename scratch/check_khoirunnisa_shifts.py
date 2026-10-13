import os
import json
import requests
from bs4 import BeautifulSoup

def list_khoirunnisa_shifts():
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
        # Load the page to get SKPD options
        res_jadwal = session.get('https://spot.tangerangkab.go.id/utilitas/kehadiran/shift', timeout=15)
        soup_jadwal = BeautifulSoup(res_jadwal.text, 'html.parser')
        
        def get_val(sel_id):
            sel = soup_jadwal.find(id=sel_id)
            if not sel: return ''
            opt = sel.find('option', selected=True)
            if opt: return opt.get('value', '')
            opt2 = sel.find('option')
            if opt2: return opt2.get('value', '')
            return ''

        payload_pagging = {
            'kunkom': get_val('kunkom_scr'),
            'kununit': get_val('kununit_scr'),
            'unit1': get_val('unit1_scr'),
            'unit2': get_val('unit2_scr'),
            'unit3': get_val('unit3_scr'),
            'unit4': get_val('unit4_scr'),
            'nama': '',
            'tgl': tgl_filter,
            'status': 1,
            'display': 'All'
        }
        
        res_pagging = session.post(
            "https://spot.tangerangkab.go.id/utilitas/kehadiran/shift/pagging/0",
            data=payload_pagging, timeout=15
        )
        
        soup = BeautifulSoup(res_pagging.text, 'html.parser')
        rows = soup.find_all('tr')
        
        found = False
        for tr in rows:
            tds = tr.find_all('td')
            if len(tds) >= 4:
                text = tr.text
                if "khoirunnisa" in text.lower():
                    print(f"Found row: {[td.text.strip() for td in tds[:6]]}")
                    day = 1
                    for td in tds:
                        title = td.get('title', '')
                        text_code = td.text.strip().upper()
                        if "Tgl" in title or (td.get('style') and 'width:24px' in td.get('style').replace(' ', '')):
                            print(f"  Day {day:02d}: Code='{text_code}' | Info='{title}'")
                            day += 1
                    found = True
                    break
        if not found:
            print("Khoirunnisa row not found in list.")
    except Exception as e:
        print(f"Error: {e}")

list_khoirunnisa_shifts()
