import os
import json
import requests

def debug_options():
    auth_path = "auth.json"
    if not os.path.exists(auth_path):
        print("auth.json not found")
        return
    with open(auth_path, 'r') as f:
        auth_data = json.load(f)
    cookies = {c['name']: c['value'] for c in auth_data.get('cookies', [])}
    
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
        res_jadwal = session.get('https://spot.tangerangkab.go.id/utilitas/kehadiran/shift', timeout=15)
        print("Response length:", len(res_jadwal.text))
        print("Is login form present?", "<!--LOGINFORM-->" in res_jadwal.text or "Login" in res_jadwal.text)
        if len(res_jadwal.text) < 1000:
            print(res_jadwal.text)
    except Exception as e:
        print(f"Error: {e}")

debug_options()
