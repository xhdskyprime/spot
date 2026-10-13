import json

har_path = "ambillog.har"
with open(har_path, 'r', encoding='utf-8', errors='ignore') as f:
    data = json.load(f)

entries = data['log']['entries']
cookie_found = False
for idx, entry in enumerate(entries):
    req = entry['request']
    url = req['url']
    if 'tangerangkab.go.id' in url:
        cookies_list = req.get('cookies', [])
        headers = req.get('headers', [])
        cookie_headers = [h for h in headers if h['name'].lower() == 'cookie']
        
        if cookies_list or cookie_headers:
            print(f"Entry #{idx}: {url}")
            if cookies_list:
                print(f"  Cookies field count: {len(cookies_list)}")
            if cookie_headers:
                print(f"  Cookie header value: {cookie_headers[0]['value'][:150]}...")
            cookie_found = True

if not cookie_found:
    print("No cookies or Cookie headers found anywhere in tangerangkab.go.id requests in this HAR file.")
