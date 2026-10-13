import os
import json
import asyncio
import subprocess
import requests
from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil
import calendar
from bs4 import BeautifulSoup
import re
import pandas as pd
from datetime import datetime

from fastapi.responses import FileResponse

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PEGAWAI_DB = os.path.join(BASE_DIR, "pegawai.json")

# Ensure directories exist
os.makedirs(os.path.join(BASE_DIR, "laporan bulanan"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "laporan harian"), exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_json(self, data: dict):
        for connection in self.active_connections:
            await connection.send_json(data)

manager = ConnectionManager()

async def run_script_and_stream(script_name, args, websocket):
    cmd = ["py", script_name] + args
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        cwd=BASE_DIR
    )
    
    while True:
        line = await process.stdout.readline()
        if not line:
            break
        text = line.decode('utf-8', errors='ignore').strip()
        if text:
            await websocket.send_json({"type": "log", "data": text})
            
    await process.wait()
    await websocket.send_json({"type": "done", "status": process.returncode})

@app.get("/api/status")
async def get_status():
    auth_path = os.path.join(BASE_DIR, "auth.json")
    auth_exists = os.path.exists(auth_path)
    session_valid = False
    if auth_exists:
        try:
            with open(auth_path, 'r') as f:
                auth_data = json.load(f)
            cookies = {c['name']: c['value'] for c in auth_data.get('cookies', [])}
            res = await asyncio.to_thread(requests.get, "https://spot.tangerangkab.go.id/utilitas/kehadiran/shift", cookies=cookies, timeout=5)
            if "Login" not in res.text or "navbar" in res.text.lower():
                session_valid = True
        except:
            session_valid = False

    return {
        "auth_exists": auth_exists,
        "session_valid": session_valid,
        "status_label": "ACTIVE" if session_valid else ("EXPIRED" if auth_exists else "NONE"),
        "scripts": ["otomatisasi_piket.py", "otomatisasi_jadwal.py", "filter_absen.py", "otomatisasi_api.py", "batch_download_laporan.py", "batch_download_harian.py", "filter_harian_masalah.py", "sinkronisasi_api.py", "batch_download_opd.py"],
        "db_exists": os.path.exists(PEGAWAI_DB)
    }

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(BASE_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"status": "success", "filename": file.filename}

@app.post("/api/upload_monthly_list")
async def upload_monthly_list(file: UploadFile = File(...)):
    file_path = os.path.join(BASE_DIR, "data_download_laporan.xlsx")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"status": "success", "filename": "data_download_laporan.xlsx"}

@app.post("/api/upload_sync_list")
async def upload_sync_list(file: UploadFile = File(...)):
    file_path = os.path.join(BASE_DIR, "data_sinkronisasi.xlsx")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"status": "success", "filename": "data_sinkronisasi.xlsx"}

@app.post("/api/upload_daily_list")
async def upload_daily_list(file: UploadFile = File(...)):
    file_path = os.path.join(BASE_DIR, "data_download_harian.xlsx")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"status": "success", "filename": "data_download_harian.xlsx"}

@app.post("/api/upload_pegawai_db")
async def upload_pegawai_db(file: UploadFile = File(...)):
    try:
        temp_path = os.path.join(BASE_DIR, "temp_db.xlsx")
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        df = pd.read_excel(temp_path)
        if 'NIP' in df.columns and 'Nama' in df.columns:
            data = df[['NIP', 'Nama']].dropna().to_dict('records')
            for item in data:
                item['NIP'] = str(item['NIP']).split('.')[0]
            with open(PEGAWAI_DB, 'w') as f:
                json.dump(data, f, indent=2)
            os.remove(temp_path)
            return {"status": "success", "count": len(data)}
        else:
            return {"status": "error", "message": "Columns 'NIP' and 'Nama' not found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/monthly_detail_problems")
async def get_monthly_detail_problems(criteria: str = "ALL"):
    import glob
    from bs4 import BeautifulSoup
    folder = 'laporan bulanan'
    files = glob.glob(os.path.join(folder, '*.xlsx')) + glob.glob(os.path.join(folder, '*.xls'))
    
    months_map = {
        'Januari': '01', 'Februari': '02', 'Maret': '03', 'April': '04', 'Mei': '05', 'Juni': '06',
        'Juli': '07', 'Agustus': '08', 'September': '09', 'Oktober': '10', 'November': '11', 'Desember': '12'
    }

    all_data = []
    for filepath in files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'html.parser')
                nama, nip = "Unknown", "Unknown"
                rows = soup.find_all('tr')
                for i, row in enumerate(rows):
                    tds = row.find_all('td')
                    if len(tds) >= 3:
                        lbl = tds[0].get_text(strip=True)
                        if lbl == 'Nama': nama = tds[2].get_text(strip=True)
                        if lbl == 'NIP': nip = tds[2].get_text(strip=True).replace("'", "")

                for row in rows:
                    tds = row.find_all('td')
                    if len(tds) < 8: continue
                    txt = [td.get_text(strip=True) for td in tds]
                    if not txt[0].isdigit() or len(txt[1]) <= 2: continue

                    raw_tgl, msk, plg, tm, psw = txt[1], txt[2], txt[4], txt[5], txt[6]
                    
                    # Konversi Tanggal ke dd/mm/yyyy untuk otomasi
                    clean_tgl = raw_tgl
                    try:
                        p = raw_tgl.split(' ')
                        d = p[1].replace(',', '').zfill(2)
                        m = months_map.get(p[2], '04')
                        y = p[3]
                        clean_tgl = f"{d}/{m}/{y}"
                    except: pass

                    is_tm = tm != "" and tm != "0"
                    is_psw = psw != "" and psw != "0"
                    is_empty = (msk == "" or plg == "") and "Libur" not in (txt[8] if len(txt)>8 else "")

                    matches, issue_label = False, ""
                    if criteria == "TM" and is_tm: matches, issue_label = True, "TM"
                    elif criteria == "PSW" and is_psw: matches, issue_label = True, "PSW"
                    elif criteria == "ALL" and (is_tm or is_psw):
                        matches = True
                        if is_tm and is_psw: issue_label = "TM & PSW"
                        elif is_tm: issue_label = "TM"
                        elif is_psw: issue_label = "PSW"

                    if matches:
                        all_data.append({
                            'NIP': nip,
                            'Nama': nama,
                            'Tanggal': clean_tgl,
                            'Hari': raw_tgl,
                            'Masalah': issue_label,
                            'Detail': f"Masuk: {msk or '-'}, Pulang: {plg or '-'}",
                            'JamMasuk': msk,
                            'JamPulang': plg,
                            'TTWM': tm,
                            'TTWP': psw
                        })
        except: continue
    return all_data

