import os
import json
import requests

AUTH_FILE = 'auth.json'

def test_harian():
    if not os.path.exists(AUTH_FILE):
        print("auth.json not found")
        return
    
    with open(AUTH_FILE, 'r') as f:
        auth_data = json.load(f)
    
    cookies = {c['name']: c['value'] for c in auth_data.get('cookies', [])}
    
    url = "https://spot.tangerangkab.go.id/laporan/kehadiran/harian/cetak"
    data = {
        'kunkom_scr': '4.02.01.01',
        'kununit_scr': '4.02.01.01.0010',
        'tgl_scr': '01/04/2026',
        'nama_scr': '',
        'status_scr': 'A',
        'par': '2'
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Referer': 'https://spot.tangerangkab.go.id/laporan/kehadiran/harian',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    # Try POST
    print("Testing POST /cetak...")
    res = requests.post(url, cookies=cookies, headers=headers, data=data, timeout=30)
    print("Status Code:", res.status_code)
    print("Content-Type:", res.headers.get('Content-Type'))
    print("Response text:", res.text[:200])
    
    if res.status_code == 404:
        print("Trying POST /pdf...")
        url = "https://spot.tangerangkab.go.id/laporan/kehadiran/harian/pdf"
        res = requests.post(url, cookies=cookies, headers=headers, data=data, timeout=30)
        print("Status Code:", res.status_code)
        print("Content-Type:", res.headers.get('Content-Type'))

if __name__ == "__main__":
    test_harian()
