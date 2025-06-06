# ipodfiller

A modern desktop app to download and organize music from public Spotify playlists, with full metadata, for use on classic iPods and other devices.

## Features

- Download tracks from any public Spotify playlist
- Automatic metadata embedding (title, artist, album, artwork)
- User-friendly graphical interface (CustomTkinter, Frutiger Aero style)
- Progress tracking and error handling
- Standalone executable distribution (no Python required for end users)
- In-app instructions and settings for Spotify API keys

## Prerequisites (for building)

- Python 3.8 or higher
- FFmpeg (for development/testing, but bundled for end users)
- pip (Python package manager)

## Installation (for developers)

1. Clone this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Download FFmpeg from https://www.gyan.dev/ffmpeg/builds/ and place `ffmpeg.exe` in your project folder (for building the executable).

## Usage (for developers)

1. Run the application:
   ```bash
   python main.py
   ```
2. Enter your Spotify API credentials in the app (Settings).
3. Paste a public Spotify playlist URL.
4. Choose a download directory.
5. Click "Start Download".

## Building a Standalone Executable

1. Make sure `ffmpeg.exe` is in your project folder.
2. Build with PyInstaller:
   ```bash
   pyinstaller --onefile --windowed --add-binary "ffmpeg.exe;." main.py
   ```
3. The executable will be in the `dist` folder as `main.exe`.

## For GitHub Users / Developers

- **The compiled `.exe` is NOT included in this repository.**
- If you clone this repo, you must run the app from source using Python (see "Usage (for developers)" above).
- If you want to build your own `.exe`, follow the "Building a Standalone Executable" instructions.

## Disclaimer

This application is provided solely for personal use and for obtaining music that you have the legal rights to access. I do not condone, support, or promote music piracy in any form. The purpose of this tool is to help manage and organize music that you already own or have explicit permission to use.

By using this application, you agree that it is your responsibility to comply with all applicable copyright laws and licensing agreements. I am not responsible for any illicit or unauthorized use of this application. Use it responsibly and ensure that you only download content for which you hold the necessary rights.

## Notes

- Only public Spotify playlists are supported.
- You must use your own Spotify API credentials (get them at https://developer.spotify.com/dashboard).
- Downloaded files are MP3s with full metadata.
- The app includes a disclaimer and is for personal, legal use only.
- The `.gitignore` file ensures that no binaries, secrets, or build artifacts are committed to the repository.

## License

MIT License
