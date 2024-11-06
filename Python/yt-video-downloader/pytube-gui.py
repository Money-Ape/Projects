import yt_dlp
import subprocess as cmd
import platform
import importlib
import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
from tabulate import tabulate

current_os = platform.system()

def OS_platform_verify():
    global current_os

    # Windows.
    if current_os == "Windows":
        print("It seems like you have a platform = 'Windows'\n")

        # Module Installation.
        module_names = ["yt_dlp", "tabulate"]
        for module_name in module_names:
            if importlib.util.find_spec(module_name) is None:
                print(f"{module_name}.......Error")
                print(f"{module_name} is not installed.\nInstalling...")
                cmd.run(["cmd", "/c", "pip3", "install", module_name, "--quiet"])
            else:
                print(f"{module_name}.......ok")
                print(f"{module_name} is already installed.")
        print("Module Installation check complete.\n")

    # Linux
    elif current_os == "Linux":
        print("It seems like you have a platform = 'Linux'\n")

        # Module Installation.
        module_names = ["yt_dlp", "tabulate"]
        for module_name in module_names:
            if importlib.util.find_spec(module_name) is None:
                print(f"{module_name}.......Error")
                print(f"{module_name} is not installed.\nInstalling...")
                cmd.run(["pip3", "install", module_name])
            else:
                print(f"{module_name}.......ok")
                print(f"{module_name} is already installed.")
        print("Module Installation check complete.\n")

    else:
        print("Unsupported platform")

OS_platform_verify()

def format_file_size(size):
    if size is None:
        return "Unknown"
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0

def video_formats(url):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])

        formats_dict = {}
        for fmt in formats:
            format_id = fmt['format_id']
            filesize = fmt.get('filesize_approx', fmt.get('filesize'))
            formats_dict[format_id] = {
                'Extension': fmt.get('ext'),
                'Resolution': fmt.get('resolution'),
                'Quality': fmt.get('format_note'),
                'Filesize': format_file_size(filesize)
            }
        return formats_dict
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def display_formats():
    url = url_entry.get()
    formats_dict = video_formats(url)
    if not formats_dict:
        messagebox.showerror("Error", "No formats available or an error occurred.")
        return

    text_area.config(state=tk.NORMAL)
    text_area.delete(1.0, tk.END)
    formats_text.config(state=tk.NORMAL)
    formats_text.delete(1.0, tk.END)

    for format_id, format_info in formats_dict.items():
        text_area.insert(tk.END, f"FORMAT ID: {format_id}\n")
        for key, value in format_info.items():
            text_area.insert(tk.END, f"  {key}: {value}\n")
        text_area.insert(tk.END, "\n")

    example_data = f"""
[youtube] {url} : Downloading webpage
[info] Available formats for {url}:

Format Code  Extension  Resolution  Quality  FPS    Video Format
249          webm       None        tiny  ,  None,   audio only
250          webm       None        tiny  ,  None,   audio only
140          m4a        None        tiny  ,  None,   audio only
160          mp4        254x144     144p  ,  15fps,  video only
133          mp4        426x240     240p  ,  30fps,  video only
134          mp4        640x360     360p  ,  30fps,  video only
135          mp4        854x480     480p  ,  30fps,  video only
136          mp4        1280x720    720p  ,  30fps,  video only
137          mp4        1280x720    1080p ,  30fps,  video only
18           mp4        640x360     360p  ,  30fps,  mp4a.40.2@ 96k (44100Hz)
22           mp4        1280x720    720p  ,  30fps,  mp4a.40.2@192k (44100Hz)

You can add both video only and audio only format codes to download the video
E.g : 136+140
"""
    formats_text.insert(tk.END, example_data)

    message = "\nChoose the appropriate format code for downloading the video in the supported video quality.!"
    formats_text.insert(tk.END, message)

    text_area.config(state=tk.DISABLED)
    formats_text.config(state=tk.DISABLED)

def download_video():
    url = url_entry.get()
    format_v = format_entry.get()
    if current_os == "Windows":
        cmd.run(["cmd", "/c", "yt-dlp", "-f", f"{format_v}", f"{url}"])

    elif current_os == "Linux":
        cmd.run(["yt-dlp", "-f", f"{format_v}", f"{url}"])

    else:
        messagebox.showerror("Error", "Unsupported platform")

if __name__ == "__main__":
    OS_platform_verify()

    root = tk.Tk()
    root.title("Video Downloader")

    url_label = tk.Label(root, text="Video URL:")
    url_label.pack(padx=10, pady=5)

    url_entry = tk.Entry(root, width=80)
    url_entry.pack(padx=10, pady=5)

    fetch_button = tk.Button(root, text="Fetch Formats", command=display_formats)
    fetch_button.pack(padx=10, pady=3)

    top_frame = tk.Frame(root)
    top_frame.pack(padx=10, pady=10)

    text_area = scrolledtext.ScrolledText(top_frame, wrap=tk.WORD, width=50, height=10)
    text_area.pack(side=tk.TOP)

    formats_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=110, height=15)
    formats_text.pack(padx=10, pady=10)

    format_label = tk.Label(root, text="Enter Format Code:")
    format_label.pack(padx=10, pady=5)

    format_entry = tk.Entry(root, width=50)
    format_entry.pack(padx=10, pady=5)

    download_button = tk.Button(root, text="Download Video", command=download_video)
    download_button.pack(padx=10, pady=5)

    root.mainloop()
