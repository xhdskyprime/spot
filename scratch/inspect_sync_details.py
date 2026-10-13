import json

har_file = "singkronasi terbaru.har"
with open(har_file, 'r', encoding='utf-8', errors='ignore') as f:
    har = json.load(f)

entries = har['log']['entries']
for i in range(52, len(entries)):
    entry = entries[i]
    req = entry['request']
    res = entry['response']
    url = req['url']
    if 'sinkronisasi' in url:
        print(f"\n=== Entry {i+1}: {req['method']} {url} ===")
        post_data = req.get('postData', {}).get('text', '')
        if post_data:
            print(f"Post Data: {post_data}")
        res_text = res.get('content', {}).get('text', '')
        print(f"Response: {res_text}")
