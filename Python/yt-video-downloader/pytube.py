import yt_dlp
import subprocess as cmd
import platform
import importlib
import tkinter as tk
from tkinter import scrolledtext, messagebox
from tabulate import tabulate

current_os = platform.system()
formats_dict = {}

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
    global formats_dict

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
"""
    example_data += tabulate(
        [(fid, fmt['Extension'], fmt['Resolution'], fmt['Quality'], fmt['Filesize']) for fid, fmt in formats_dict.items()],
        headers=["Format Code", "Extension", "Resolution", "Quality", "Filesize"],
        tablefmt="plain"
    )

    formats_text.insert(tk.END, example_data)

    message = "\nChoose the appropriate format code for downloading the video in the supported video quality.!"
    formats_text.insert(tk.END, message)

    text_area.config(state=tk.DISABLED)
    formats_text.config(state=tk.DISABLED)

def download_video():
    url = url_entry.get()
    format_v = format_entry.get()
    if current_os == "Windows":
        cmd.run(["cmd", "/c", "yt-dlp", "-f", format_v, url])
    elif current_os == "Linux":
        cmd.run(["yt-dlp", "-f", format_v, url])
    else:
        messagebox.showerror("Error", "Unsupported platform")

if __name__ == "__main__":
    OS_platform_verify()

    root = tk.Tk()
    root.title("Video Downloader")

    url_label = tk.Label(root, text="Video URL:")
    url_label.pack(padx=10, pady=5)

    url_entry = tk.Entry(root, width=100)
    url_entry.pack(padx=10, pady=5)

    fetch_button = tk.Button(root, text="Fetch Formats", command=display_formats)
    fetch_button.pack(padx=10, pady=5)

    top_frame = tk.Frame(root)
    top_frame.pack(padx=10, pady=10)

    text_area = scrolledtext.ScrolledText(top_frame, wrap=tk.WORD, width=50, height=10)
    text_area.pack(side=tk.TOP)

    formats_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=110, height=15)
    formats_text.pack(padx=10, pady=10)

    # Create format input widgets but don't pack them initially
    format_label = tk.Label(root, text="Enter Format Code:")
    format_label.pack(padx=10, pady=5)

    format_entry = tk.Entry(root, width=50)
    format_entry.pack(padx=10, pady=5)

    download_button = tk.Button(root, text="Download Video", command=download_video)
    download_button.pack(padx=10, pady=5)

    root.mainloop()
