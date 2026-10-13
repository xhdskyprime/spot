import os
from bs4 import BeautifulSoup

base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
folder = os.path.join(base_dir, 'laporan bulanan')
print(f"Base dir: {base_dir}")
print(f"Folder: {folder}")
print(f"Exists: {os.path.exists(folder)}")
if os.path.exists(folder):
    files = os.listdir(folder)
    print("Files in folder:")
    for f in files:
        if '200201142025042002' in f:
            print(f" - Found file: {f}")
            filepath = os.path.join(folder, f)
            with open(filepath, 'r', encoding='utf-8') as file_obj:
                soup = BeautifulSoup(file_obj, 'html.parser')
            rows = soup.find_all('tr')
            print(f"Total rows in parsed file: {len(rows)}")
            for r in rows:
                tds = r.find_all('td')
                txt = [td.get_text(strip=True) for td in tds]
                if len(txt) >= 8 and txt[0].isdigit():
                    print(f"Day {txt[0]:2} | In: {txt[2]:<8} | Out: {txt[4]:<8} | Late: {txt[5]:<5} | Early: {txt[6]:<5} | Desc: {txt[7] if len(txt)>7 else ''}")
