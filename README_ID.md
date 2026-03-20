# Rojo GUI Launcher

> **v1.1** | GUI launcher untuk [Rojo](https://github.com/rojo-rbx/rojo) server dengan fitur file watcher dan monitoring.

## Fitur

### Core
- **Start/Stop Server** - Jalankan dan hentikan `rojo serve` dengan satu klik
- **File Watcher** - Deteksi perubahan file di `src/` secara real-time
- **Log ke File** - Simpan semua log ke folder `gui/logs/` (ANSI codes di-strip)
- **4 Tab Panel:**
  - Server Log - Output dari Rojo server
  - File Changes - Daftar file yang berubah dengan filter
  - Folder Projek - Tree view struktur `src/` dengan info file & preview
  - Logs - Kelola file log (delete)

### Baru di v1.1
- **Search/Filter** - Search bar dengan tombol filter di log
- **Double-click to Open** - Buka file di editor default
- **File Preview** - Preview isi file di tab Folder Projek
- **Toast Notification** - Popup saat file berubah
- **Auto-restart** - Auto restart server jika crash (max 3x retry)
- **Settings Panel** - Konfigurasi path project, editor, auto-restart, dll
- **Log Rotation** - Auto hapus log lama (max 50 file)
- **Export Log** - Copy ke clipboard atau simpan ke file
- **Keyboard Shortcuts** - Ctrl+1/2/3/4, Ctrl+S/Q/L, F5
- **System Tray** - Minimize ke tray dengan menu restore/quit
- **Multi-project** - Ganti project dengan dropdown

### UI
- **Custom UI** - Dark theme, borderless, resizable, draggable
- **Taskbar Entry** - Muncul di Windows taskbar
- **Konfirmasi Close** - Popup saat mau close saat server running
- **Error Handling** - Handle edge case lebih baik

## Syarat

- Python 3.8+ (dengan tkinter, sudah bawaan Python)
- [Rojo](https://github.com/rojo-rbx/rojo) sudah terinstall dan ada di PATH

> **Tips:** Jika install Python custom, pastikan centang "Add Python to PATH" saat install, atau gunakan `py` command.

## Install

```bash
# 1. Clone repo
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO/gui

# 2. Pastikan Rojo terinstall
rojo --version
```

## Cara Pakai

### GUI (Recommended)
```bash
# Pilih salah satu
py rojo_gui.py                    # Python Launcher
python rojo_gui.py                # Dari PATH
run.bat                           # Double-click (console auto-close)
```

### Command Line (Alternatif)
```bash
# PowerShell
.\serve.ps1

# Atau langsung
rojo serve
```

> **Tips:** `run.bat` dan `serve.ps1` otomatis deteksi nama project dari folder saat ini.

### Keyboard Shortcuts
| Shortcut | Aksi |
|----------|------|
| Ctrl+1 | Pindah ke Server Log |
| Ctrl+2 | Pindah ke File Changes |
| Ctrl+3 | Pindah ke Folder Projek |
| Ctrl+4 | Pindah ke Logs |
| Ctrl+L | Bersihkan log aktif |
| Ctrl+S | Start server |
| Ctrl+Q | Stop server |
| Ctrl+, | Buka settings |
| F5 | Refresh |

### Panduan Fitur
1. **Search/Filter** - Gunakan search bar untuk cari log, filter berdasarkan tipe
2. **Double-click** - Klik file di tree atau daftar perubahan untuk buka di editor
3. **Preview** - Klik file untuk lihat preview di panel kanan
4. **Toast** - Notifikasi muncul saat file berubah
5. **Settings** - Klik ⚙️ untuk konfigurasi project, editor, dll
6. **Export** - Klik 📋 untuk copy, 💾 untuk simpan log ke file
7. **Multi-project** - Klik nama project untuk ganti project

## Struktur Folder
```
gui/
├── parts/
│   ├── __init__.py
│   ├── config.py           # Auto-detect path project, recent projects
│   ├── theme.py            # Warna tema (GitHub Dark)
│   ├── widgets.py          # HoverButton, StatusDot
│   ├── title_bar.py        # Title bar, drag, resize
│   ├── log_panel.py        # Panel utama (4 tab)
│   ├── server.py           # Server controller dengan auto-restart
│   ├── file_watcher.py     # Monitor perubahan file
│   ├── search.py           # Search/filter bar
│   ├── file_opener.py      # Buka file di editor
│   ├── preview.py          # Preview file
│   ├── toast.py            # Toast notification
│   ├── settings.py         # Settings dialog
│   ├── log_rotation.py     # Auto-hapus log lama
│   ├── export.py           # Copy/export log
│   ├── shortcuts.py        # Keyboard shortcuts
│   ├── tray.py             # System tray manager
│   └── tabs/
│       ├── __init__.py
│       ├── server_log.py   # Tab Server Log
│       ├── file_changes.py # Tab File Changes
│       ├── folder_projek.py# Tab Folder Projek
│       └── logs.py         # Tab Logs
├── config.json             # Pengaturan project (auto-generated)
├── logs/                   # Log auto-generated
├── rojo_gui.py             # Entry point GUI
├── run.bat                 # Launcher (console auto-close)
├── serve.ps1               # Command line launcher
├── README.md               # Dokumentasi (English)
└── README_ID.md            # Dokumentasi (Indonesia)
```

## Teknis

| Komponen | Teknologi |
|----------|-----------|
| GUI | tkinter |
| Server | subprocess |
| Threading | threading |
| File Watch | os.stat (interval 1 detik) |
| Taskbar | ctypes (Windows API) |
| Config | JSON |

## Changelog

### v1.1
- Tambah search/filter di log
- Tambah double-click untuk buka file
- Tambah file preview
- Tambah toast notification
- Tambah auto-restart saat crash
- Tambah settings panel
- Tambah log rotation
- Tambah export log (copy/save)
- Tambah keyboard shortcuts
- Tambah system tray support
- Tambah multi-project support
- Fix ANSI codes di log file
- Fix thread safety issues
- Fix hardcoded nama project

### v1.0
- Rilis pertama
- Rojo server launcher dasar
- File watcher
- 4 tab panel
- Dark theme UI

## License

MIT
