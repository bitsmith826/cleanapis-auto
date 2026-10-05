CleanAPIs Auto
==============

Otomasi pembuatan akun CleanAPIs + API Key + pendaftaran ke 9Router, pakai
Camoufox (browser anti-detect berbasis Firefox).

Install
-------

1. Salin folder ini ke komputer Windows.
2. Buka `.env`, sesuaikan kalau perlu (lihat bagian "Konfigurasi").
   Default-nya `http://localhost:20128` (ganti di `.env` kalau pakai host lain).
3. Buka `empas.txt`, isi daftar akun. Format satu per baris:

   ```
   email|password
   ```

   Contoh:

   ```
   contoh1@gmail.com|sandi123
   contoh2@gmail.com|sandi456
   ```

   Baris diawali `#` tidak diproses (dianggap catatan).

   Format `empas.txt` sama persis dengan Atria Auto, jadi file `empas.txt`
   lama bisa langsung disalin ke sini.

4. Klik dua kali `run.bat`. Selesai.

`run.bat` akan otomatis:
- cek Python; kalau tidak ada -> kasih tahu link downloadnya
- install library (`camoufox`, `playwright`) -- sekali saja
- download browser Camoufox -- sekali saja
- menjalankan otomasi untuk tiap akun di `empas.txt`

Browser berjalan di latar belakang secara default (`HEADLESS=true` di `.env`).
Kalau ingin melihatnya bekerja, ubah jadi `HEADLESS=false`.

Pilih mode
----------

Saat jalan, akan muncul pertanyaan:

```
PILIH MODE
------------------------------------------------------------
 1. Buat API Key saja
    Login CleanAPIs -> buat key -> simpan ke result.txt

 2. Full - sampai terdaftar di 9Router
    Login CleanAPIs -> buat key -> simpan -> daftar ke 9Router

 3. Input keys.txt ke 9Router saja
    Untuk yang sudah punya API key, tinggal daftar ke 9Router
------------------------------------------------------------
Pilih (1/2/3) [default 2]:
```

- **Ketik 1** -> buat akun CleanAPIs + API key, simpan ke `result.txt`.
  Tidak menyentuh 9Router.
- **Ketik 2** (atau Enter) -> lanjut daftarkan key ke 9Router sampai
  tersimpan & lolos Check. Kalau key ditolak (*Invalid API key*), otomatis
  dibuatkan key baru, maksimal 3 kali per akun.
  Kalau nama koneksi sudah ada, koneksi lama **dihapus** dulu lalu
  diganti dengan key baru (anti duplikat).
- **Ketik 3** -> **untuk yang sudah punya API key.** Tidak perlu `empas.txt`
  dan tidak perlu buka CleanAPIs. Cukup buat file `keys.txt`:

  ```
  nama|apikey
  ```

  Contoh:

  ```
  budi@gmail.com|cc_QpXf2m...48 char
  sari@gmail.com|cc_zZ9aBc...48 char
  ```

  `nama` = email, dipakai sebagai nama API Key di 9Router. Setiap nama
  dicek dulu: kalau sudah ada di provider CleanAPIs -> **dilewati**,
  kalau belum -> didaftarkan (Check -> Save).

  File `keys.txt` **hanya dibutuhkan kalau pilih mode 3**. Kalau belum ada
  saat dipilih, script akan kasih tahu cara buatnya.

Hasil
-----

Tersimpan di **`result.txt`**, format:
```
email|password|apikey
```

Ditulis langsung setiap kali satu API key berhasil dibuat -- jika skrip
dihentikan di tengah jalan, akun yang sudah selesai tetap tersimpan.

Resume otomatis
---------------

Saat dijalankan lagi, akun yang emailnya sudah ada di `result.txt`
**akan dilewati**. Jadi cukup klik `run.bat` lagi untuk melanjutkan sisanya.

Yang dilakukan per akun
-----------------------

**Mode 1 (Buat API Key saja):**

1. Buka `https://cleanapis.com/?ref=CC9ELETL` -> klik **Get Started**
2. Menu *Create your account* -> klik **Sign up With Google**
3. Isi email -> **Next**
4. Isi password -> **Next**
5. Layar *Login ke cleanapis.com* -> klik **Lanjutkan**
   (Hanya untuk akun baru. Kalau akun Google sudah pernah daftar
   CleanAPIs sebelumnya, layar ini di-skip langsung ke Dashboard.)
6. Dashboard -> **API Keys** (menu kiri) -> **Create API Key**
7. Isi *Key Name* dengan email -> **Create Key** -> ambil key `cc_...`
8. Simpan ke `result.txt`

**Mode 2 (Full):** semua di atas, lalu:

9. Buka 9Router -> login -> halaman **Providers**
10. Cek provider **CleanAPIs**:
    - **Belum ada** -> klik **Add OpenAI Compatible**
      -> isi Name `CleanAPIs`, Prefix `cleanapis`,
      Base URL `https://cleanapis.com/v1` -> **Create**
      (Dilakukan **SEKALI saja** untuk seluruh batch, bukan per akun.)
    - **Sudah ada** -> langsung klik **CleanAPIs**
