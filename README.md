
# Sistem Absensi Berbasis Lokasi

Sistem absensi ini menggunakan **Flask** sebagai backend, dengan fitur login untuk admin dan pengguna, pencatatan absensi berbasis geolokasi, serta perhitungan jarak dari sekolah untuk validasi kehadiran. Terdapat juga fitur untuk mengelola siswa dan riwayat absensi oleh admin.

## Fitur Utama
- **Absensi Geolokasi**: Pengguna harus mencatatkan lokasinya saat melakukan absensi. Jika lokasi berada di luar radius 100 meter dari sekolah, absensi ditandai sebagai tidak valid.
- **Pengelolaan Siswa**: Admin dapat menambah, mengedit, dan menghapus data siswa melalui dashboard.
- **Dashboard**: Terdapat dashboard untuk siswa dan admin, dimana siswa bisa melihat riwayat absensi mereka, sementara admin dapat mengelola data siswa dan absensi.
- **Laporan Semester**: Admin dapat melihat rekap absensi per semester.

---

## Cara Penggunaan

### 1. Untuk Siswa

#### a. **Login**
- Kunjungi halaman `/login_user`.
- Masukkan **username** dan **password** Anda untuk login.
- Jika berhasil, Anda akan diarahkan ke halaman **Dashboard**.

#### b. **Melakukan Absensi**
- Setelah login, Anda akan melihat form absensi pada halaman dashboard.
- Masukkan **lokasi geografi** Anda (latitude dan longitude) yang dapat diambil dari GPS perangkat Anda.
- Klik **Submit** untuk mengirim absensi.
  - Jika lokasi Anda **dalam radius 100 meter** dari sekolah, absensi Anda akan ditandai sebagai:
    - `On Time` jika absensi dilakukan sebelum jam 07:10 pagi.
    - `Late` jika absensi dilakukan setelah jam 07:10 pagi.
  - Jika lokasi Anda **di luar 100 meter**, absensi akan ditandai `Invalid`. Setelah 3 kali percobaan tidak valid, Anda akan dianggap `Absent`.
- Anda juga dapat menambahkan **keterangan/remarks** jika diperlukan.

#### c. **Melihat Riwayat Absensi**
- Anda dapat melihat riwayat absensi Anda dengan mengunjungi halaman **History**.
- Di halaman tersebut, Anda bisa melihat status absensi dan detail lainnya dari absensi sebelumnya.
- Di dashboard, sistem akan menampilkan **5 catatan absensi terakhir** Anda.

#### d. **Mengubah Profil**
- Anda dapat memperbarui **username** dan **password** di halaman **Profile**.
- Setelah melakukan perubahan, klik **Submit** untuk menyimpan pembaruan.

---

### 2. Untuk Admin

#### a. **Login**
- Kunjungi halaman `/login_admin`.
- Masukkan **username** dan **password admin** Anda untuk login.
- Setelah login, Anda akan diarahkan ke **Admin Dashboard**.

#### b. **Melihat Absensi Harian**
- Di **Admin Dashboard**, Anda dapat melihat catatan absensi harian dari semua siswa.
- Anda dapat melakukan sorting dan filtering berdasarkan:
  - **Nama Siswa**
  - **Username**
  - **Kelas**
  - **Status Absensi**

#### c. **Mengelola Siswa**
- Akses halaman **Students** di panel admin.
- Di sini, Anda dapat **menambah**, **mengedit**, atau **menghapus** data siswa.
- Saat menambah siswa baru, Anda perlu mengisi informasi berikut:
  - **ID** (nomor identifikasi siswa)
  - **Nama Lengkap**
  - **Kelas**
  - **Username**
  - **Password** (akan dienkripsi secara otomatis)
- Anda juga dapat mengedit detail siswa yang sudah ada, termasuk mereset kata sandi mereka.

#### d. **Mengedit Catatan Absensi**
- Anda dapat mengedit catatan absensi siswa dengan mengklik tombol **edit** pada catatan absensi di dashboard admin.
- Anda bisa memperbarui status dan remarks absensi.

#### e. **Melihat Rekap Semester**
- Fitur **Semester Recap** memungkinkan Anda untuk melihat data absensi selama satu semester penuh.
- Anda bisa memilih **tahun** dan **semester** untuk memfilter catatan absensi dalam rentang waktu tertentu.

#### f. **Menghapus Siswa**
- Di halaman **Students**, Anda dapat menghapus siswa.
- Saat siswa dihapus, seluruh catatan absensi mereka juga akan dihapus dari sistem.



## Instalasi

Ikuti langkah-langkah di bawah ini untuk menginstal dan menjalankan aplikasi secara lokal.

1. Clone repository ini ke komputer Anda:
   ```bash
   git clone https://github.com/username/repository.git
   ```
2. Instal dependensi:
   ```bash
   pip install -r requirements.txt
   ```
3. Setup database dengan migrasi:
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```
4. Jalankan aplikasi:
   ```bash
   flask run
   ```

---

## Kontribusi

Anda dipersilakan untuk memberikan kontribusi pada proyek ini. Silakan fork repository ini, lakukan perubahan, dan kirimkan pull request.

---

## Lisensi

Proyek ini dilisensikan di bawah [MIT License](LICENSE).

```

### Penjelasan Tambahan:
- **Tampilan**: Anda bisa mengganti URL gambar dengan tangkapan layar nyata dari aplikasi Anda yang di-hosting secara online.
- **Link GitHub dan License**: Pastikan untuk mengganti link yang relevan dengan URL repositori Anda di GitHub.

Dengan struktur dan panduan di atas, README Anda akan lebih menarik dan mudah dipahami oleh pengguna.
