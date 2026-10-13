import requests
import json

month = "04-2026"

with open("d:/SPOT/auth.json", 'r') as f:
    auth_data = json.load(f)
cookies = {c['name']: c['value'] for c in auth_data.get('cookies', [])}

b, t = month.split('-')
bulan_indo = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
nama_bulan = bulan_indo[int(b) - 1]
tgl_filter = f"{nama_bulan} {t}"

res = requests.post(
    "https://spot.tangerangkab.go.id/utilitas/kehadiran/shift/pagging/0",
    data={'nama': '', 'tgl': tgl_filter, 'status': 1, 'display': 'All'},
    cookies=cookies, timeout=10
)

print("Status Code:", res.status_code)
print("Response text snippet:")
print(res.text[:1000])
