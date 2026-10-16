# Panel Sesi Claude Code di herdr

Satu popup di [herdr](https://herdr.dev) yang berisi **semua sesi Claude Code yang pernah ada** — yang
sedang terbuka maupun yang sudah ditutup. Dari panel ini sebuah sesi bisa **dibuka lagi** (dilanjutkan
dengan konteks lengkap) atau **ditutup** untuk membebaskan RAM, tanpa perlu mengingat ID sesi atau
mencari pane-nya satu per satu.

```
╭─ Sesi Claude Code  8 sesi · 3 terbuka ─────────────────────────────────────────────────╮
│ / untuk cari                                                                           │
│                                                                                        │
│ ◐ kerja    16 Oct 10:44  Keyboard extender tidak bisa mengetik              David      │
│ ○ tutup    16 Oct 08:04  Menghubungkan Claude ke GitHub                     David      │
│ ◆ tunggu   16 Oct 08:04  Modul spedo tester PR12-4DN                        David      │
│▶◆ tunggu   16 Oct 08:04  Riset brake bansai                                 David      │
│ ○ tutup    14 Oct 10:52  Menghubungkan Claude ke GitHub                     David      │
│ ○ tutup    13 Oct 10:50  Herdr install script                               David      │
│────────────────────────────────────────────────────────────────────────────────────────│
│ 7930ceb4-5dd4-4b37-a0c9-fff5dedadd7b  C:\Users\David · 4 prompt · pane w1:p5           │
│ terakhir: langsung commit and push ke master                                           │
│                                                                                        │
│ ↑↓ pilih · Enter buka · x tutup · o hanya terbuka · r muat ulang · / cari · q keluar   │
╰────────────────────────────────────────────────────────────────────────────────────────╯
```

## ⌨️ Cara membuka panel (tombol keyboard)

Di jendela **herdr**:

| Langkah | Tekan | Keterangan |
|---|---|---|
| 1 | <kbd>Ctrl</kbd> + <kbd>B</kbd> | tekan bersamaan, lalu **lepas kedua tombol** (ini *prefix* herdr) |
| 2 | <kbd>Alt</kbd> + <kbd>C</kbd> | tekan bersamaan → panel **Sesi Claude Code** muncul sebagai popup |

Ditulis singkat: **`Ctrl+B` lalu `Alt+C`** (C = **C**laude). Jangan menahan <kbd>Ctrl</kbd>+<kbd>B</kbd>
sambil menekan <kbd>Alt</kbd>+<kbd>C</kbd> — lepas dulu, baru tekan yang kedua.

Tombol di dalam panel:

| Tekan | Fungsi |
|---|---|
| <kbd>↑</kbd> / <kbd>↓</kbd> (atau <kbd>k</kbd> / <kbd>j</kbd>) | pindah pilihan |
| <kbd>PgUp</kbd> / <kbd>PgDn</kbd>, <kbd>Home</kbd> / <kbd>End</kbd> | lompat 10 baris / ke awal / ke akhir |
| <kbd>Enter</kbd> | **buka** sesi: lanjutkan di tab baru, atau langsung pindah ke pane-nya kalau sudah terbuka |
| <kbd>X</kbd> atau <kbd>Del</kbd> | **tutup** sesi (kirim `/exit`, lalu pane-nya ditutup) |
| <kbd>/</kbd> lalu ketik | cari berdasarkan judul, folder, atau ID; <kbd>Enter</kbd> selesai, <kbd>Esc</kbd> hapus pencarian |
| <kbd>O</kbd> | tampilkan hanya sesi yang sedang terbuka (tekan lagi untuk semua) |
| <kbd>R</kbd> | muat ulang daftar dan status |
| <kbd>Q</kbd> atau <kbd>Esc</kbd> | tutup popup |

## Daftar isi
1. [Hasil uji](#hasil-uji)
2. [Kenapa perlu panel ini](#kenapa-perlu-panel-ini)
3. [Cara kerja](#cara-kerja)
4. [Instalasi](#instalasi)
5. [Memakai panel](#memakai-panel)
6. [Apa yang terjadi saat membuka & menutup](#apa-yang-terjadi-saat-membuka--menutup)
7. [Tanpa panel: perintah manual](#tanpa-panel-perintah-manual)
8. [Kustomisasi](#kustomisasi)
9. [Masalah yang mungkin terjadi & solusinya](#masalah-yang-mungkin-terjadi--solusinya)
10. [Lampiran: update herdr di Windows](#lampiran-update-herdr-di-windows)
11. [Struktur repo](#struktur-repo)

## Hasil uji

Diuji pada laptop Windows 10 22H2 (i3-7020U, RAM 8 GB, HDD), 16 Oktober 2026, dengan:

| Komponen | Versi |
|---|---|
| herdr | 0.9.5 (client & server), integrasi Claude v11 |
| Claude Code | 2.1.301 |
| Python | 3.14.5 (hanya pustaka bawaan, tanpa `pip install`) |
| Terminal | Windows Terminal, tema Dracula |

| Yang diuji | Hasil |
|---|---|
| Membaca semua transcript (8 sesi, ±23 MB) | ✅ 0,24 dtk |
| Mendeteksi sesi yang terbuka + statusnya (kerja / tunggu / siap) | ✅ cocok dengan `herdr agent list` |
| Membuka panel dengan `Ctrl+B` lalu `Alt+C` | ✅ dicoba langsung |
| **Menutup** sesi dari panel (<kbd>X</kbd>) | ✅ dicoba langsung, pane ikut tertutup |
| **Membuka lagi** sesi yang sudah ditutup (<kbd>Enter</kbd>) | ✅ dicoba langsung, percakapan lanjut dengan konteks lengkap |

> Belum diuji khusus: jalur konfirmasi saat menutup sesi yang **sedang bekerja** (◐) dan sesi di pane
> yang sedang dipakai, serta sesi yang folder kerjanya sudah dihapus.

## Kenapa perlu panel ini

Setiap sesi Claude Code yang terbuka adalah satu proses `claude.exe` yang memakan **±200–300 MB RAM**,
ditambah satu shell PowerShell di pane-nya (±70 MB). herdr memulihkan pane lama saat dibuka kembali
(`resume_agents_on_restore = true`), jadi tanpa disadari bisa ada 3–4 sesi lama yang tetap hidup.
Di laptop RAM 8 GB, menutup dua sesi lama saja membebaskan ±500 MB.

Menutup sesi **tidak menghapus apa pun**: seluruh percakapan tersimpan di
`%USERPROFILE%\.claude\projects\<folder>\<id-sesi>.jsonl` dan bisa dilanjutkan kapan saja. Masalahnya,
untuk membuka lagi biasanya perlu mengingat ID sesi atau memilih dari `claude --resume` di folder yang
benar. Panel ini menggabungkan semuanya di satu tempat.

## Cara kerja

```
 %USERPROFILE%\.claude\projects\*\*.jsonl          herdr agent list (JSON)
   ├─ ai-title / agent-name  → judul                 └─ agent_session.value = ID sesi
   ├─ cwd                    → folder kerja              pane_id, tab_id, agent_status
   ├─ last-prompt            → prompt terakhir                    │
   └─ jumlah prompt user                                          │
                │                                                 │
                └────────────►  claude-sesi.py  ◄─────────────────┘
                                (popup herdr, Ctrl+B Alt+C)
                                     │
             Enter (tertutup) ──► herdr tab create --cwd <folder>  →  claude --resume <id>
             Enter (terbuka)  ──► herdr tab focus + herdr agent focus <pane>
             X                ──► herdr agent prompt <pane> "/exit"  →  herdr pane close <pane>
```

**Sumber data:**

1. **Transcript Claude Code** — setiap sesi adalah satu file JSON Lines. Panel membaca baris-baris kecil
   berisi metadata dan melewati baris besar (`api-request*`) agar tetap cepat di HDD:

   | Tipe baris | Dipakai untuk |
   |---|---|
   | `agent-name` | judul yang Anda beri sendiri (prioritas pertama) |
   | `ai-title` | judul otomatis buatan Claude (prioritas kedua) |
   | prompt `user` pertama | judul cadangan bila belum ada judul |
   | `last-prompt` | baris "terakhir:" di bagian detail |
   | `cwd` (baris pertama yang memilikinya) | folder kerja sesi — dipakai saat membuka lagi |
   | jumlah pesan `user` yang bukan meta | kolom "N prompt"; sesi dengan 0 prompt disembunyikan |

2. **herdr** — dengan integrasi Claude terpasang, herdr mencatat ID sesi Claude di setiap pane.
   `herdr agent list` mengembalikan JSON seperti ini (dipotong):

   ```json
   {"agent":"claude","agent_session":{"kind":"id","value":"7930ceb4-5dd4-..."},
    "agent_status":"blocked","pane_id":"w1:p5","tab_id":"w1:t5","cwd":"C:\\Users\\David"}
   ```

   Sesi yang ID-nya ada di daftar ini ditandai **terbuka**; sisanya **tutup**.

**Arti ikon status:**

| Ikon | Status herdr | Artinya |
|---|---|---|
| ◐ kerja | `working` | Claude sedang mengerjakan sesuatu |
| ◆ tunggu | `blocked` | Claude menunggu jawaban/izin Anda (dialog pertanyaan atau approval) |
| ● siap / ● selesai | `idle` / `done` | terbuka dan siap menerima prompt |
| ● terbuka | `unknown` | terbuka, tapi herdr belum bisa memastikan statusnya |
| ○ tutup | — | tidak ada proses; hanya transcript di disk |

## Instalasi

### Prasyarat
- **herdr** sudah terpasang dan dipakai sebagai terminal (lihat tutorial
  [wsl-flash-mikrokontroler](https://github.com/davidrizkisadewa/wsl-flash-mikrokontroler) untuk setup herdr).
- **Claude Code** sudah terpasang (`claude --version`).
- **Python 3** ada di PATH (`python --version`). Tidak perlu paket tambahan — panel memakai `msvcrt`
  dan escape ANSI bawaan Windows 10+.

### 1. Pasang / perbarui integrasi Claude di herdr
Integrasi ini (hook di `%USERPROFILE%\.claude\hooks\herdr-agent-state.ps1`) yang memberi tahu herdr
ID sesi dan status Claude di tiap pane. Tanpa ini semua sesi akan tampil **○ tutup**.

```powershell
herdr integration install claude
herdr integration status          # harus: claude: current (v11)
```

Jalankan ulang perintah pertama **setiap kali herdr di-update** — setelah update ke 0.9.5 integrasinya
sempat berstatus `outdated (v10 < v11)`.

### 2. Salin skrip
```powershell
New-Item -ItemType Directory -Force "$env:APPDATA\herdr\scripts"
Copy-Item scripts\claude-sesi.py "$env:APPDATA\herdr\scripts\"
```

### 3. Tambah pintasan di herdr
Tempel isi [`herdr/claude-sesi.toml`](herdr/claude-sesi.toml) ke `%APPDATA%\herdr\config.toml`
(di dekat blok `[[keys.command]]` lainnya):

```toml
[[keys.command]]
key = "prefix+alt+c"
type = "popup"
command = 'python.exe "%APPDATA%\herdr\scripts\claude-sesi.py"'
description = "panel sesi Claude Code (buka/tutup)"
width = "90%"
height = "80%"
```

Lalu periksa dan muat ulang config **tanpa** me-restart herdr:

```powershell
herdr config check                # harus: Config: ok
herdr server reload-config        # harus: "status":"applied"
```

### 4. Coba
Tekan **`Ctrl+B` lalu `Alt+C`**. Kalau daftar sesi muncul, instalasi selesai.

Pengecekan cepat tanpa popup (dijalankan di pane herdr):
```powershell
herdr agent list                  # sesi yang terbuka harus punya "agent_session":{"value":"<id>"}
python "$env:APPDATA\herdr\scripts\claude-sesi.py"   # panel juga bisa dijalankan langsung di pane
```

## Memakai panel

### Membaca daftar
Setiap baris berisi:

```
 ◆ tunggu   16 Oct 08:04  Riset brake bansai                                 David
 └ status   └ terakhir    └ judul sesi                                       └ folder kerja
            diubah
```

Urutan dari yang **terakhir dipakai** di atas. Baris yang dipilih tampil terbalik warnanya, dan bagian
bawah panel menunjukkan detailnya: ID lengkap, folder kerja, jumlah prompt, pane tempat sesi terbuka,
dan prompt terakhir Anda.

### Membuka sesi
1. Pilih sesi dengan <kbd>↑</kbd>/<kbd>↓</kbd> (atau cari dengan <kbd>/</kbd>).
2. Tekan <kbd>Enter</kbd>.
   - Sesi **○ tutup** → tab baru dibuat di folder kerja sesi itu, dinamai sesuai judulnya, lalu
     `claude --resume <id>` dijalankan. Percakapan lanjut dengan konteks lengkap.
   - Sesi yang **sudah terbuka** → popup tertutup dan Anda langsung dibawa ke tab & pane-nya
     (tidak membuka salinan kedua).

### Menutup sesi
1. Pilih sesi yang terbuka.
2. Tekan <kbd>X</kbd> (atau <kbd>Del</kbd>).
3. Konfirmasi <kbd>Y</kbd> muncul hanya bila:
   - sesi sedang **◐ kerja** — pekerjaan yang sedang berjalan akan terhenti, atau
   - sesi itu adalah **pane yang sedang Anda pakai** (misalnya sesi tempat Anda membuka popup).
4. Tunggu pesan *"Sesi ditutup"*. Statusnya berubah menjadi ○ tutup dan pane-nya hilang.

> Pastikan pekerjaan di sesi itu memang sudah selesai (misalnya commit/push sudah terkirim) sebelum
> menutupnya. Transcript aman, tetapi perintah yang sedang berjalan akan dihentikan.

### Mencari
Tekan <kbd>/</kbd>, ketik sebagian judul, nama folder, atau ID (mis. `brake`, `spedo`, `7930`). Daftar
langsung tersaring. <kbd>Enter</kbd> atau <kbd>↓</kbd> untuk kembali memilih, <kbd>Esc</kbd> untuk
menghapus pencarian.

### Hanya yang terbuka
Tekan <kbd>O</kbd> untuk melihat sesi yang sedang hidup saja — berguna untuk bersih-bersih RAM:
buka panel, <kbd>O</kbd>, lalu <kbd>X</kbd> pada sesi yang tidak dipakai.

## Apa yang terjadi saat membuka & menutup

### Enter pada sesi tertutup
```powershell
herdr tab create --cwd "<folder kerja sesi>" --label "<judul, maks 28 huruf>" --focus
# tunggu ±0,8 detik sampai prompt PowerShell di tab baru siap
herdr pane run <pane baru> "claude --resume <id-sesi>"
```
`claude --resume` mencari transcript berdasarkan folder kerja, karena itu tab baru **harus** dibuat di
folder yang sama dengan sesi aslinya. Bila folder itu sudah tidak ada, panel memakai `%USERPROFILE%`.

### Enter pada sesi terbuka
```powershell
herdr tab focus <tab_id>
herdr agent focus <pane_id>
```

### X (tutup)
```powershell
# bila status ◆ tunggu: tutup dialognya dulu
herdr agent send-keys <pane> esc
# bila status ◐ kerja (setelah konfirmasi): hentikan pekerjaannya
herdr agent send-keys <pane> ctrl+c
# keluar dengan rapi
herdr agent prompt <pane> "/exit"
# tunggu sampai sesi hilang dari `herdr agent list` (maks ±8 detik), lalu
herdr pane close <pane>
```
Pane ikut ditutup agar shell kosongnya tidak tertinggal dan memakan RAM. Bila Claude tidak keluar dalam
8 detik, `pane close` tetap menutupnya — transcript sudah tersimpan per pesan, jadi tidak ada yang hilang.

## Tanpa panel: perintah manual

| Keperluan | Perintah |
|---|---|
| Daftar sesi lama (pilih dengan panah) | `claude --resume` |
| Buka sesi tertentu | `claude --resume <id-sesi>` (jalankan di folder kerja sesi itu) |
| Lanjutkan sesi terakhir di folder ini | `claude --continue` |
| Lihat sesi yang sedang terbuka di herdr | `herdr agent list` |
| Pindah ke pane sebuah sesi | `herdr agent focus <pane_id>` |
| Tutup sesi dari dalamnya | ketik `/exit` |
| Lihat proses Claude & ID-nya | `Get-CimInstance Win32_Process -Filter "Name='claude.exe'" \| select ProcessId,CommandLine` |
| Lokasi transcript | `%USERPROFILE%\.claude\projects\<folder>\<id-sesi>.jsonl` |

## Kustomisasi

| Ingin mengubah | Caranya |
|---|---|
| Tombol pintasan | ganti `key = "prefix+alt+c"` di `config.toml`, lalu `herdr server reload-config`. Pastikan tidak bentrok dengan pintasan lain (`prefix+alt+p/m/s/g/f/t/e/w` sudah dipakai) |
| Ukuran popup | ubah `width` / `height` (persen layar) |
| Warna | ubah kamus `C` di awal `claude-sesi.py` (default Dracula, format `\x1b[38;2;R;G;Bm`) |
| Teks/ikon status | ubah `STATUS_STYLE` di `claude-sesi.py` |
| Lama menunggu `/exit` | ubah `range(16)` di `close_session` (16 × 0,5 dtk = 8 dtk) |
| Tampilkan juga sesi 0 prompt | hapus filter `s["turns"] > 0` di `load_sessions` |
| Folder transcript lain | ubah `PROJECTS` di awal skrip |

Tidak perlu restart apa pun setelah mengedit skrip — perubahan berlaku saat popup dibuka berikutnya.

## Masalah yang mungkin terjadi & solusinya

| Gejala | Penyebab | Solusi |
|---|---|---|
| Semua sesi tampil **○ tutup**, padahal ada yang terbuka | integrasi Claude di herdr belum terpasang/usang, atau sesi dimulai sebelum integrasi dipasang | `herdr integration install claude`, lalu tutup & buka lagi sesinya |
| `herdr integration status` → `claude: outdated` | herdr baru di-update | `herdr integration install claude` |
| Popup muncul lalu langsung hilang | `python.exe` tidak ada di PATH | cek `python --version`; atau ganti `command` dengan path lengkap, mis. `C:\Users\David\AppData\Local\Programs\Python\Python314\python.exe` |
| Tulisan *"Jalankan dari dalam herdr"* | skrip dijalankan di terminal biasa | buka dari herdr (`Ctrl+B` `Alt+C`) atau dari pane herdr |
| Muncul kode aneh seperti `←[2J` | konsol tidak mendukung ANSI (Windows lama / conhost lama) | pakai Windows Terminal; skrip sudah mengaktifkan VT mode lewat `os.system("")` |
| Sesi tidak ada di daftar | sesi belum punya prompt (0 prompt) atau transcript-nya di folder lain | lihat [Kustomisasi](#kustomisasi) |
| Enter membuka tab tapi `claude --resume` bilang sesi tidak ditemukan | folder kerja sesi sudah dipindah/dihapus sehingga tab dibuka di `%USERPROFILE%` | kembalikan foldernya, atau `cd` ke folder asal lalu `claude --resume <id>` |
| Tab baru terbuka tapi perintah tidak jalan | shell di tab baru belum siap dalam 0,8 dtk (PC sedang berat) | ketik sendiri `claude --resume <id>` (ID tampil di detail panel), atau naikkan `time.sleep(0.8)` di `open_session` |
| Judul sesi sama persis untuk dua sesi | sesi kedua adalah lanjutan (*continued*) dari yang pertama | bedakan dari tanggal dan ID di bagian detail |

## Lampiran: update herdr di Windows

Dicatat karena integrasi Claude perlu dipasang ulang setelah update, dan ada beberapa jebakan:

1. **`herdr update` menolak jalan dari dalam herdr** (*"run `herdr update` outside herdr after
   detaching from the session"*). Yang dicek hanya variabel lingkungan `HERDR_ENV=1` — **bukan** apakah
   client sedang attach. Jadi tidak perlu detach; cukup jalankan dari PowerShell yang bukan pane herdr.
   Tab Windows Terminal baru yang dibuka *dari* pane herdr (`wt new-tab`) ikut mewarisi `HERDR_ENV`,
   jadi tetap ditolak — buka tab baru lewat tombol <kbd>+</kbd> Windows Terminal.
2. **Live handoff (`--handoff`) tidak didukung di Windows** — server menjawab
   *"live handoff is only supported on Unix"*. Setelah update, client sudah versi baru tetapi server
   tetap versi lama (`herdr status` → `server_binary_stale: yes`) sampai server di-restart.
3. Server ikut versi baru setelah **restart PC** atau `herdr server stop` lalu `herdr` (keduanya
   **menutup semua pane** — sesi Claude bisa dibuka lagi lewat panel ini).
4. Setelah server baru jalan: `herdr integration install claude`.

```powershell
# dari PowerShell biasa (bukan pane herdr)
herdr update
herdr status                      # client: versi baru; server: lama sampai di-restart
herdr integration install claude
```

## Struktur repo

```
herdr-panel-sesi-claude/
├── README.md                 tutorial ini
├── scripts/
│   └── claude-sesi.py        panel (salin ke %APPDATA%\herdr\scripts\)
└── herdr/
    └── claude-sesi.toml      blok pintasan untuk %APPDATA%\herdr\config.toml
```
