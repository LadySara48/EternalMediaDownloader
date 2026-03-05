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

- Download video and audio from YouTube and many other platforms
- Clean and user-friendly GUI built with PyQt6
- Supports various formats and quality options
- Powered by the ever-updated yt-dlp engine

---

## 📦 Requirements

Before running the application, you need to install the following:

### 1. Python Dependencies

Need Python 3.10.X+

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

## 👥 Credits

See [CREDITS.md](CREDITS.md) for full credits and acknowledgements.

---

## 📄 License

This project is open source. Feel free to use, modify, and distribute.
