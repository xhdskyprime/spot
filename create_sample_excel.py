import pandas as pd
import os

def create_template():
    # Mencontohkan template minimalis (Jam Masuk, Keluar, Tanggal Bebas diurus otomatis oleh script)
    data = {
        'NIP': ['199901062025041001', ''],
        'Nama': ['MUHAMAD LUTFI, S.Kom', 'LUTFIATUL HASANAH'],
        'Tanggal': ['10/02/2026', '11/02/2026']
    }
    
    df = pd.DataFrame(data)
    df.to_excel('d:/SPOT/data_pegawai.xlsx', index=False)
    print("Berhasil membuat template SUPER SIMPEL (data_pegawai.xlsx)")
    print("Kolom wajib hanya: Nama/NIP dan Tanggal!")

if __name__ == '__main__':
    create_template()

