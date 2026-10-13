import pandas as pd

def create_template_jadwal():
    # Membuat daftar kolom dari 1 sampai 31 untuk tanggal
    columns = ['NIP', 'Nama', 'Bulan_Tahun'] + [str(i) for i in range(1, 32)]
    
    # Contoh data 1 pegawai
    data = [{
        'NIP': '197104042025211025',
        'Nama': 'MARJUKI SASTRA WIJAYA',
        'Bulan_Tahun': '03-2026', # Format MM-YYYY
        '1': 'P', '2': 'S', '3': 'M', '4': 'L', '5': 'P',
        '6': 'S', '7': 'M', '8': 'L', '9': 'P', '10': 'L'
        # Tanggal lainnya dikosongkan (Nan) sebagai contoh
    }]
    
    df = pd.DataFrame(data, columns=columns)
    df.to_excel('d:/SPOT/data_jadwal.xlsx', index=False)
    
    print("==================================================")
    print("✅ Berhasil membuat template Jadwal: data_jadwal.xlsx")
    print("==================================================")
    print("CARA MENGISI EXCEL:")
    print("1. 'Bulan_Tahun' diisi format MM-YYYY (contoh: 03-2026 untuk Maret 2026)")
    print("2. Kolom '1' sampai '31' menunjukkan tanggal pada bulan tersebut.")
    print("3. Isi tiap tanggal dengan salah satu kode berikut:")
    print("   P = Pagi")
    print("   S = Siang")
    print("   M = Malam")
    print("   L = Libur / Lepas")
    print("==================================================")

if __name__ == '__main__':
    create_template_jadwal()
