Overview
Video Clip Downloader is a Python-based GUI application that enables users to download video clips from popular platforms like YouTube, TikTok, and Facebook. The tool provides the flexibility to specify start and end times for clips, select video resolution, download audio-only versions, and optionally download available transcripts. It uses yt-dlp for downloading and ffmpeg for video processing, wrapped in a user-friendly tkinter interface.

Features
Download Video Clips: Specify start and end times to download specific parts of a video.
Download Audio Only: Option to download just the audio from the video.
Resolution Selection: Choose from multiple resolutions (144p, 240p, 360p, 480p, 720p, 1080p).
Transcript Download: Automatically download available transcripts in text format.
Batch Downloading: Supports efficient, multi-threaded downloading using aria2c.
Cross-Platform: Runs on Windows, macOS, and Linux.

Installation
Prerequisites
Python 3.x (including tkinter for the GUI)
yt-dlp (Install via pip)
ffmpeg (Ensure it’s installed and added to your system's PATH)
aria2c (Optional, for faster downloads)

Steps
1.	Clone the repository:
git clone https://github.com/ttgrex1/Video-Clip-Downloader.git
cd video-clip-downloader

3.	Install the required Python packages:
pip install -r requirements.txt

5.	Run the application:
python main.py

Usage
1.	Enter the video URL from YouTube, TikTok, Facebook, Instagram, & more.
2.	Set the start and end times (optional).
3.	Choose the desired video resolution.
4.	Select the folder where the video should be saved.
5.	Toggle options for full video download, transcript download, and audio-only download.
6.	Click the Download button to start the process.

*Audio option only allows for full audio download at this time. 

Contributing
Contributions are welcome! Please submit a pull request or open an issue for any bugs or feature requests.
License
This project is licensed under the MIT License. See the LICENSE file for details.

