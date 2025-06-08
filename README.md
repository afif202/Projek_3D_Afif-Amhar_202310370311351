# Visualisasi Lemari 3D dengan Plotly dan Pyodide

Proyek ini mendemonstrasikan cara membuat, mentransformasi, dan memvisualisasikan model lemari 3D menggunakan Python dengan library `numpy` dan `plotly`. Model ini kemudian dirender secara interaktif di browser web menggunakan Pyodide, yang memungkinkan eksekusi kode Python langsung di front-end.

![Contoh Tampilan Lemari 3D](assets/tampilan-lemari.png)

## 📂 Struktur File

* `main.py`: Skrip utama Python yang mendefinisikan geometri lemari, merakit semua bagian, dan menghasilkan data plot dalam format JSON.
* `index.html`: Halaman web yang memuat Pyodide untuk menjalankan skrip `main.py` dan menggunakan Plotly.js untuk merender visualisasi 3D di browser.
* `README.md`: File ini, berisi penjelasan proyek.

---

## 🐍 Penjelasan Model (`main.py`)

Skrip `main.py` bertanggung jawab untuk membangun model lemari 3D secara matematis. Setiap bagian dari lemari dibuat sebagai objek mesh 3D yang terdiri dari **vertices** (titik-titik sudut) dan **faces** (permukaan yang menghubungkan titik-titik tersebut).

### Bagian-Bagian Utama Skrip

1. **Utilitas Transformasi (`apply_transform`)**
   Fungsi ini adalah inti dari manipulasi objek. Fungsi ini menerapkan transformasi geometri dasar (skala, rotasi pada sumbu X, Y, Z, dan translasi/pergeseran) pada sekumpulan titik. Urutan transformasi adalah:  **Skala → Rotasi → Translasi** .
2. **Bentuk Primitif (`create_...`)**
   Fungsi-fungsi ini berfungsi sebagai "pabrik" untuk membuat bentuk-bentuk dasar yang akan dirakit menjadi lemari:
   * `create_cube()`: Membuat balok. Digunakan untuk badan lemari dan rak.
   * `create_plane()`: Membuat bidang datar. Digunakan untuk pintu.
   * `create_cylinder()`: Membuat silinder. Digunakan untuk salah satu handle pintu.
   * `create_cuboid()`: Membuat balok dengan titik pusat di (0,0,0). Digunakan untuk handle pintu lainnya.
3. **Parameter Lemari**
   Bagian ini berisi variabel global yang mendefinisikan properti utama lemari:
   * `lebar`, `dalam`, `tinggi`: Dimensi keseluruhan badan lemari.
   * `tebal_rak`: Ketebalan papan rak di dalam lemari.
   * `door_gap`: Jarak kecil antar pintu.
   * `door_angle`: Sudut bukaan pintu kiri (dalam radian, `np.pi/3` setara dengan 60°).
4. **Perakitan Komponen**
   Di sini, setiap komponen lemari dibuat menggunakan bentuk primitif, kemudian diposisikan dan diorientasikan menggunakan `apply_transform`.
   * **Badan Lemari (`Body`)** : Sebuah balok besar yang menjadi kerangka utama.
   * **Pintu Kiri (`Pintu Kiri`)** : Sebuah bidang yang dirotasi sebesar `door_angle` pada engselnya.
   * **Pintu Kanan (`Pintu Kanan`)** : Sebuah bidang yang ditranslasikan ke posisi tertutup.
   * **Handle** :
   * Handle kiri berbentuk balok (`Cuboid`) yang posisinya dihitung relatif terhadap pintu kiri dan ikut terotasi bersama pintu.
   * Handle kanan berbentuk silinder (`Cylinder`) yang diposisikan di pintu kanan.
   * **Rak (`Rak1`, `Rak2`, dst.)** : Empat buah rak dibuat menggunakan perulangan (`for loop`), di mana setiap rak adalah balok yang diposisikan pada ketinggian (`zpos`) yang berbeda di dalam lemari.