@app.get("/api/opd_problems")
async def get_opd_problems():
    import glob
    from bs4 import BeautifulSoup
    folder = 'laporan opd'
    files = glob.glob(os.path.join(folder, '*.xls'))
    
    def t2s(ts):
        if not ts or ts == 'nan': return 0
        try:
            p = ts.split(':')
            return int(p[0])*3600 + int(p[1])*60 + int(p[2]) if len(p)==3 else 0
        except: return 0

    all_data = []
    for filepath in files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'html.parser')
                for row in soup.find_all('tr'):
                    tds = row.find_all('td')
                    if len(tds) < 13: continue
                    txt = [td.get_text(strip=True) for td in tds]
                    nip = txt[2].replace("'", "")
                    if nip.isdigit() and len(nip) >= 15:
                        sec = t2s(txt[6]) + t2s(txt[12])
                        if sec > 18000: # > 5 jam
                            all_data.append({
                                'NIP': nip,
                                'Nama': txt[1],
                                'TTWM': txt[6],
                                'TTWP': txt[12],
                                'Total': f"{sec//3600:02}:{(sec%3600)//60:02}:{(sec%3600)%60:02}",
                                'Seconds': sec
                            })
        except: continue
    return all_data

@app.get("/api/daily_problems")
async def get_daily_problems():
    import glob
    from bs4 import BeautifulSoup
    folder = 'laporan harian'
    files = glob.glob(os.path.join(folder, '*.xls'))
    
    all_data = []
    for filepath in files:
        filename = os.path.basename(filepath)
        date_str = filename.replace('Laporan_Harian_', '').replace('.xls', '')
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'html.parser')
                rows = soup.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 9:
                        datang = cols[5].text.strip()
                        pulang = cols[7].text.strip()
                        ket = cols[8].text.strip()
                        nip = cols[2].text.strip().replace("'", "")
                        nama = cols[1].text.strip()
                        
                        problem = None
                        detail = ""
                        if 'TMTB' in ket.upper():
                            problem = 'TMTB'
                            detail = ket
                        elif datang == "" and ket == "":
                            problem = 'Datang Kosong'
                            detail = 'Jam Datang & Keterangan Kosong'
                        elif pulang == "" and ket == "":
                            problem = 'Pulang Kosong'
                            detail = 'Jam Pulang & Keterangan Kosong'
                        
                        if problem:
                            all_data.append({
                                'Tanggal': date_str,
                                'NIP': nip,
                                'Nama': nama,
                                'Masalah': problem,
                                'Detail': detail
                            })
        except:
            continue
    return all_data

@app.get("/api/search_pegawai")
async def search_pegawai(q: str):
    if os.path.exists(PEGAWAI_DB):
        with open(PEGAWAI_DB, 'r') as f:
            db = json.load(f)
        q_low = q.lower()
        filtered = [p for p in db if q_low in p['Nama'].lower() or q_low in p['NIP']][:15]
        if filtered: return filtered
    return []

@app.get("/api/sync_pegawai")
async def sync_unit_pegawai(month: str = None):
    if month is None:
        month = datetime.now().strftime("%m-%Y")
    auth_path = os.path.join(BASE_DIR, "auth.json")
    if not os.path.exists(auth_path): return []
    with open(auth_path, 'r') as f:
        auth_data = json.load(f)
    cookies = {c['name']: c['value'] for c in auth_data.get('cookies', [])}
    try:
        b, t = month.split('-')
        bulan_indo = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
        nama_bulan = bulan_indo[int(b) - 1]
        tgl_filter = f"{nama_bulan} {t}"
        res = await asyncio.to_thread(
            requests.post,
            "https://spot.tangerangkab.go.id/utilitas/kehadiran/shift/pagging/0",
            data={'nama': '', 'tgl': tgl_filter, 'status': 1, 'display': 'All'},
            cookies=cookies, timeout=15
        )
        soup = BeautifulSoup(res.text, 'html.parser')
        results = []
        for tr in soup.find_all('tr'):
            tds = tr.find_all('td')
            if len(tds) > 3:
                nip = tds[2].text.strip()
                nama = tds[3].text.strip()
                if nip.isdigit() and len(nip) > 10:
                    results.append({"NIP": nip, "Nama": nama})
        if results:
            with open(PEGAWAI_DB, 'w') as f:
                json.dump(results, f, indent=2)
        return results
    except Exception as e:
        print(f"Sync error: {e}")
        return []

@app.get("/api/get_current_jadwal")
async def get_current_jadwal(nip: str, month: str):
    auth_path = os.path.join(BASE_DIR, "auth.json")
    if not os.path.exists(auth_path): return {}
    with open(auth_path, 'r') as f:
        auth_data = json.load(f)
    cookies = {c['name']: c['value'] for c in auth_data.get('cookies', [])}
    try:
        b, t = month.split('-')
        bulan_indo = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
        nama_bulan = bulan_indo[int(b) - 1]
        tgl_filter = f"{nama_bulan} {t}"
        res = await asyncio.to_thread(
            requests.post,
            "https://spot.tangerangkab.go.id/utilitas/kehadiran/shift/pagging/0",
            data={'nama': nip, 'tgl': tgl_filter, 'status': 1, 'display': 'All'},
            cookies=cookies, timeout=10
        )
        soup = BeautifulSoup(res.text, 'html.parser')
        shifts = {}
        target_row = None
        for tr in soup.find_all('tr'):
            if nip in tr.text: target_row = tr; break
        if target_row:
            tds = target_row.find_all('td')
            for day in range(1, 32):
                found_shift = ""
                for td in tds:
                    if f"Tgl {day} " in td.get('title', ''):
                        text = td.text.strip().upper()
                        if text in ['P','S','M','L']: found_shift = text
                        elif 'PAGI' in td.get('title',''): found_shift = 'P'
                        elif 'SIANG' in td.get('title',''): found_shift = 'S'
                        elif 'MALAM' in td.get('title',''): found_shift = 'M'
                        elif 'LIBUR' in td.get('title',''): found_shift = 'L'
                    shifts[str(day)] = found_shift
        return shifts
    except: return {}

