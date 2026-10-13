import requests
import json
import os
from bs4 import BeautifulSoup

AUTH_FILE = 'auth.json'
if not os.path.exists(AUTH_FILE):
    print("Auth file not found")
    exit(1)

with open(AUTH_FILE, 'r') as f:
    auth_data = json.load(f)

cookies = {c['name']: c['value'] for c in auth_data.get('cookies', [])}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'X-Requested-With': 'XMLHttpRequest'
}

print("Trying logabseni endpoint...")
url = "https://spot.tangerangkab.go.id/kehadiran/logabseni/pagging/0"
payload = {
    'kunkom': '11',
    'kununit': '83',
    'unit1': '',
    'unit2': '',
    'unit3': '',
    'unit4': '',
    'status': '1',
    'tgl': '11/05/2026',
    'nama': '198910112025211038'
}

try:
    res = requests.post(url, data=payload, cookies=cookies, headers=headers, timeout=10)
    print("Status:", res.status_code)
    print("Response text (first 1000 chars):")
    print(res.text[:1000])
    
    # Let's parse with BeautifulSoup to see if there's table data
    soup = BeautifulSoup(res.text, 'html.parser')
    rows = soup.find_all('tr')
    print(f"Found {len(rows)} rows in response.")
    for idx, row in enumerate(rows):
        tds = [td.get_text(strip=True) for td in row.find_all('td')]
        print(f"Row {idx}: {tds}")
except Exception as e:
    print("Error:", e)
