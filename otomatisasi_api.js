const fs = require('fs');
const path = require('path');
const xlsx = require('xlsx');

const HAR_FILE = path.join(__dirname, 'spot.tangerangkab.go.id.har');
const EXCEL_FILE = path.join(__dirname, 'data_pegawai.xlsx');
const API_URL = 'https://spot.tangerangkab.go.id/kedinasan/piket/simpan';

async function main() {
    console.log("=== OTOMATISASI API INPUT BEBAS PIKET (CEPAT & BACKGROUND) ===");

    // 1. Cek file HAR
    if (!fs.existsSync(HAR_FILE)) {
        console.error(`❌ File HAR tidak ditemukan: spot.tangerangkab.go.id.har`);
        console.log("Pastikan Anda sudah menaruh file 'spot.tangerangkab.go.id.har' di folder d:/SPOT");
        return;
    }

    if (!fs.existsSync(EXCEL_FILE)) {
        console.error(`❌ File EXCEL tidak ditemukan: data_pegawai.xlsx`);
        return;
    }

    // 2. Baca file HAR untuk mencari Cookies dan Headers
    console.log("-> Mengambil sesi (Cookies) dari file HAR...");
    const harRaw = fs.readFileSync(HAR_FILE, 'utf8');
    const harData = JSON.parse(harRaw);

    // Cari Request POST ke endpoint simpan
    let targetHeaders = {};
    let harPiketRequest = null;

    // Safety check jika json besar
    if (harData.log && harData.log.entries) {
        harPiketRequest = harData.log.entries.find(e =>
            e.request.url.includes('/kedinasan/piket/simpan') &&
            e.request.method === 'POST'
        );
    }

    if (!harPiketRequest) {
        console.error("❌ Tidak menemukan request 'simpan' (POST) di file HAR Anda.");
        console.log("Pastikan sebelum melakukan 'Save as HAR', Anda sudah berhasil mengklik 'Simpan' dan mengisi 1 data bebas piket dengan benar di website!");
        return;
    }

    // Mengambil Headers penting dari HAR
    harPiketRequest.request.headers.forEach(h => {
        const name = h.name.toLowerCase();
        // Buang Content-Type karena saat mengirim `FormData` baru kita akan let the browser/node set boundary sendiri.
        // Buang Origin & Referer jika perlu tapi aman untuk keep Cookie, User-Agent, X-Requested-With
        if (!name.startsWith(':') && name !== 'content-length' && name !== 'content-type' && name !== 'host') {
            targetHeaders[h.name] = h.value;
        }
    });

    console.log("✅ Sesi otentikasi (Cookies) berhasil diekstrak dari HAR.");

    // 3. Baca Data Excel
    console.log("-> Membaca Data dari Excel...");
    const workbook = xlsx.readFile(EXCEL_FILE);
    const sheetName = workbook.SheetNames[0];
    const sheet = workbook.Sheets[sheetName];
    // Pastikan data punya Header
    const records = xlsx.utils.sheet_to_json(sheet);
    console.log(`✅ Ditemukan ${records.length} baris data untuk diinput.\n`);

    // 4. Proses Input Satu per Satu via API
    let successCount = 0;
    let errorCount = 0;

    for (let i = 0; i < records.length; i++) {
        const row = records[i];

        // Memastikan isi dari baris, dari excel, menyesuaikan structure payload HTTP
        const nipStr = row['NIP'] ? String(row['NIP']).trim() : '';
        const namaStr = row['Nama'] ? String(row['Nama']).trim() : '';
        const comboNama = `${nipStr} - ${namaStr}`;
        const tglFinger = row['Tanggal_Finger'] || '';
        const jamMasuk = row['Jam_Masuk'] || '';
        const jamKeluar = row['Jam_Keluar'] || '';
        const tglBebas = row['Tanggal_Bebas'] || tglFinger;
        const ket = row['Keterangan'] || '';

        console.log(`[Baris ${i + 1}/${records.length}] Memproses: ${comboNama}`);

        // Persiapkan parameter POST layaknya multipart Form-Data native
        const form = new FormData();
        form.append('nama', comboNama);
        form.append('nip', nipStr);
        form.append('id', '');
        form.append('tanggal_bp', String(tglBebas));
        form.append('masuk', String(jamMasuk));
        form.append('telat', '0:00:00');
        form.append('keluar', String(jamKeluar));
        form.append('cepat', '0:00:00');
        form.append('tanggal', String(tglFinger));
        form.append('keterangan', String(ket));

        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: targetHeaders,  // fetch native akan otomatis merge header Content-Type + boundary
                body: form
            });

            // Seringkali API e-kinerja mengembalikan text/html bahkan saat sukses / berhasil
            const responseText = await response.text();

            if (response.ok) {
                console.log(`  -> ✅ [Berhasil] Data tersimpan di server!`);
                successCount++;
            } else {
                console.log(`  -> ❌ [Gagal] Server merespon Http Code: ${response.status}`);
                errorCount++;
            }

        } catch (error) {
            console.error(`  -> ❌ [Error] Kesalahan Jaringan Server: ${error.message}`);
            errorCount++;
        }

        // Delay 1 detik untuk menghindari overload / block dari Server Pemerintah
        if (i < records.length - 1) {
            await new Promise(resolve => setTimeout(resolve, 1000));
        }
    }

    console.log(`\n=== PROSES PENGERJAAN SELESAI ===`);
    console.log(`Total  : ${records.length} Baris`);
    console.log(`Sukses : ${successCount} Baris`);
    console.log(`Gagal  : ${errorCount} Baris`);
}

main().catch(console.error);
