import os
import logging
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import yt_dlp

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def convert_time_to_seconds(time_str):
    parts = list(map(int, time_str.split(':')))
    if len(parts) == 2:
        minutes, seconds = parts
        hours = 0
    elif len(parts) == 3:
        hours, minutes, seconds = parts
    else:
        raise ValueError("Invalid time format")
    return hours * 3600 + minutes * 60 + seconds

def sanitize_filename(filename):
    return "".join([c if c.isalnum() or c in (' ', '.', '_') else '_' for c in filename])

def download_video_with_yt_dlp(url, start_time=None, end_time=None, output_file="output", resolution='720'):
    try:
        logging.info(f"Starting download process for URL: {url}")
        ydl_opts = {
            'format': f'bestvideo[height<={resolution}]+bestaudio/best[height<={resolution}]',
            'outtmpl': f'{output_file}.%(ext)s',
            'verbose': True,
            'noplaylist': True,
            'progress_hooks': [cleanup_hook],
            'external_downloader': 'aria2c',  # Use aria2c as external downloader
            'external_downloader_args': ['-x', '16', '-s', '16', '-k', '1M'],  # Aria2c arguments for multiple connections
        }

        logging.debug(f"yt-dlp options: {ydl_opts}")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logging.info("Extracting video info...")
            info_dict = ydl.extract_info(url, download=True)
            logging.debug(f"Video info: {info_dict}")
            
            filename = ydl.prepare_filename(info_dict)
            logging.info(f"Download completed. Temporary file: {filename}")

        if start_time and end_time:
            start_seconds = convert_time_to_seconds(start_time)
            end_seconds = convert_time_to_seconds(end_time)

            final_output_file = f"{output_file}_{sanitize_filename(info_dict['title'])}.mp4"
            logging.info(f"Preparing to extract clip to: {final_output_file}")

            ffmpeg_command = [
                'ffmpeg',
                '-i', filename,
                '-ss', str(start_seconds),
                '-to', str(end_seconds),
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-strict', 'experimental',
                final_output_file
            ]

            logging.info(f"Executing FFmpeg command: {' '.join(ffmpeg_command)}")
            result = subprocess.run(ffmpeg_command, check=True, capture_output=True, text=True)
            logging.debug(f"FFmpeg output: {result.stdout}")
            logging.debug(f"FFmpeg error (if any): {result.stderr}")

            logging.info(f"Removing temporary file {filename}")
            os.remove(filename)

            logging.info(f"Clip saved as {final_output_file}")
            return final_output_file
        else:
            final_output_file = f"{output_file}_{sanitize_filename(info_dict['title'])}.mp4"
            os.rename(filename, final_output_file)
            return final_output_file

    except yt_dlp.DownloadError as e:
        logging.error(f"yt-dlp download error: {e}")
        raise
    except subprocess.CalledProcessError as e:
        logging.error(f"FFmpeg error: {e}")
        logging.error(f"FFmpeg output: {e.output}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error: {e}", exc_info=True)
        raise

def cleanup_hook(d):
    if d['status'] == 'finished':
        filename = d['filename']
        base, ext = os.path.splitext(filename)
        part_file = base + '.part'
        ytdl_file = base + '.ytdl'
        try:
            if os.path.exists(part_file):
                os.remove(part_file)
            if os.path.exists(ytdl_file):
                os.remove(ytdl_file)
        except OSError as e:
            logging.error(f"Error removing temporary files: {e}")