@app.post("/api/run/jadwal_json")
async def prepare_jadwal_file(data: List[dict]):
    temp_file = os.path.join(BASE_DIR, "data_jadwal_temp.xlsx")
    df = pd.DataFrame(data)
    df.to_excel(temp_file, index=False)
    return {"status": "ready", "filename": "data_jadwal_temp.xlsx"}

@app.post("/api/run/problems_json")
async def prepare_problems_file(data: List[dict]):
    temp_file = os.path.join(BASE_DIR, "data_pegawai_temp.xlsx")
    standardized_data = []
    for p in data:
        # Menyesuaikan label masalah (TM/PSW/TMTB)
        standardized_data.append({
            'Nama Pegawai': p.get('Nama'),
            'NIP': p.get('NIP'),
            'Tanggal': p.get('Tanggal'),
            'Masalah': p.get('Masalah'),
            'Detail': p.get('Detail'),
            'SKPD 1': p.get('skpd1', "4.02.01.01"),
            'SKPD 2': p.get('skpd2', "4.02.01.01.0010")
        })
    df = pd.DataFrame(standardized_data)
    df.to_excel(temp_file, index=False)
    return {"status": "ready", "filename": "data_pegawai_temp.xlsx"}

@app.post("/api/run/prepare_monthly_download")
async def prepare_monthly_download(data: List[dict], month: str = None):
    if month is None:
        bulan_indo = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
        now = datetime.now()
        month = f"{bulan_indo[now.month - 1]} {now.year}"
    temp_file = os.path.join(BASE_DIR, "data_download_laporan.xlsx")
    df_data = []
    for p in data:
        df_data.append({
            'NIP': p.get('NIP'),
            'BulanTahun': month,
            'Format': 'excel' # Gunakan excel agar bisa dianalisa otomatis
        })
    df = pd.DataFrame(df_data)
    df.to_excel(temp_file, index=False)
    return {"status": "ready", "filename": "data_download_laporan.xlsx"}

@app.websocket("/ws/run/{script_name}")
async def websocket_run_script(websocket: WebSocket, script_name: str, args: str = ""):
    import shlex
    await websocket.accept()
    cmd_args = shlex.split(args) if args else []
    try: await run_script_and_stream(script_name, cmd_args, websocket)
    except Exception as e: await websocket.send_json({"type": "error", "data": str(e)})
    finally: await websocket.close()

@app.get("/api/download_sample/{type}")
async def download_sample(type: str):
    file_path = ""
    current_month_str = datetime.now().strftime("%m-%Y")
    if type == "jadwal":
        file_path = os.path.join(BASE_DIR, "sample_jadwal.xlsx")
        df = pd.DataFrame([{
            "NIP": "199001012015011001", "Nama": "Contoh Pegawai", "Bulan_Tahun": current_month_str,
            **{str(i): ("P" if i % 3 == 0 else ("S" if i % 3 == 1 else "M")) for i in range(1, 32)}
        }])
        df.to_excel(file_path, index=False)
    elif type == "bulanan":
        file_path = os.path.join(BASE_DIR, "sample_bulanan.xlsx")
        df = pd.DataFrame([
            {"NIP": "199001012015011001", "BulanTahun": current_month_str, "Format": "PDF"},
            {"NIP": "199001012015011002", "BulanTahun": current_month_str, "Format": "PDF"}
        ])
        df.to_excel(file_path, index=False)
    elif type == "harian":
        file_path = os.path.join(BASE_DIR, "sample_harian.xlsx")
        current_date_str_1 = datetime.now().strftime("01/%m/%Y")
        current_date_str_2 = datetime.now().strftime("02/%m/%Y")
        df = pd.DataFrame([
            {"NIP": "199001012015011001", "Tanggal": current_date_str_1},
            {"NIP": "199001012015011001", "Tanggal": current_date_str_2}
        ])
        df.to_excel(file_path, index=False)
    elif type == "sinkronisasi":
        file_path = os.path.join(BASE_DIR, "sample_sinkronisasi.xlsx")
        df = pd.DataFrame([
            {"NIP": "199001012015011001", "Nama": "Contoh Pegawai"},
            {"NIP": "199001012015011002", "Nama": "Pegawai Lain"}
        ])
        df.to_excel(file_path, index=False)
    
    
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=os.path.basename(file_path))
    return {"status": "error", "message": "Sample type not found"}

@app.post("/api/export_excel")
async def export_excel(data: List[dict]):
    temp_file = os.path.join(BASE_DIR, "exported_data.xlsx")
    df = pd.DataFrame(data)
    df.to_excel(temp_file, index=False)
    return FileResponse(temp_file, filename="exported_data.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

@app.get("/api/download_result/{type}")
async def download_result(type: str):
    file_path = ""
    if type == "tmtb":
        file_path = os.path.join(BASE_DIR, "hasil_filter_tmtb.xlsx")
    elif type == "harian_masalah":
        file_path = os.path.join(BASE_DIR, "filter harian masalah.xlsx")
    elif type == "pdf_filter":
        file_path = os.path.join(BASE_DIR, "hasil_filter.xlsx")
    elif type == "opd_masalah":
        file_path = os.path.join(BASE_DIR, "analisa_opd_masalah.xlsx")

    
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=os.path.basename(file_path))
    return {"status": "error", "message": "File not found. Please run the script first."}

