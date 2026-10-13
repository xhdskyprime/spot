import json
import os

har_path = "ambillog.har"
if not os.path.exists(har_path):
    print("ambillog.har not found!")
    exit(1)

with open(har_path, 'r', encoding='utf-8', errors='ignore') as f:
    data = json.load(f)

entries = data['log']['entries']
print(f"Total entries: {len(entries)}")

interesting = []
for idx, entry in enumerate(entries):
    req = entry['request']
    url = req['url']
    method = req['method']
    
    # Cari keyword terkait log atau absensi
    if 'log' in url.lower() or 'absen' in url.lower() or 'kehadiran' in url.lower() or 'sync' in url.lower() or 'pagging' in url.lower():
        resp = entry.get('response', {})
        status = resp.get('status', 0)
        
        post_data = req.get('postData', {})
        text = post_data.get('text', '')
        params = post_data.get('params', [])
        
        # Ambil contoh response text jika ada
        resp_text = resp.get('content', {}).get('text', '')[:200] # 200 karakter pertama
        
        interesting.append({
            'index': idx,
            'url': url,
            'method': method,
            'status': status,
            'postData_text': text,
            'postData_params': params,
            'resp_sample': resp_text
        })

print(f"Found {len(interesting)} interesting requests:")
for item in interesting:
    print(f"\n--- Entry #{item['index']} ---")
    print(f"URL: {item['url']}")
    print(f"Method: {item['method']}")
    print(f"Status: {item['status']}")
    if item['postData_text']:
        print(f"Post Data Text: {item['postData_text']}")
    if item['postData_params']:
        print(f"Post Data Params: {item['postData_params']}")
    print(f"Response Sample: {item['resp_sample']}")
