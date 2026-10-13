import json

har_file = "singkronasi terbaru.har"
with open(har_file, 'r', encoding='utf-8', errors='ignore') as f:
    har = json.load(f)

entries = har['log']['entries']
for i, entry in enumerate(entries):
    req = entry['request']
    url = req['url']
    if 'history' in url:
        res_text = entry['response'].get('content', {}).get('text', '')
        try:
            data = json.loads(res_text)
            rows = data.get('rows', [])
            if rows:
                latest = rows[0]
                print(f"Entry {i+1}: Job ID={latest.get('id')}, status={latest.get('status')}, progress={latest.get('progress')}, created={latest.get('created_at')}")
        except Exception as e:
            print(f"Entry {i+1}: parse error {e}")
