import json
import os

har_path = "ambillog.har"
with open(har_path, 'r', encoding='utf-8', errors='ignore') as f:
    data = json.load(f)

entries = data['log']['entries']
for idx, entry in enumerate(entries):
    req = entry['request']
    url = req['url']
    if 'logabseni/pagging/0' in url:
        resp = entry.get('response', {})
        text = resp.get('content', {}).get('text', '')
        with open('logabseni_response.html', 'w', encoding='utf-8') as out:
            out.write(text)
        print("Successfully extracted response to logabseni_response.html")
        break
else:
    print("Request logabseni/pagging/0 not found!")
