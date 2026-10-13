import subprocess
import time
import os
import sys

def run():
    print("\n" + "="*50)
    print("   STARTING SPOT AUTOMATION DASHBOARD")
    print("="*50 + "\n")

    # Path setup
    root_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(root_dir, "frontend")

    # 1. Start Backend
    print("[INFO] Starting Backend (FastAPI) on port 8000...")
    backend_proc = subprocess.Popen([sys.executable, "backend.py"], cwd=root_dir)

    # 2. Start Frontend
    print("[INFO] Starting Frontend (Vite) on port 5173...")
    frontend_proc = subprocess.Popen(["npm", "run", "dev"], cwd=frontend_dir, shell=True)

    print("\n" + "-"*50)
    print("   DASHBOARD IS READY!")
    print(f"   *  UI: http://localhost:5173")
    print(f"   *  Backend API: http://localhost:8000")
    print("-"*50 + "\n")
    print("Press Ctrl+C to stop both servers.")

    try:
        while True:
            time.sleep(1)
            if backend_proc.poll() is not None:
                print("[ERROR] Backend stopped unexpectedly.")
                break
            if frontend_proc.poll() is not None:
                print("[ERROR] Frontend stopped unexpectedly.")
                break
    except KeyboardInterrupt:
        print("\n[INFO] Stopping servers...")
        backend_proc.terminate()
        frontend_proc.terminate()
        print("[SUCCESS] Servers stopped.")

if __name__ == "__main__":
    run()
