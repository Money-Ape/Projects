import yt_dlp
import subprocess as cmd
import platform
import importlib
import tkinter as tk
from tkinter import scrolledtext
from tabulate import tabulate

current_os = platform.system()

def OS_platform_verify():
    global current_os

    # Windows.
    if current_os == "Windows":
        print("It seems like you've a platform = 'Windows'\n")

        # Module Installation.
        module_names = ["yt-dlp", "tabulate"]
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
        print("It seems like you've a platform = 'Linux'\n")

        # Module Installation.
        module_names = ["yt-dlp", "tabulate"]
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
        print("Computer Kharab hai", "\n"
              "Mujhe Dede tere kisi kaam ka nhi.!!!"
              )

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

def display_formats(formats_dict, url):
    if not formats_dict:
        print("No formats available or an error occurred.")
        return

    root = tk.Tk()
    root.title("Video Formats")

    top_frame = tk.Frame(root)
    top_frame.pack(padx=10, pady=10)

    bottom_frame = tk.Frame(root)
    bottom_frame.pack(padx=10, pady=10)

    text_area = scrolledtext.ScrolledText(top_frame, wrap=tk.WORD, width=50, height=10)
    text_area.pack(side=tk.TOP)

    formats_text = scrolledtext.ScrolledText(bottom_frame, wrap=tk.WORD, width=100, height=15)
    formats_text.pack(side=tk.BOTTOM)

    for format_id, format_info in formats_dict.items():
        text_area.insert(tk.END, f"FORMAT ID: {format_id}\n")
        for key, value in format_info.items():
            text_area.insert(tk.END, f"  {key}: {value}\n")
        text_area.insert(tk.END, "\n")

    example_data = f"""
[youtube] {url} : Downloading webpage
[info] Available formats for {url}:
format code  extension  resolution note
249          webm       audio only tiny   50k , opus @ 50k (48000Hz), 1.42MiB
250          webm       audio only tiny   64k , opus @ 70k (48000Hz), 1.83MiB
140          m4a        audio only tiny  128k , m4a_dash container, mp4a.40.2@128k (44100Hz), 3.51MiB
160          mp4        144p        144p   10k , avc1.4d400c, 15fps, video only, 1.13MiB
133          mp4        240p        240p   50k , avc1.4d4015, 30fps, video only, 2.61MiB
134          mp4        360p        360p  100k , avc1.4d401e, 30fps, video only, 4.64MiB
135          mp4        480p        480p  200k , avc1.4d401f, 30fps, video only, 8.37MiB
136          mp4        720p        720p  500k , avc1.4d401f, 30fps, video only, 17.34MiB
137          mp4        1080p       1080p 1000k , avc1.640028, 30fps, video only, 33.87MiB
18           mp4        360p        360p  100k , avc1.42001E, 30fps, mp4a.40.2@ 96k (44100Hz), 11.11MiB
22           mp4        720p        720p  200k , avc1.64001F, 30fps, mp4a.40.2@192k (44100Hz) (best)
"""
    formats_text.insert(tk.END, example_data)

    message = "\nChoose the appropriate format code for downloading the video in the supported video quality.!"
    formats_text.insert(tk.END, message)

    text_area.config(state=tk.DISABLED)
    formats_text.config(state=tk.DISABLED)
    root.mainloop()

    return formats_dict

url = input("Link for individual video: ")
formats_dict = video_formats(url)
display_formats(formats_dict, url)

format_v = input("Choose your format for video quality,\nEnter your format: ")

if current_os == "Windows":
    cmd.run(["cmd", "/c", "yt-dlp", "-f", format_v, url])

elif current_os == "Linux":
    cmd.run(["yt-dlp", "-f", format_v, url])
    
else:
    print("Something is wrong with the link or the format you provided is not supported.")
