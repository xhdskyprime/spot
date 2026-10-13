import json
import os

def inspect_har():
    har_path = "d:/SPOT/dinasluar dan diklat.har"
    if not os.path.exists(har_path):
        print("HAR file not found at:", har_path)
        return
        
    print("Reading HAR file...")
    with open(har_path, 'r', encoding='utf-8', errors='ignore') as f:
        har_data = json.load(f)
        
    entries = har_data['log']['entries']
    print(f"Total entries: {len(entries)}")
    
    results = []
    for i, entry in enumerate(entries):
        req = entry['request']
        url = req['url']
        method = req['method']
        
        # Look for POST requests or anything containing relevant keywords
        keywords = ['dinas', 'diklat', 'luar', 'keterangan', 'tambah', 'insert', 'save', 'submit']
        is_interesting = method == 'POST' or any(kw in url.lower() for kw in keywords)
        
        if is_interesting:
            res_status = entry.get('response', {}).get('status', 0)
            post_data = req.get('postData', {})
            post_text = post_data.get('text', '')
            post_params = post_data.get('params', [])
            
            results.append({
                'index': i,
                'method': method,
                'url': url,
                'status': res_status,
                'post_text': post_text,
                'post_params': post_params
            })
            
    # Print summary of unique URLs found
    print("\nSummary of unique URLs:")
    unique_urls = set()
    for r in results:
        unique_urls.add((r['method'], r['url']))
    for m, u in sorted(unique_urls):
        print(f"- {m} {u}")
        
    # Detail on POST requests
    print("\nDetails on POST requests:")
    for r in results:
        if r['method'] == 'POST':
            print("="*60)
            print(f"Index: {r['index']} | POST {r['url']} | Status: {r['status']}")
            print("Params:")
            if r['post_params']:
                for p in r['post_params']:
                    print(f"  {p.get('name')}: {p.get('value')}")
            else:
                print(f"  Raw: {r['post_text']}")

if __name__ == '__main__':
    inspect_har()