def download_youtube_transcript(url, output_folder):
    try:
        logging.debug(f"Downloading transcript from URL: {url}")
        ydl_opts = {
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en'],
            'skip_download': True,
            'outtmpl': os.path.join(output_folder, 'temp.%(ext)s')
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            
            # Check for both manual and automatic subtitles
            subtitle_file = None
            for file in os.listdir(output_folder):
                if file.endswith('.vtt'):
                    subtitle_file = os.path.join(output_folder, file)
                    break

            if subtitle_file:
                txt_filename = subtitle_file.replace(".vtt", ".txt")
                vtt_to_txt(subtitle_file, txt_filename)
                os.remove(subtitle_file)
                logging.info(f"Transcript saved as {txt_filename}")
                return txt_filename
            else:
                logging.info("No transcript available.")
                return None

    except Exception as e:
        logging.error(f"Error downloading transcript: {e}")
        return None

def execute_download(url, start_time, end_time, folder, resolution, download_full, download_transcript_option):
    try:
        output_file = os.path.join(folder, "output")

        if download_full:
            final_file = download_video_with_yt_dlp(url, output_file=output_file, resolution=resolution)
        else:
            final_file = download_video_with_yt_dlp(url, start_time, end_time, output_file=output_file, resolution=resolution)

        messagebox.showinfo("Success", f"Video downloaded and saved as: {final_file}")

        if download_transcript_option:
            transcript_file = download_youtube_transcript(url, folder)
            if transcript_file:
                messagebox.showinfo("Success", f"Transcript downloaded successfully: {transcript_file}")
            else:
                messagebox.showinfo("Info", "No transcript available for this video.")

    except Exception as e:
        logging.error(f"Error during download: {e}", exc_info=True)
        messagebox.showerror("Error", f"Download failed: {str(e)}")

def browse_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        folder_path.set(folder_selected)

# Custom switch class
class Switch(tk.Frame):
    def __init__(self, master=None, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)
        self.config(width=42, height=21, bg="white")  # Further adjusted width and height

        self.canvas = tk.Canvas(self, width=42, height=21, bg="white", bd=0, highlightthickness=0)
        self.canvas.pack()
        
        self.is_on = False
        self.canvas.bind("<Button-1>", self.toggle)
        
        self.switch_id = self.canvas.create_rectangle(2, 2, 40, 19, outline="black", fill="white")
        self.knob_id = self.canvas.create_oval(2, 2, 19, 19, outline="black", fill="gray")

    def toggle(self, event=None):
        self.is_on = not self.is_on
        self.update_switch()

    def update_switch(self):
        if self.is_on:
            self.canvas.itemconfig(self.switch_id, fill="lightgreen")
            self.canvas.coords(self.knob_id, 23, 2, 40, 19)
        else:
            self.canvas.itemconfig(self.switch_id, fill="white")
            self.canvas.coords(self.knob_id, 2, 2, 19, 19)

    def get_state(self):
        return self.is_on

# GUI setup
def create_gui():
    root = tk.Tk()
    root.title("Video Clip Downloader")
    root.geometry("500x400")
    root.configure(bg='black')

    style = ttk.Style()
    style.theme_use('clam')
    style.configure('TLabel', background='black', foreground='white')
    style.configure('TButton', background='gray', foreground='white')
    style.configure('TEntry', fieldbackground='darkgray', foreground='black')
    style.configure('TCheckbutton', background='black', foreground='white')
    style.configure('TCombobox', fieldbackground='darkgray', foreground='black', background='gray')

    ttk.Label(root, text="Enter Video URL:").pack(pady=5)
    url_entry = ttk.Entry(root, width=50)
    url_entry.pack(pady=5)

    time_frame = tk.Frame(root, bg='black')
    time_frame.pack(pady=5)

    ttk.Label(time_frame, text="Start Time (hh:mm:ss):").pack(side='left', padx=5)
    start_time_entry = ttk.Entry(time_frame, width=10)
    start_time_entry.insert(0, "0:00:00")
    start_time_entry.pack(side='left', padx=5)

    ttk.Label(time_frame, text="End Time (hh:mm:ss):").pack(side='left', padx=5)
    end_time_entry = ttk.Entry(time_frame, width=10)
    end_time_entry.insert(0, "0:03:00")
    end_time_entry.pack(side='left', padx=5)

    # Create a frame for the download full video switch
    download_full_frame = tk.Frame(root, bg='black')
    download_full_frame.pack(pady=5)
    ttk.Label(download_full_frame, text="Download Full Video:").pack(side='left', padx=5)
    download_full_switch = Switch(download_full_frame)
    download_full_switch.pack(side='left', padx=5)

    # Create a frame for the download transcript switch
    download_transcript_frame = tk.Frame(root, bg='black')
    download_transcript_frame.pack(pady=5)
    ttk.Label(download_transcript_frame, text="Download Transcript (if available):").pack(side='left', padx=5)
    download_transcript_switch = Switch(download_transcript_frame)
    download_transcript_switch.pack(side='left', padx=5)

    ttk.Label(root, text="Resolution:").pack(pady=5)
    resolution_var = tk.StringVar(value='720p')
    resolution_menu = ttk.Combobox(root, textvariable=resolution_var, values=['144p', '240p', '360p', '480p', '720p', '1080p'])
    resolution_menu.pack(pady=5)

    global folder_path
    folder_path = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Downloads"))
    ttk.Label(root, text="Save Folder:").pack(pady=5)

    folder_frame = tk.Frame(root, bg='black')
    folder_frame.pack(pady=5, fill='x')

    folder_entry = ttk.Entry(folder_frame, textvariable=folder_path, width=40)
    folder_entry.pack(side='left', padx=5, fill='x', expand=True)

    browse_button = tk.Button(folder_frame, text="Browse", command=browse_folder, bg='blue', fg='white', activebackground='darkblue', relief='flat', bd=0, highlightthickness=0)
    browse_button.pack(side='left', padx=5)
    browse_button.configure(width=10, height=1)
    browse_button.bind("<Enter>", lambda e: browse_button.configure(bg='darkblue'))
    browse_button.bind("<Leave>", lambda e: browse_button.configure(bg='blue'))
    browse_button.configure(borderwidth=1, relief="solid", highlightthickness=1, highlightbackground="blue")
    browse_button.configure(borderwidth=2, highlightcolor='blue')

    import threading

    def start_download():
        url = url_entry.get()
        start_time = start_time_entry.get()
        end_time = end_time_entry.get()
        folder = folder_path.get()
        resolution = resolution_var.get()
        download_full = download_full_switch.get_state()
        download_transcript_option = download_transcript_switch.get_state()
        if not url or (not download_full and (not start_time or not end_time)):
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        def download_thread():
            execute_download(url, start_time, end_time, folder, resolution, download_full, download_transcript_option)
        
        threading.Thread(target=download_thread, daemon=True).start()

    download_button = tk.Button(root, text="Download", command=start_download, bg='green', fg='white', activebackground='darkgreen', relief='flat', bd=0, highlightthickness=0)
    download_button.pack(pady=20, side='bottom')
    download_button.configure(width=15, height=2)
    download_button.bind("<Enter>", lambda e: download_button.configure(bg='darkgreen'))
    download_button.bind("<Leave>", lambda e: download_button.configure(bg='green'))
    download_button.configure(borderwidth=1, relief="solid", highlightthickness=1, highlightbackground="green")
    download_button.configure(borderwidth=2, highlightcolor='green')

    root.mainloop()

if __name__ == "__main__":
    create_gui()
