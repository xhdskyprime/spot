import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sinkronisasi_api import perform_sync, wait_for_job, get_session

print("=== Testing Sync Polling Logic ===")

session = get_session()
if session:
    print("Session created successfully.")
    try:
        res = session.get('https://spot.tangerangkab.go.id/utilitas/sinkronisasi/history?page=1', timeout=10)
        if res.status_code == 200:
            data = res.json()
            rows = data.get('rows', [])
            print(f"History Endpoint Working. Found {len(rows)} recent jobs.")
            if rows:
                latest = rows[0]
                print(f"Most recent job: ID={latest.get('id')}, Status={latest.get('status')}, Progress={latest.get('progress')}")
                
                # Test wait_for_job with existing done job
                print("\nTesting wait_for_job polling on most recent job...")
                res_wait = wait_for_job(session, latest.get('id'), timeout=5)
                print(f"wait_for_job result: {res_wait}")
        else:
            print(f"History Endpoint returned status code {res.status_code}")
    except Exception as e:
        print(f"Error calling history endpoint: {e}")
else:
    print("Session not available (auth.json missing/expired).")

print("=== Test Complete ===")
