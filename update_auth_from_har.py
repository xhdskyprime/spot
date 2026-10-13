import json

def get_cookies_from_har(har_path):
    with open(har_path, 'r', encoding='utf-8') as f:
        har_data = json.load(f)
        
    for entry in har_data['log']['entries']:
        request = entry['request']
        if 'tangerangkab.go.id' in request['url']:
            cookies = request.get('cookies', [])
            if cookies:
                return cookies
        # Check response just in case
        response = entry['response']
        if 'tangerangkab.go.id' in request['url']:
            cookies = response.get('cookies', [])
            if cookies:
                 # In HAR, response cookies might not have the full structure, but let's check
                 pass

    # If no explicit cookies array, parse cookie header
    for entry in har_data['log']['entries']:
        request = entry['request']
        if 'tangerangkab.go.id' in request['url']:
            for header in request['headers']:
                if header['name'].lower() == 'cookie':
                    # Parse cookie string
                    cookie_str = header['value']
                    cookies = []
                    for c in cookie_str.split(';'):
                        if '=' in c:
                            k, v = c.strip().split('=', 1)
                            cookies.append({'name': k, 'value': v})
                    return cookies
    return []

if __name__ == '__main__':
    har_files = ['ambillog.har', 'setting jadwal di spot.har', 'spot.tangerangkab.go.id.har']
    cookies = []
    for har in har_files:
        print(f"Checking {har}...")
        try:
            cookies = get_cookies_from_har(har)
            if cookies:
                print(f"Found cookies in {har}")
                break
        except Exception as e:
            print(f"Error reading {har}: {e}")
            
    if cookies:
        auth_data = {'cookies': cookies}
        with open('auth.json', 'w', encoding='utf-8') as f:
            json.dump(auth_data, f, indent=4)
        print("Updated auth.json successfully.")
    else:
        print("No cookies found in the HAR files.")