@app.get("/api/get_log_absensi")
async def get_log_absensi(nip: str, date: str, skpd1: str = "4.02.01.01", skpd2: str = "4.02.01.01.0010"):
    auth_path = os.path.join(BASE_DIR, "auth.json")
    if not os.path.exists(auth_path):
        return {"status": "error", "message": "Sesi tidak ditemukan. Silakan login kembali."}
    with open(auth_path, 'r') as f:
        auth_data = json.load(f)
    cookies = {c['name']: c['value'] for c in auth_data.get('cookies', [])}
    
    kunkom = "11" if skpd1 == "4.02.01.01" else skpd1
    kununit = "83" if skpd2 == "4.02.01.01.0010" else skpd2
    
    url = "https://spot.tangerangkab.go.id/kehadiran/logabseni/pagging/0"
    payload = {
        'kunkom': kunkom,
        'kununit': kununit,
        'unit1': '', 'unit2': '', 'unit3': '', 'unit4': '',
        'status': '1',
        'tgl': date.replace("-", "/"),
        'nama': nip,
        'display': 'All'
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'X-Requested-With': 'XMLHttpRequest'
    }
    try:
        res = await asyncio.to_thread(requests.post, url, data=payload, cookies=cookies, headers=headers, timeout=15)
        if "<!--LOGINFORM-->" in res.text:
            return {"status": "expired", "message": "Sesi kedaluwarsa. Silakan login ulang."}
        
        soup = BeautifulSoup(res.text, 'html.parser')
        rows = soup.find_all('tr')
        results = []
        for row in rows:
            tds = row.find_all('td')
            if len(tds) >= 7:
                results.append({
                    'NIP': tds[1].get_text(strip=True),
                    'Nama': tds[2].get_text(strip=True),
                    'Gol': tds[3].get_text(strip=True),
                    'SerialNumber': tds[4].get_text(strip=True),
                    'Tanggal': tds[5].get_text(strip=True),
                    'IP': tds[6].get_text(strip=True)
                })
        return {"status": "success", "logs": results}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/get_shift_for_date")
async def get_shift_for_date(nip: str, date: str):
    try:
        parts = date.replace("/", "-").split("-")
        if len(parts) == 3:
            day = str(int(parts[0]))
            month_year = f"{parts[1]}-{parts[2]}"
            shifts = await get_current_jadwal(nip, month_year)
            shift = shifts.get(day, "")
            shift_names = {
                'P': 'Pagi (P)',
                'S': 'Siang (S)',
                'M': 'Malam (M)',
                'L': 'Libur (L)'
            }
            return {
                "status": "success",
                "day": day,
                "month_year": month_year,
                "shift_code": shift,
                "shift_name": shift_names.get(shift, f"Lainnya ({shift})" if shift else "Belum Diatur")
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}
    return {"status": "error", "message": "Format tanggal salah"}

@app.get("/api/post_shift_for_date")
async def post_shift_for_date(nip: str, date: str, shift: str, skpd1: str = "4.02.01.01", skpd2: str = "4.02.01.01.0010"):
    auth_path = os.path.join(BASE_DIR, "auth.json")
    if not os.path.exists(auth_path):
        return {"status": "error", "message": "Sesi tidak ditemukan. Silakan login kembali."}
    with open(auth_path, 'r') as f:
        auth_data = json.load(f)
    cookies = {c['name']: c['value'] for c in auth_data.get('cookies', [])}
    
    kunkom = "11" if skpd1 == "4.02.01.01" else skpd1
    kununit = "83" if skpd2 == "4.02.01.01.0010" else skpd2
    
    # Parsing tanggal (DD-MM-YYYY atau DD/MM/YYYY atau YYYY-MM-DD)
    parts = date.replace("/", "-").split("-")
    if len(parts) != 3:
        return {"status": "error", "message": "Format tanggal salah."}
        
    if len(parts[0]) == 4:
        # YYYY-MM-DD
        year_str = parts[0]
        month_str = parts[1]
        day_str = parts[2]
    else:
        # DD-MM-YYYY
        day_str = parts[0]
        month_str = parts[1]
        year_str = parts[2]
        
    try:
        year_int = int(year_str)
        month_int = int(month_str)
        day_int = int(day_str)
    except ValueError:
        return {"status": "error", "message": "Tanggal tidak valid (non-integer)."}
        
    tgl_str = f"{year_int}-{month_int:02d}-{day_int:02d}"
    
    bulan_indo = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
    if not (1 <= month_int <= 12):
        return {"status": "error", "message": "Bulan tidak valid."}
    nama_bulan = bulan_indo[month_int - 1]
    tgl_filter = f"{nama_bulan} {year_int}"
    
    shift_map = {
        'P': '1',   # Pagi
        'S': '2',   # Siang
        'M': '3',   # Malam
        'L': '99',  # Libur / Lepas
        'D': '0'    # Dinas / Default / Non-Shift
    }
    
    val_shift = shift_map.get(shift.upper())
    if not val_shift:
        return {"status": "error", "message": f"Kode shift '{shift}' tidak dikenal. Pakai P/S/M/L/D"}
        
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    # 1. Ambil id_hk dari pagging
    url_pagging = 'https://spot.tangerangkab.go.id/utilitas/kehadiran/shift/pagging/0'
    payload_pagging = {
        'kunkom': kunkom,
        'kununit': kununit,
        'unit1': '', 'unit2': '', 'unit3': '', 'unit4': '',
        'nama': nip,
        'tgl': tgl_filter,
        'status': 1,
        'display': 'All'
    }
    
    try:
        res_pagging = await asyncio.to_thread(requests.post, url_pagging, data=payload_pagging, cookies=cookies, headers=headers, timeout=15)
        if "<!--LOGINFORM-->" in res_pagging.text:
            return {"status": "expired", "message": "Sesi kedaluwarsa. Silakan login ulang."}
            
        soup = BeautifulSoup(res_pagging.text, 'html.parser')
        id_hk = '9'
        found = False
        for tr in soup.find_all('tr'):
            if nip in tr.text:
                found = True
                hk_input = tr.find('input', id='hk1')
                if hk_input:
                    id_hk = hk_input.get('value', '9')
                break
                
        if not found:
            # Fallback
            hk_inputs = soup.find_all('input', {'id': lambda x: x and x.startswith('hk')})
            if hk_inputs:
                id_hk = hk_inputs[0].get('value', '9')
                found = True
                
        if not found:
            return {"status": "error", "message": "Pegawai tidak muncul di daftar jadwal shift SPOT. Pastikan NIP dan SKPD sesuai."}
            
        # 2. Kirim update shift ke setHariKerja
        url_submit = 'https://spot.tangerangkab.go.id/utilitas/kehadiran/shift/setHariKerja'
        payload_set = {
            'nip': nip,
            'tgl': tgl_str,
            'id_hk': id_hk,
            'hr': val_shift
        }
        
        res_set = await asyncio.to_thread(requests.post, url_submit, data=payload_set, cookies=cookies, headers=headers, timeout=15)
        if res_set.status_code == 200 and 'sukses' in res_set.text.lower():
            return {"status": "success", "message": f"Berhasil menyetel shift {shift.upper()} pada tanggal {tgl_str}"}
        else:
            return {"status": "error", "message": f"Gagal menyetel shift. Response: {res_set.text[:100]}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/post_kedinasan")
