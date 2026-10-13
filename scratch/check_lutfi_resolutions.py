import os
import pandas as pd

def check_files():
    files = ['hasil_api_pegawai.xlsx', 'hasil_filter_absen_harian.xlsx', 'filter harian masalah.xlsx']
    for fn in files:
        if os.path.exists(fn):
            print(f"=== {fn} ===")
            try:
                df = pd.read_excel(fn)
                print("Columns:", df.columns.tolist())
                # filter by Lutfi
                # Columns might be 'NIP', 'Nama Pegawai', 'Tanggal', etc.
                lutfi_rows = []
                for idx, row in df.iterrows():
                    row_str = " ".join([str(val) for val in row.values])
                    if "lutfi" in row_str.lower() or "199901062025041001" in row_str:
                        lutfi_rows.append(row)
                if lutfi_rows:
                    print(pd.DataFrame(lutfi_rows).to_string())
                else:
                    print("No lutfi row")
            except Exception as e:
                print("Error:", e)

check_files()
