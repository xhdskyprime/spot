const xlsx = require('xlsx');

function createTemplate() {
    const data = [
        {
            'NIP': '199901062025041001',
            'Nama': 'MUHAMAD LUTFI, S.Kom',
            'Tanggal_Finger': '10/02/2026',
            'Jam_Masuk': '2026-02-10 07:50:48',
            'Jam_Keluar': '2026-02-10 16:06:11',
            'Tanggal_Bebas': '10/02/2026',
            'Keterangan': 'Bebas piket'
        },
        {
            'NIP': '199908182025042002',
            'Nama': 'LUTFIATUL HASANAH, A.Md.',
            'Tanggal_Finger': '11/02/2026',
            'Jam_Masuk': '2026-02-11 07:50:01',
            'Jam_Keluar': '2026-02-11 16:01:23',
            'Tanggal_Bebas': '11/02/2026',
            'Keterangan': 'Bebas piket'
        }
    ];

    const workbook = xlsx.utils.book_new();
    const worksheet = xlsx.utils.json_to_sheet(data);

    // Auto-size columns slightly
    worksheet['!cols'] = [
        { wch: 20 }, // NIP
        { wch: 30 }, // Nama
        { wch: 15 }, // Tanggal_Finger
        { wch: 20 }, // Jam_Masuk
        { wch: 20 }, // Jam_Keluar
        { wch: 15 }, // Tanggal_Bebas
        { wch: 20 }  // Keterangan
    ];

    xlsx.utils.book_append_sheet(workbook, worksheet, 'DataPegawai');
    xlsx.writeFile(workbook, 'd:/SPOT/data_pegawai.xlsx');
    console.log("✅ Berhasil membuat template: d:/SPOT/data_pegawai.xlsx");
}

createTemplate();
