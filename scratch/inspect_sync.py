import json
import os

har_file = "singkronasi terbaru.har"
if os.path.exists(har_file):
    with open(har_file, 'r', encoding='utf-8', errors='ignore') as f:
        har = json.load(f)
    
    entries = har['log']['entries']
    print(f"Total entries: {len(entries)}")
    for i, entry in enumerate(entries):
        req = entry['request']
        res = entry['response']
        url = req['url']
        method = req['method']
        status = res['status']
        post_data = req.get('postData', {}).get('text', '')
        
        print(f"\n--- Entry {i+1} ---")
        print(f"URL: {method} {url}")
        print(f"Status: {status}")
        if post_data:
            print(f"Post Data: {post_data[:200]}")
        
        res_text = res.get('content', {}).get('text', '')
        if res_text:
            print(f"Response Preview (first 200 chars): {res_text[:200]}")
