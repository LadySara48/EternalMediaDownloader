# 🎬 Eternal Media Downloader

A simple and powerful media downloader built with Python and PyQt6, powered by yt-dlp.  
Download videos and audio from hundreds of platforms with ease.

---

## ⚠️ Legal Disclaimer

Eternal Media Downloader is intended solely for downloading content that is copyright-free,
licensed for download, or for which you have explicit permission from the rights holder.

For users downloading content from major platforms such as YouTube, Instagram,
and similar services — any legal responsibility arising from the downloading of copyrighted or otherwise restricted material rests entirely with the user.
The developers of this application bear no liability for misuse.

Please be mindful of the terms of service of the platforms you use,
and always respect copyright law. You are strongly advised to use this application responsibly.

---

## ✨ Features

- 🎨 **Modern Dark UI** — Frameless window, rounded corners, smooth animations
- 🎵 **MP3 Downloads** — 96K / 128K / 148K bitrate options
- 🎬 **MP4 Downloads** — 360p / 480p / 720p / 1080p quality options
- 📥 **Multiple Downloads** — Queue system with configurable parallel limit
- 🚀 **Speed Control** — Per-download speed limiting
- 📋 **Download History** — Searchable, filterable, with re-download support
- ✅ **Completed Panel** — Open file/folder with one click
- ⚙️ **Settings** — Persistent configuration saved to JSON
- 🔍 **Smart Info Fetch** — Fetches video metadata before download

---

## 📦 Requirements

Before running the application, you need to install the following:

### 1. Python Dependencies

Need Python 3.11+

Install required Python packages via pip:

```bash
pip install -r requirements.txt
```

The `requirements.txt` includes:
- `PyQt6>=6.10.0` — GUI framework
- `yt-dlp>=2026.3.3` — Media downloading engine

---

### 2. FFmpeg (Required for merging video/audio and conversions)

Eternal Media Downloader requires **FFmpeg** to be installed and available in your system PATH.

#### Download FFmpeg

Go to the official FFmpeg builds page:  
👉 https://www.gyan.dev/ffmpeg/builds/

Download either:
- **FFmpeg Essentials** — lighter, recommended for most users
- **FFmpeg Full** — includes all codecs, for advanced use

#### Installing FFmpeg on Windows (Adding to PATH)

1. Download the zip file from the link above (e.g. `ffmpeg-release-essentials.zip`)
2. Extract the zip to a folder, for example:  
   `C:\ffmpeg`
3. Inside the extracted folder, find the `bin` folder:  
   `C:\ffmpeg\bin`  
   *(This folder should contain `ffmpeg.exe`, `ffprobe.exe`, etc.)*
4. Open **Start Menu** and search for **"Environment Variables"**
5. Click **"Edit the system environment variables"**
6. In the window that opens, click **"Environment Variables..."** button at the bottom
7. Under **"System variables"**, find and select the **`Path`** variable, then click **"Edit..."**
8. Click **"New"** and type the full path to the `bin` folder:  
   `C:\ffmpeg\bin`
9. Click **OK** on all windows to save
10. Open a new **Command Prompt** and verify the installation:
    ```bash
    ffmpeg -version
    ```
    If you see version information, FFmpeg is successfully installed! ✅

---

## 🚀 Running the Application

Once dependencies are installed:

```bash
python main.py
```

---

## 🛠️ Built With

- [Python](https://www.python.org/)
- [PyQt6](https://pypi.org/project/PyQt6/)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [FFmpeg](https://ffmpeg.org/)

---

## 📁 Project Structure

```
eternal_media_downloader/
├── main.py              # Entry point
├── run.cmd              # Windows launcher
├── requirements.txt     # Python dependencies
├── core/
│   ├── downloader.py    # yt-dlp subprocess engine
│   ├── settings.py      # Persistent settings manager
│   └── history.py       # Download history manager
├── ui/
│   ├── main_window.py   # Frameless main window
│   ├── title_bar.py     # Custom title bar
│   ├── sidebar.py       # Animated sidebar navigation
│   ├── pages.py         # All content pages
│   ├── download_card.py # Download progress card
│   ├── format_dialog.py # Format selection dialog
│   └── theme.py         # Colors, fonts, dimensions
└── data/
    ├── settings.json    # User settings (auto-generated)
    └── history.json     # Download history (auto-generated)
```

---

## ⚠️ Disclaimer (Try)

This application is a **GUI wrapper** and does not contain any download engines.  
It relies on user-installed tools (yt-dlp, ffmpeg).  
Please respect copyright laws and terms of service of content platforms.

---

## 👥 Credits

See [CREDITS.md](CREDITS.md) for full credits and acknowledgements.

---

## 📄 License

MIT License — See [LICENSE](LICENSE) for details.
