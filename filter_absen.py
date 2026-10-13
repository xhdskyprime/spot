import pdfplumber
import pandas as pd
import sys
import os
import glob
import re
import argparse

MONTH_MAP = {
    "Januari": "01", "Februari": "02", "Maret": "03", "April": "04",
    "Mei": "05", "Juni": "06", "Juli": "07", "Agustus": "08",
    "September": "09", "Oktober": "10", "November": "11", "Desember": "12"
}

def parse_indonesian_date(date_str):
    # Example: "Jumat, 20 Maret 2026" or "20 Maret 2026"
    try:
        # Remove day name and comma
        clean_date = re.sub(r'^[a-zA-Z]+,\s*', '', date_str).strip()
        parts = clean_date.split()
        if len(parts) >= 3:
            day = parts[0].zfill(2)
            month_name = parts[1]
            month = MONTH_MAP.get(month_name, "00")
            year = parts[2]
            return f"{day}/{month}/{year}"
    except:
        pass
    return date_str

def filter_attendance_pdf(pdf_path, mode="tm"):
    rows_data = [] # List of dicts for Excel
    name = "Unknown"
    nip = "Unknown"
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Extract Name and NIP from first page text
            text = pdf.pages[0].extract_text()
            for line in text.split('\n'):
                if "Nama" in line and ":" in line:
                    name = line.split(":", 1)[1].strip()
                if ("IP" in line or "NIP" in line) and ":" in line:
                    nip = line.split(":", 1)[1].strip()
            
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        if len(row) < 13:
                            continue
                            
                        # Skip header rows
                        if row[0] == "NO" or "TANGGAL" in str(row[1]):
                            continue
                            
                        # Normalize checkmarks
                        found_v_at = [i for i, cell in enumerate(row) if str(cell).strip().upper() == 'V']
                        
                        is_tm = bool(5 in found_v_at) # Index 5 is column 6 (TM)
                        is_psw = bool(6 in found_v_at) # Index 6 is column 7 (PSW)
                        is_bp = bool(12 in found_v_at) # Index 12 is column 13 (BP)
                        
                        tanggal_raw = str(row[1]).strip()
                        if not tanggal_raw or tanggal_raw == "":
                            continue
                        
                        # Selection logic
                        condition = False
                        if mode == "tm":
                            condition = is_tm and not is_bp
                        elif mode == "psw":
                            condition = is_psw and not is_bp
                        elif mode == "both":
                            condition = (is_tm or is_psw) and not is_bp
                        
                        if condition:
                            tanggal_fmt = parse_indonesian_date(tanggal_raw)
                            rows_data.append({
                                "NIP": nip,
                                "Nama": name,
                                "Tanggal": tanggal_fmt,
                                "Status": f"{'TM ' if is_tm else ''}{'PSW' if is_psw else ''}".strip()
                            })
                            
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        
    return rows_data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Filter SPOT PDF Attendance")
    parser.add_argument("--path", default="laporan bulanan/*.pdf", help="Path to PDF files (glob)")
    parser.add_argument("--mode", default="tm", choices=["tm", "psw", "both"], help="Filter mode: tm, psw, or both")
    
    args = parser.parse_args()
    
    search_path = args.path
    files = glob.glob(search_path)
    if not files:
        if os.path.isfile(search_path):
            files = [search_path]
        else:
            print(f"No PDF files found matching: {search_path}")
            sys.exit(1)
            
    final_data = []
    
    print(f"Mode Filter: {args.mode.upper()}")
    print(f"Processing {len(files)} files...")
    for pdf_file in files:
        data = filter_attendance_pdf(pdf_file, mode=args.mode)
        final_data.extend(data)
            
    if final_data:
        df = pd.DataFrame(final_data)
        output_file = "hasil_filter.xlsx"
        df.to_excel(output_file, index=False)
        print(f"\nBerhasil menyaring {len(final_data)} data.")
        print(f"Hasil disimpan di: {output_file}")
    else:
        print("\nTidak ada data yang sesuai kriteria.")

