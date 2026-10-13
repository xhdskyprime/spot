import os
import glob
import pandas as pd

def search_schedule():
    files = ['data_jadwal.xlsx', 'hasil_jadwal.xlsx', 'Jadwal IPSRS APRI.. 2026 .xlsx']
    for fn in files:
        if os.path.exists(fn):
            try:
                df = pd.read_excel(fn)
                # Find if any column contains "lutfi" or NIP
                print(f"=== {fn} ===")
                matching_rows = []
                for idx, row in df.iterrows():
                    row_str = " ".join([str(val) for val in row.values])
                    if "lutfi" in row_str.lower() or "199901062025041001" in row_str:
                        matching_rows.append(row)
                if matching_rows:
                    m_df = pd.DataFrame(matching_rows)
                    print(m_df.to_string())
                else:
                    print("No match")
            except Exception as e:
                print(f"Error reading {fn}: {e}")

search_schedule()
