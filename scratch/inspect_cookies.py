import json

har_path = "ambillog.har"
with open(har_path, 'r', encoding='utf-8', errors='ignore') as f:
    data = json.load(f)

entries = data['log']['entries']
for idx, entry in enumerate(entries):
    req = entry['request']
    url = req['url']
    if 'logabseni/pagging/0' in url:
        print("URL:", url)
        print("Cookies field:", req.get('cookies'))
        print("Headers:")
        for h in req.get('headers', []):
            if h['name'].lower() in ['cookie', 'set-cookie']:
                print(f"Header {h['name']}: {h['value'][:200]}...")
        break