async def post_kedinasan(nip: str, nama: str, date: str, keterangan: str, type: str, skpd1: str = "4.02.01.01", skpd2: str = "4.02.01.01.0010"):
    auth_path = os.path.join(BASE_DIR, "auth.json")
    if not os.path.exists(auth_path):
        return {"status": "error", "message": "Sesi tidak ditemukan. Silakan login kembali."}
    with open(auth_path, 'r') as f:
        auth_data = json.load(f)
    cookies = {c['name']: c['value'] for c in auth_data.get('cookies', [])}
    
    parts = date.replace("/", "-").split("-")
    if len(parts) != 3:
        return {"status": "error", "message": "Format tanggal salah."}
        
    if len(parts[0]) == 4:
        day_str = parts[2]
        month_str = parts[1]
        year_str = parts[0]
    else:
        day_str = parts[0]
        month_str = parts[1]
        year_str = parts[2]
        
    try:
        year_int = int(year_str)
        month_int = int(month_str)
        day_int = int(day_str)
    except ValueError:
        return {"status": "error", "message": "Tanggal tidak valid."}
        
    formatted_date = f"{day_int:02d}/{month_int:02d}/{year_int}"
    
    payload = {
        'nama': f"{nama}; ",
        'nip': f"{nip}|",
        'id': '',
        'tanggal': formatted_date,
        'tanggal2': formatted_date,
        'keterangan': keterangan
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    try:
        url = "https://spot.tangerangkab.go.id/kedinasan/dinas/simpan" if type == "dinas" else "https://spot.tangerangkab.go.id/kedinasan/diklat/simpan"
        res = await asyncio.to_thread(requests.post, url, data=payload, cookies=cookies, headers=headers, timeout=15)
        
        if "<!--LOGINFORM-->" in res.text:
            return {"status": "expired", "message": "Sesi kedaluwarsa. Silakan login ulang."}
            
        try:
            res_json = res.json()
            if res_json.get("status") == "sukses":
                return {"status": "success", "message": f"Berhasil menyimpan kedinasan {type.upper()}: {res_json.get('msg', '')}"}
            else:
                return {"status": "error", "message": f"Gagal menyimpan: {res_json.get('msg', 'Response status bukan sukses')}"}
        except:
            if res.status_code == 200 and ("sukses" in res.text.lower() or "berhasil" in res.text.lower()):
                return {"status": "success", "message": f"Berhasil menyimpan kedinasan {type.upper()}."}
            else:
                return {"status": "error", "message": f"Gagal menyimpan. Response: {res.text[:100]}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/sync_single")
async def sync_single(nip: str, date: str, skpd1: str = "4.02.01.01", skpd2: str = "4.02.01.01.0010", end_date: str = None):
    from sinkronisasi_api import perform_sync
    norm_date = date.replace("-", "/")
    norm_end_date = end_date.replace("-", "/") if end_date else norm_date
    kunkom = "11" if skpd1 == "4.02.01.01" else skpd1
    kununit = "83" if skpd2 == "4.02.01.01.0010" else skpd2
    
    loop = asyncio.get_event_loop()
    success = await loop.run_in_executor(None, perform_sync, nip, norm_date, norm_end_date, kunkom, kununit)
    return {"status": "success" if success else "error"}

@app.get("/api/get_daily_report")
async def get_daily_report(nip: str, date: str, skpd1: str = "4.02.01.01", skpd2: str = "4.02.01.01.0010"):
    auth_path = os.path.join(BASE_DIR, "auth.json")
    if not os.path.exists(auth_path):
        return {"status": "error", "message": "Sesi tidak ditemukan. Silakan login kembali."}
    with open(auth_path, 'r') as f:
        auth_data = json.load(f)
    cookies = {c['name']: c['value'] for c in auth_data.get('cookies', [])}
    
    kunkom = "11" if skpd1 == "4.02.01.01" else skpd1
    kununit = "83" if skpd2 == "4.02.01.01.0010" else skpd2
    
    url = "https://spot.tangerangkab.go.id/laporan/kehadiran/harian/pagging/0"
    payload = {
        'kunkom': kunkom,
        'kununit': kununit,
        'unit1': '', 'unit2': '', 'unit3': '', 'unit4': '',
        'nama': nip,
        'status': '1',
        'tgl': date.replace("-", "/"),
        'display': 'All'
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'X-Requested-With': 'XMLHttpRequest'
    }
    try:
        res = await asyncio.to_thread(requests.post, url, data=payload, cookies=cookies, headers=headers, timeout=15)
        if "<!--LOGINFORM-->" in res.text:
            return {"status": "expired", "message": "Sesi kedaluwarsa. Silakan login ulang."}
        
        soup = BeautifulSoup(res.text, 'html.parser')
        rows = soup.find_all('tr')
        report = None
        for row in rows:
            tds = row.find_all('td')
            if len(tds) >= 9:
                row_nip = tds[1].get_text(strip=True).replace("'", "")
                if row_nip == nip:
                    report = {
                        'NIP': row_nip,
                        'Nama': tds[2].get_text(strip=True),
                        'Gol': tds[3].get_text(strip=True),
                        'Jabatan': tds[4].get_text(strip=True),
                        'Masuk': tds[5].get_text(strip=True),
                        'Istirahat': tds[6].get_text(strip=True),
                        'Pulang': tds[7].get_text(strip=True),
                        'Keterangan': tds[8].get_text(strip=True)
                    }
                    break
        if report:
            return {"status": "success", "report": report}
        else:
            return {"status": "success", "report": None, "message": "Pegawai tidak ditemukan di Laporan Harian untuk tanggal ini."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def parse_date(date_str: str):
    import datetime
    for fmt in ("%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unknown date format: {date_str}")

def is_tanggal_merah(date_str: str) -> bool:
    try:
        d = parse_date(date_str)
    except:
        return False
    if d.weekday() in (5, 6): # 5: Sabtu, 6: Minggu
        return True
    
    # Hari Libur Nasional Indonesia 2026 (Format YYYY-MM-DD)
    holidays_2026 = {
        "2026-01-01", # Tahun Baru Masehi
        "2026-01-15", # Isra Mikraj
        "2026-02-17", # Imlek
        "2026-03-19", # Nyepi
        "2026-04-03", # Wafat Yesus Kristus
        "2026-04-05", # Kebangkitan Yesus Kristus
        "2026-04-17", # Idul Fitri
        "2026-04-18", # Idul Fitri
        "2026-04-20", # Cuti Bersama
        "2026-04-21", # Cuti Bersama
        "2026-04-22", # Cuti Bersama
        "2026-04-23", # Cuti Bersama
        "2026-05-01", # Hari Buruh
        "2026-05-13", # Waisak
        "2026-05-14", # Kenaikan Yesus Kristus
        "2026-06-01", # Hari Lahir Pancasila
        "2026-06-27", # Idul Adha
        "2026-07-17", # Tahun Baru Islam
        "2026-08-17", # Kemerdekaan RI
        "2026-08-25", # Maulid Nabi
        "2026-12-25", # Natal
    }
    return d.strftime("%Y-%m-%d") in holidays_2026

def parse_time_to_seconds(t_str: str) -> int:
    if not t_str:
        return -1
    try:
        parts = list(map(int, t_str.split(':')))
        if len(parts) == 3:
            return parts[0]*3600 + parts[1]*60 + parts[2]
        elif len(parts) == 2:
            return parts[0]*3600 + parts[1]*60
    except:
        pass
    return -1

@app.get("/api/auto_resolve_single")
async def auto_resolve_single(nip: str, date: str, skpd1: str = "4.02.01.01", skpd2: str = "4.02.01.01.0010"):
    is_merah = is_tanggal_merah(date)
    
    # Step 1: Ambil log mentah
    logs_res = await get_log_absensi(nip, date, skpd1, skpd2)
    if logs_res.get("status") != "success":
        return {"status": "review_manual", "reason": "log_error", "message": f"Review Manual: Gagal mengambil log mentah ({logs_res.get('message')})."}
    
    logs = logs_res.get("logs", [])
    
    # Aturan A: Tanggal Merah & Tidak Ada Log -> Setel Libur (L)
    if is_merah and not logs:
        shift_res = await post_shift_for_date(nip, date, 'L', skpd1, skpd2)
        if shift_res.get("status") != "success":
            return {"status": "error", "message": f"Gagal menyetel shift L di SPOT. Detail: {shift_res.get('message')}"}
            
        sync_res = await sync_single(nip, date, skpd1, skpd2)
        if sync_res.get("status") != "success":
            return {"status": "error", "message": "Gagal sinkronisasi data ke SPOT."}
            
        report_res = await get_daily_report(nip, date, skpd1, skpd2)
        if report_res.get("status") != "success":
            return {"status": "review_manual", "reason": "verify_error", "message": f"Review Manual: Libur disetel, verifikasi gagal ({report_res.get('message')})."}
            
        return {
            "status": "success",
            "detected_shift": "L",
            "message": "Sukses! Hari libur/akhir pekan tanpa log otomatis disetel Libur (L)."
        }
        
    if not logs:
        return {"status": "review_manual", "reason": "no_logs", "message": "Review Manual: Tidak ada data log tapping finger."}
        
    # Step 2: Analisa log & Deteksi shift
    times = []
    for log in logs:
        try:
            t_str = log.get('Tanggal', '')
            time_part = t_str.split(' ')[1]
            h, m, s = map(int, time_part.split(':'))
            times.append(h * 3600 + m * 60 + s)
        except:
            continue
            
    if not times:
        return {"status": "review_manual", "reason": "parse_error", "message": "Review Manual: Gagal menganalisa waktu log tapping."}
        
    # Aturan B: Tanggal Merah & Tapping Tidak Sinkron / Checkout Pagi
    is_rule_b_triggered = False
    reason_rule_b = ""
    
    if max(times) < 9.5 * 3600:
        if is_merah:
            is_rule_b_triggered = True
            reason_rule_b = "Semua log tapping di bawah pukul 09:30 pagi pada hari libur (checkout shift malam)"
        else:
            # Hari kerja biasa, check if previous day had a night shift entry (after 19:30)
            try:
                import datetime
                prev_date_obj = parse_date(date) - datetime.timedelta(days=1)
                prev_date_str = prev_date_obj.strftime("%d-%m-%Y")
                prev_logs_res = await get_log_absensi(nip, prev_date_str, skpd1, skpd2)
                if prev_logs_res.get("status") == "success":
                    prev_logs = prev_logs_res.get("logs", [])
                    has_prev_night_entry = False
                    for pl in prev_logs:
                        try:
                            t_str = pl.get('Tanggal', '')
                            time_part = t_str.split(' ')[1]
                            h, m, s = map(int, time_part.split(':'))
                            if h >= 19 and m >= 30 or h > 19:
                                has_prev_night_entry = True
                                break
                        except:
                            continue
                    if has_prev_night_entry:
                        is_rule_b_triggered = True
                        reason_rule_b = f"Hari Lepas Malam (ada tapping malam pada tanggal {prev_date_str} dan hanya checkout pagi ini)"
            except Exception as e:
                print(f"Error checking previous day logs: {e}")
    elif is_merah:
        # Check if check_out < check_in on a holiday
        report_res = await get_daily_report(nip, date, skpd1, skpd2)
        if report_res.get("status") == "success" and report_res.get("report"):
            report = report_res.get("report")
            masuk_str = report.get('Masuk', '')
            pulang_str = report.get('Pulang', '')
            masuk_sec = parse_time_to_seconds(masuk_str)
            pulang_sec = parse_time_to_seconds(pulang_str)
            if masuk_sec >= 0 and pulang_sec >= 0 and pulang_sec < masuk_sec:
                is_rule_b_triggered = True
                reason_rule_b = f"Tapping tidak sinkron pada hari libur (Pulang {pulang_str} < Masuk {masuk_str})"
                    
    if is_rule_b_triggered:
        shift_res = await post_shift_for_date(nip, date, 'L', skpd1, skpd2)
        if shift_res.get("status") != "success":
            return {"status": "error", "message": f"Gagal menyetel shift L di SPOT. Detail: {shift_res.get('message')}"}
            
        sync_res = await sync_single(nip, date, skpd1, skpd2)
        if sync_res.get("status") != "success":
            return {"status": "error", "message": "Gagal sinkronisasi data ke SPOT."}
            
        report_res = await get_daily_report(nip, date, skpd1, skpd2)
        if report_res.get("status") != "success":
            return {"status": "review_manual", "reason": "verify_error", "message": f"Review Manual: Libur disetel, verifikasi gagal ({report_res.get('message')})."}
            
        return {
            "status": "success",
            "detected_shift": "L",
            "message": f"Sukses! Hari libur/lepas otomatis disetel Libur (L) karena: {reason_rule_b}."
        }
        
    scores = {'P': 0, 'S': 0, 'M': 0, 'Non-Shift': 0}
    
    # Analisa waktu tapping
    has_morning_entry = any(5 <= (t/3600.0) <= 9.5 for t in times)
    has_afternoon_entry = any(12.5 <= (t/3600.0) <= 15.5 for t in times)
    has_night_entry = any(19.0 <= (t/3600.0) <= 23.9 for t in times)
    
    has_afternoon_exit = any(13.5 <= (t/3600.0) <= 16.5 for t in times)
    has_evening_exit = any(20.0 <= (t/3600.0) <= 22.5 for t in times)
    
    # Cek log besok hari (H+1) untuk shift malam (checkout pagi H+1)
    has_next_morning_exit = False
    next_date_str = None
    if has_night_entry or (has_morning_entry and not has_afternoon_exit and not has_afternoon_entry):
        try:
            import datetime
            d_obj = parse_date(date)
            next_date_obj = d_obj + datetime.timedelta(days=1)
            next_date_str = next_date_obj.strftime("%d-%m-%Y")
            
            next_logs_res = await get_log_absensi(nip, next_date_str, skpd1, skpd2)
            if next_logs_res.get("status") == "success":
                next_logs = next_logs_res.get("logs", [])
                for nl in next_logs:
                    try:
                        t_str = nl.get('Tanggal', '')
                        time_part = t_str.split(' ')[1]
                        h, m, s = map(int, time_part.split(':'))
                        if h < 10:  # Checkout pagi di H+1
                            has_next_morning_exit = True
                            break
                    except:
                        continue
        except Exception as e:
            print(f"Error checking next day logs: {e}")
    
    # Pagi
    if has_morning_entry and has_afternoon_exit:
        scores['P'] += 10
    elif has_morning_entry:
        scores['P'] += 3
    elif has_afternoon_exit:
        scores['P'] += 3
        
    # Siang (Kombinasi Entry Siang 13:00 + Exit Malam 21:00)
    if has_afternoon_entry and has_evening_exit:
        scores['S'] += 15  # Tapping masuk siang + pulang malam = SHIFT SIANG PASTI
    elif has_afternoon_entry:
        scores['S'] += 5
    elif has_evening_exit and not has_night_entry:
        scores['S'] += 3
        
    # Malam (Penanganan Irisan: Hanya diprioritaskan jika TIDAK ADA entry siang 12:30-15:30)
    if has_night_entry:
        if not has_afternoon_entry:
            scores['M'] += 15  # Tapping malam tanpa entry siang = SHIFT MALAM
            if has_next_morning_exit:
                scores['M'] += 20  # Ada checkout H+1 = SHIFT MALAM PASTI
        else:
            # Jika ada entry siang, jam malam di 20:00-22:00 adalah JAM PULANG Shift Siang!
            scores['S'] += 10
        
    if has_morning_entry and not has_afternoon_exit and not has_afternoon_entry:
        scores['M'] += 2
        
    # Non-Shift (Standard Office Hour)
    has_std_entry = any(7 <= (t/3600.0) <= 9 for t in times)
    has_std_exit = any(15.5 <= (t/3600.0) <= 18 for t in times)
    if has_std_entry and has_std_exit:
        scores['Non-Shift'] += 12
        
    best_shift = max(scores, key=scores.get)
    if scores[best_shift] == 0:
        return {"status": "review_manual", "reason": "unknown_shift", "message": "Review Manual: Pola tapping tidak cocok dengan shift P/S/M/D."}
    elif best_shift == 'Non-Shift':
        detected_shift = 'D'
    else:
        detected_shift = best_shift
        
    # Step 3: Setel jadwal shift
    shift_res = await post_shift_for_date(nip, date, detected_shift, skpd1, skpd2)
    if shift_res.get("status") != "success":
        return {"status": "error", "message": f"Gagal menyetel shift di SPOT. Detail: {shift_res.get('message')}"}
        
    # Step 4: Sinkronisasi (Jika Shift Malam dan ada log checkout H+1, sinkronkan rentang H s/d H+1)
    if detected_shift == 'M' and next_date_str:
        sync_res = await sync_single(nip, date, skpd1, skpd2, end_date=next_date_str)
    else:
        sync_res = await sync_single(nip, date, skpd1, skpd2)
        
    if sync_res.get("status") != "success":
        return {"status": "error", "message": "Gagal sinkronisasi data ke SPOT."}
        
    # Step 5: Verifikasi Akhir
    report_res = await get_daily_report(nip, date, skpd1, skpd2)
    if report_res.get("status") != "success":
        return {"status": "review_manual", "reason": "verify_error", "message": f"Review Manual: Sinkronisasi berhasil, tetapi verifikasi gagal ({report_res.get('message')})."}
        
    report = report_res.get("report")
    if not report:
        return {"status": "review_manual", "reason": "no_report", "message": "Review Manual: Laporan harian tidak ditemukan setelah sinkronisasi."}
        
    masuk = report.get('Masuk', '')
    pulang = report.get('Pulang', '')
    ket = report.get('Keterangan', '')
    
    # Cek apakah masih kosong atau ada TMTB (kecuali jika ada keterangan Dinas/Diklat)
    is_kedinasan = any(k in ket.lower() for k in ["dinas", "diklat"])
    
    # Penanganan Khusus Shift Malam (M): Jam pulang berada di H+1 pagi
    if detected_shift == 'M':
        if not is_kedinasan and 'TMTB' in ket.upper():
            return {
                "status": "review_manual",
                "reason": "unresolved_gap",
                "detected_shift": detected_shift,
                "message": f"Review Manual: Status TMTB pada Shift Malam. Masuk: {masuk or 'Kosong'}, Pulang: {pulang or 'Kosong'}, Ket: {ket or '-'}"
            }
        if masuk:
            plg_display = pulang if pulang else ("Checkout H+1" if has_next_morning_exit else "Pending H+1")
            return {
                "status": "success",
                "detected_shift": detected_shift,
                "message": f"Sukses! Shift Malam (M) dideteksi. Jam Masuk: {masuk}, Jam Pulang: {plg_display}."
            }

    if not is_kedinasan and (not masuk or not pulang or 'TMTB' in ket.upper()):
        return {
            "status": "review_manual",
            "reason": "unresolved_gap",
            "detected_shift": detected_shift,
            "message": f"Review Manual: Masih ada jam kosong atau TMTB. Masuk: {masuk or 'Kosong'}, Pulang: {pulang or 'Kosong'}, Ket: {ket or '-'}"
        }
        
    return {
        "status": "success",
        "detected_shift": detected_shift,
        "message": f"Sukses! Shift dideteksi: {detected_shift}. Jam Masuk: {masuk}, Jam Pulang: {pulang}."
    }

@app.get("/api/auto_resolve_monthly")
async def auto_resolve_monthly(nip: str, month: str, skpd1: str = "4.02.01.01", skpd2: str = "4.02.01.01.0010"):
    import calendar
    auth_path = os.path.join(BASE_DIR, "auth.json")
    if not os.path.exists(auth_path):
        return {"status": "error", "message": "Sesi tidak ditemukan. Silakan login kembali."}
        
    try:
        b, t = month.split('-')
        month_int = int(b)
        year_int = int(t)
    except:
        return {"status": "error", "message": "Format bulan salah. Harus MM-YYYY."}
        
    num_days = calendar.monthrange(year_int, month_int)[1]
    
    sem = asyncio.Semaphore(5)
    
    async def resolve_day(day):
        async with sem:
            date_str = f"{day:02d}-{month_int:02d}-{year_int}"
            try:
                res = await auto_resolve_single(nip, date_str, skpd1, skpd2)
                return {
                    "day": day,
                    "status": res.get("status"),
                    "message": res.get("message"),
                    "detected_shift": res.get("detected_shift")
                }
            except Exception as e:
                return {
                    "day": day,
                    "status": "error",
                    "message": str(e),
                    "detected_shift": None
                }
                
    tasks = [resolve_day(day) for day in range(1, num_days + 1)]
    results = await asyncio.gather(*tasks)
    
    results.sort(key=lambda x: x["day"])
    return {"status": "success", "results": results}

@app.get("/api/get_individual_opd_status")
async def get_individual_opd_status(nip: str, month: str, skpd1: str = "4.02.01.01", skpd2: str = "4.02.01.01.0010"):
    auth_path = os.path.join(BASE_DIR, "auth.json")
    if not os.path.exists(auth_path):
        return {"status": "error", "message": "Sesi tidak ditemukan. Silakan login kembali."}
        
    try:
        b, t = month.split('-')
        month_int = int(b)
        year_int = int(t)
    except:
        return {"status": "error", "message": "Format bulan salah. Harus MM-YYYY."}
        
    bulan_indo = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
    nama_bulan = bulan_indo[month_int - 1]
    periode_indo = f"{nama_bulan} {year_int}"
    
    from batch_download_opd import download_opd
    session = requests.Session()
    with open(auth_path, 'r') as f:
        auth_data = json.load(f)
    cookies = {c['name']: c['value'] for c in auth_data.get('cookies', [])}
    for k, v in cookies.items():
        session.cookies.set(k, v)
        
    # Download OPD report individual in thread pool
    download_res = await asyncio.to_thread(download_opd, session, skpd1, skpd2, periode_indo, nip)
    if download_res != True:
        return {"status": "error", "message": f"Gagal mengunduh laporan dari SPOT. Detail: {download_res}"}
        
    # Parse the downloaded Individual OPD file
    safe_period = periode_indo.replace(' ', '_').replace('"', '').replace("'", "")
    filename = f"Laporan_OPD_{safe_period}_{nip}.xls"
    filepath = os.path.join(BASE_DIR, 'laporan opd', filename)
    
    if not os.path.exists(filepath):
        return {"status": "error", "message": f"File laporan {filename} tidak ditemukan setelah diunduh."}
        
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
            
        for row in soup.find_all('tr'):
            tds = row.find_all('td')
            if len(tds) < 13: continue
            txt = [td.get_text(strip=True) for td in tds]
            row_nip = txt[2].replace("'", "")
            if row_nip == nip:
                return {
                    "status": "success",
                    "nip": nip,
                    "nama": txt[1],
                    "ttwm": txt[6],
                    "ttwp": txt[12]
                }
        return {"status": "error", "message": f"Pegawai dengan NIP {nip} tidak ditemukan dalam file laporan."}
    except Exception as e:
        return {"status": "error", "message": f"Gagal membaca file laporan: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
