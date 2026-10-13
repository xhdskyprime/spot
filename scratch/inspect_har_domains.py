import json

har_path = "ambillog.har"
with open(har_path, 'r', encoding='utf-8', errors='ignore') as f:
    data = json.load(f)

entries = data['log']['entries']
domains = {}
for entry in entries:
    url = entry['request']['url']
    domain = url.split('/')[2] if '//' in url else url
    cookies = entry['request'].get('cookies', [])
    headers = entry['request'].get('headers', [])
    cookie_headers = [h for h in headers if h['name'].lower() == 'cookie']
    
    if domain not in domains:
        domains[domain] = {'count': 0, 'has_cookies_field': False, 'has_cookie_header': False}
    
    domains[domain]['count'] += 1
    if cookies:
        domains[domain]['has_cookies_field'] = True
    if cookie_headers:
        domains[domain]['has_cookie_header'] = True

print("Domain summary in ambillog.har:")
for dom, info in domains.items():
    print(f"- {dom}: Requests={info['count']}, CookiesField={info['has_cookies_field']}, CookieHeader={info['has_cookie_header']}")
