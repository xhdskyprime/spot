import json
import os

def check_responses():
    har_path = "d:/SPOT/dinasluar dan diklat.har"
    if not os.path.exists(har_path):
        print("HAR file not found!")
        return

    with open(har_path, 'r', encoding='utf-8', errors='ignore') as f:
        har_data = json.load(f)

    entries = har_data['log']['entries']
    for idx, entry in enumerate(entries):
        url = entry['request']['url']
        if '/simpan' in url:
            print("="*60)
            print(f"Index: {idx} | URL: {url}")
            res = entry.get('response', {})
            print(f"Status: {res.get('status')}")
            content = res.get('content', {})
            text = content.get('text', '')
            print("Response Text Snippet:")
            print(text[:500])

if __name__ == '__main__':
    check_responses()