11. Klik **Add API Key** -> isi Name (email) + API Key -> **Check** -> **Save**
12. **Default Model** selalu diisi `default` (field wajib di 9Router).

**Mode 3 (Input keys.txt ke 9Router saja):** tidak buka CleanAPIs, langsung:

1. Buka 9Router -> login -> halaman *Providers*
2. Pastikan provider CleanAPIs ada (buat sekali kalau belum, lihat langkah 10)
3. Cek nama: kalau sudah ada -> **dilewati**, kalau belum -> daftarkan
4. Isi Name + API Key -> **Check** -> **Save**
5. Ulangi untuk setiap baris di `keys.txt`

File penting
------------

| File | Kegunaan |
|---|---|
| `run.bat` | **klik dua kali untuk mulai** |
| `.env` | **konfigurasi** -- URL, password, headless, dll |
| `empas.txt` | daftar akun (mode 1 & 2) |
| `keys.txt` | daftar API key (mode 3, opsional) |
| `result.txt` | hasil (email\|password\|apikey) |
| `main.py`, `cleanapis.py`, `router9.py`, `tampilan.py` | kode program |
| `requirements.txt` | daftar library Python |

Konfigurasi (file `.env`)
-------------------------

Semua pengaturan ada di satu file `.env`. Isi sekali, tidak perlu buka kode.

```
ROUTER_URL=http://localhost:20128            # URL 9Router
ROUTER_PASSWORD=ganti-dengan-password-anda  # password login 9Router
HEADLESS=true                                 # true = tersembunyi, false = tampil
MAX_COBA_KEY=3                                # ulang buat key kalau ditolak
JEDA_ANTAR_AKUN=5                             # jeda detik antar akun
```

> Salin `.env.example` menjadi `.env` lalu isi `ROUTER_PASSWORD` kamu.
> Jangan commit file `.env` yang berisi password asli.

Kalau file `.env` tidak ada atau isinya kosong, semua kembali ke nilai
default di atas. Lihat `.env.example` sebagai contoh.

Troubleshooting
---------------

- **"Gagal download Python/Camoufox"** -> cek koneksi internet, jalankan lagi.
- **Google meminta verifikasi (captcha / 2FA)** -> akun itu gagal dan
  dilewati, lanjut akun berikutnya. Bisa diulang lagi nanti.
- **Login 9Router gagal** -> cek `ROUTER_URL` dan `ROUTER_PASSWORD` di file
  `.env`, dan pastikan 9Router bisa dibuka.
- **Browser tidak muncul** -> set `HEADLESS=false` di `.env`.
- **Provider CleanAPIs tidak ketemu di 9Router** -> script akan buat otomatis
  sekali. Kalau gagal, coba tambah manual: Add OpenAI Compatible
  -> Name `CleanAPIs`, Prefix `cleanapis`, Base URL `https://cleanapis.com/v1`.
- **Akun gagal di tengah batch** -> akun yang sudah selesai tetap tersimpan
  di `result.txt`. Jalankan lagi untuk melanjutkan sisanya; yang sudah ada
  akan otomatis dilewati. Untuk mengulang akun yang gagal, hapus barisnya
  dari `result.txt` (kalau ada) lalu jalankan lagi.

Catatan
-------

- Hanya untuk komputer Windows.
- Butuh koneksi internet (download Python, library, browser Camoufox; saat
  berjalan).
- Tombol "lanjut" di layar Google dideteksi **otomatis** (warna tombol, bukan
  teks), jadi cocok untuk akun Google dengan bahasa apa pun.

Edukasi
-------

Project ini dibuat untuk **tujuan edukasi** — memahami otomasi browser
dan integrasi API:

- **Otomasi browser dengan Camoufox** — login OAuth Google, navigasi
  multi-step (reff -> Get Started -> Sign up with Google -> consent ->
  Dashboard -> API Keys), deteksi tombol by warna (bukan teks) agar
  tahan perubahan bahasa, dan fresh browser per akun (tanpa carry-over
  session).
- **Manajemen kredensial yang aman** — semua secret di `.env` (di-ignore
  git), template di `.env.example`, hasil di `result.txt` (di-ignore
  git). Jangan pernah commit `.env` / `empas.txt` / `result.txt` yang
  berisi data asli.
- **Resume & idempotency** — tiap akun simpan langsung ke `result.txt`
  + fsync; run lagi otomatis skip yang sudah ada. Tidak ada duplikasi.
- **Integrasi OpenAI-compatible provider** — membuat provider sekali,
  lalu Add API Key + Check + Save dengan Default Model `default`.
- **Auto-create file** — kalau `empas.txt` / `keys.txt` belum ada, script
  buat template otomatis + buka editor (zero-config untuk clone baru).

Gunakan dengan bijak dan patuhi ToS layanan terkait.
