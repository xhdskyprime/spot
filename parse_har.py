import json

def parse_har():
    with open('spot.tangerangkab.go.id.har', 'r', encoding='utf-8') as f:
        har_data = json.load(f)
    
    entries = har_data['log']['entries']
    
    interesting_requests = []
    
    for entry in entries:
        req = entry['request']
        method = req['method']
        url = req['url']
        
        # We are looking for actions like submitting form (POST) or loading specific pages
        if method == 'POST' or 'piket' in url or 'kedinasan' in url:
            req_data = {
                'url': url,
                'method': method,
                'headers': {h['name']: h['value'] for h in req['headers'] if h['name'].lower() in ['content-type', 'cookie', 'x-requested-with', 'user-agent']},
                'postData': req.get('postData', {}).get('text', ''),
                'params': req.get('postData', {}).get('params', [])
            }
            interesting_requests.append(req_data)
            
    with open('filtered_har.json', 'w', encoding='utf-8') as f:
        json.dump(interesting_requests, f, indent=4)

if __name__ == '__main__':
    parse_har()