5. **Visualisasi & Ekspor (`go.Figure` dan `get_plot_json`)**
   * Semua komponen yang telah dibuat (disebut `traces` di Plotly) dikumpulkan menjadi satu `Figure`.
   * Pengaturan `layout.scene` digunakan untuk mengatur tampilan visual seperti rasio aspek, posisi kamera, dan menyembunyikan sumbu koordinat agar terlihat lebih bersih.
   * Fungsi `get_plot_json()` mengonversi seluruh objek Figure Plotly menjadi string JSON. Ini adalah langkah kunci agar data visualisasi dapat "dikirim" dari lingkungan Python (Pyodide) ke JavaScript (Plotly.js).

---

## 🚀 Cara Menjalankan

Visualisasi ini berjalan sepenuhnya di browser dan memerlukan **server web lokal** untuk menyajikan file. Ini karena kebijakan keamanan browser (CORS) mencegah `index.html` memuat `main.py` jika dibuka langsung dari sistem file (`file://...`).

Cara termudah untuk melakukannya adalah dengan menggunakan ekstensi **Live Server** di editor kode  **Visual Studio Code** .

### Prasyarat

1. **Visual Studio Code** : Pastikan Anda telah menginstal [Visual Studio Code](https://code.visualstudio.com/).
2. **Ekstensi Live Server** : Instal ekstensi "Live Server" oleh Ritwick Dey dari marketplace VS Code.

* Buka VS Code.
* Buka tab **Extensions** (ikon kotak di sidebar kiri atau `Ctrl+Shift+X`).
* Cari `Live Server`.
* Klik **Install** pada ekstensi yang dibuat oleh  **Ritwick Dey** .

### Langkah-langkah Menjalankan:

1. **Buka Folder Proyek di VS Code**
   * Buka Visual Studio Code.
   * Pilih `File > Open Folder...` dan buka direktori tempat Anda menyimpan `index.html` dan `main.py`.
2. **Mulai Live Server**
   Ada dua cara mudah untuk memulai server:
   * **Opsi A (Klik Kanan):** Di panel Explorer VS Code, klik kanan pada file `index.html` dan pilih  **"Open with Live Server"** .
   * **Opsi B (Tombol Status Bar):** Klik tombol **"Go Live"** yang ada di pojok kanan bawah jendela VS Code.
3. **Lihat Hasilnya**
   * Live Server akan secara otomatis membuka tab baru di browser default Anda (misalnya ke alamat seperti `http://127.0.0.1:5500/index.html`).
   * Halaman akan menampilkan pesan "Memuat..." saat Pyodide dan library disiapkan. Harap tunggu sesaat.
   * Setelah selesai, model lemari 3D interaktif akan muncul di browser. Anda dapat mengklik dan menyeret untuk memutar visualisasi.

### Alur Kerja `index.html`:

Alur kerja di dalam browser tetap sama:

1. **Memuat Library** : Browser memuat `Pyodide` (mesin WebAssembly untuk Python) dan `Plotly.js` (untuk rendering).
2. **Inisialisasi Pyodide** : Fungsi `runPython` di dalam `index.html` memulai Pyodide dan menginstal dependensi (`numpy`, `plotly`) yang diperlukan.
3. **Fetch & Run** : Skrip mengambil konten `main.py` dari server lokal (Live Server), lalu menjalankannya di dalam lingkungan Pyodide.
4. **Ambil Data Plot** : Memanggil fungsi `get_plot_json()` dari `main.py` untuk mendapatkan data visualisasi dalam format JSON.
5. **Render** : Data JSON tersebut diberikan kepada `Plotly.newPlot()` untuk dirender sebagai grafik interaktif di dalam halaman web.

## ✒️ Pembuat

© 2025, **[Afif Amhar - 202310370311351]** ([@afif202](https://github.com/afif202)).
