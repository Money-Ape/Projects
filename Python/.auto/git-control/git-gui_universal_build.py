import subprocess
import platform
import os
import time
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import threading
import pickle
import queue

current_os = platform.system()

# Get the directory where the main script is stored
script_dir = os.path.dirname(os.path.abspath(__file__))
folder_save_file = os.path.join(script_dir, 'git_folder_path.bin')

# Global variables to store the selected folder, push state, and lock
selected_folder = None
pending_push = False
timer_value = 120  # Initial timer value set to 2 minutes (120 seconds)
lock = threading.Lock()  # To handle thread-safe operations

# Create a queue for thread-safe communication
user_input_queue = queue.Queue()

# Initialize Tkinter
root = tk.Tk()
root.title("Git Automation Tool")

def save_folder_to_file(folder_path):
    """Save the selected folder path to a binary file."""
    with open(folder_save_file, 'wb') as f:
        pickle.dump(folder_path, f)

def load_folder_from_file():
    """Load the folder path from a binary file."""
    if os.path.exists(folder_save_file):
        with open(folder_save_file, 'rb') as f:
            return pickle.load(f)
    return None

def select_folder():
    """Let user select the folder and save it."""
    global selected_folder
    root.withdraw()  # Hide the main window during folder selection

    selected_folder = filedialog.askdirectory(title="Select your Git repository folder")
    if selected_folder:
        save_folder_to_file(selected_folder)
        check_git_installation(selected_folder)
        show_fetch_button()  # Show fetch button if folder is selected
        folder_button.config(state=tk.DISABLED)  # Disable folder button
    else:
        messagebox.showwarning("Warning", "No folder selected. Please select a folder.")
    root.deiconify()  # Show the main window again

def check_git_installation(directory):
    """Check if Git is installed and valid in the selected directory."""
    if current_os == "Linux":
        output_area.config(state=tk.NORMAL)
        output_area.delete('1.0', tk.END)
        output_area.insert(tk.END, "Platform detected: Windows\n", ('bold'))
        try:
            os.chdir(directory)
            result = run_git_command(['git', '--version'])
            if result.returncode == 0:
                output_area.insert(tk.END, f"Git is installed: {result.stdout}\n", ('bold'))
                
                # Display Git user information
                user_name = run_git_command(['git', 'config', 'user.name']).stdout.strip()
                user_mail = run_git_command(['git', 'config', 'user.email']).stdout.strip()
                output_area.insert(tk.END, f"Git User Name : {user_name}\n", ('bold', 'green'))
                output_area.insert(tk.END, f"Git User Email : {user_mail}\n\n", ('bold', 'green'))
                
                # Display remote URLs
                remote_urls = run_git_command(['git', 'remote', '-v']).stdout
                output_area.insert(tk.END, f"Git Remote URLs:\n{remote_urls}\n", ('bold', 'green'))
                
                start_monitor_thread()
            else:
                output_area.insert(tk.END, "Git is not installed.\n", ('bold'))
        except FileNotFoundError:
            output_area.insert(tk.END, "Git is not installed.\n", ('bold'))
        except Exception as e:
            output_area.insert(tk.END, f"Error: {str(e)}\n", ('bold'))
        output_area.config(state=tk.DISABLED)
    else:
        messagebox.showerror("Error", "This script is designed for Linux operating systems.")

def run_git_command(command_list):
    """Run a Git command and return the result."""
    result = subprocess.run(command_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result

def monitor_changes():
    """Continuously monitor the repository for changes."""
    global pending_push
    while True:
        result = run_git_command(['git', 'status'])
        if 'modified:' in result.stdout or 'deleted:' in result.stdout or 'new file:' in result.stdout:
            def update_gui():
                with lock:
                    output_area.config(state=tk.NORMAL)
                    output_area.delete('1.0', tk.END)
                    output_area.insert(tk.END, "Changes detected.\n", ('bold'))

                    # Collect modified and new files
                    modified_files = []
                    new_files = []
                    for line in result.stdout.splitlines():
                        if 'modified:' in line:
                            modified_files.append(line)
                        elif 'new file:' in line:
                            new_files.append(line)
                    
                    if modified_files or new_files:
                        output_area.insert(tk.END, "Modified files:\n" + "\n".join(modified_files) + "\n", ('bold'))
                        output_area.insert(tk.END, "New files:\n" + "\n".join(new_files) + "\n", ('bold'))
                        
                        # Put a prompt request in the queue
                        user_input_queue.put('prompt_add_files')

                    output_area.config(state=tk.DISABLED)

            root.after(0, update_gui)
        else:
            def update_gui_no_changes():
                with lock:
                    output_area.config(state=tk.NORMAL)
                    output_area.insert(tk.END, "No local changes detected. Pulling from remote...\n", ('bold'))
                    output_area.config(state=tk.DISABLED)
                
                git_pull()  # Make the pull operation
            
            root.after(0, update_gui_no_changes)

        time.sleep(120)  # Check status every 120 seconds

def handle_user_input():
    """Handle user input from the queue."""
    while not user_input_queue.empty():
        action = user_input_queue.get()
        if action == 'prompt_add_files':
            # Schedule a dialog prompt in the main thread
            root.after(0, ask_for_permission)

def ask_for_permission():
    """Prompt the user for permission to add files."""
    user_response = messagebox.askyesno("Permission Request", "Do you want to add these files to the staging area?")
    
    if user_response:
        # User agreed to add files
        result = run_git_command(['git', 'add', '.'])
        output_area.config(state=tk.NORMAL)
        output_area.insert(tk.END, f"Added files:\n{result.stdout}\n", ('bold'))

        # Commit message prompt
        commit_message = simpledialog.askstring("Commit Message", "Enter commit message for your changes:")
        if commit_message is None:  # User canceled the dialog
            output_area.insert(tk.END, "Commit operation canceled by user. Continuing monitoring...\n", ('bold'))
            output_area.config(state=tk.DISABLED)
            reset_timer()  # Reset the timer
            return

        if not commit_message.strip():
            messagebox.showwarning("Warning", "Commit message cannot be empty.")
            output_area.config(state=tk.DISABLED)
            return

        result = run_git_command(['git', 'commit', '-m', commit_message])
        output_area.insert(tk.END, f"Commit result:\n{result.stdout}\n", ('bold'))
        global pending_push
        pending_push = True  # Indicate that there's a pending push
        push_button.config(state=tk.NORMAL)  # Enable the push button
    else:
        output_area.config(state=tk.NORMAL)
        output_area.insert(tk.END, "Add operation declined by user. Continuing monitoring...\n", ('bold'))
        output_area.config(state=tk.DISABLED)

def git_pull():
    """Run git pull to fetch remote changes."""
    if selected_folder is None:
        output_area.config(state=tk.NORMAL)
        output_area.insert(tk.END, "No folder selected. Please select a folder.\n", ('bold', 'red'))
        output_area.config(state=tk.DISABLED)
        return

    output_area.config(state=tk.NORMAL)
    output_area.insert(tk.END, "Pulling changes from remote...\n", ('bold'))
    output_area.config(state=tk.DISABLED)

    # Run git pull
    result = run_git_command(['git', 'pull', 'origin', 'main'])

    with lock:
        output_area.config(state=tk.NORMAL)
        output_area.insert(tk.END, f"Pull result:\n{result.stdout}\n", ('bold'))

        # Check for stderr output but only if it contains actual errors
        if result.stderr and 'error:' in result.stderr:
            output_area.insert(tk.END, f"Pull error:\n{result.stderr}\n", ('bold', 'red'))
        
        # Check for specific git pull responses
        if 'Already up to date.' in result.stdout:
            output_area.insert(tk.END, "Repository is already up to date.\n", ('bold', 'green'))
        elif 'Updating' in result.stdout and 'Fast-forward' in result.stdout:
            output_area.insert(tk.END, "Merge completed successfully. Changes were fast-forwarded.\n", ('bold', 'green'))
        elif 'Merge conflict' in result.stdout or 'Merge conflict' in result.stderr:
            output_area.insert(tk.END, "Merge conflict detected. Please resolve the conflicts manually.\n", ('bold', 'red'))

        output_area.config(state=tk.DISABLED)

def git_push():
    """Run git push to push changes to the remote."""
    global pending_push
    if not pending_push:
        messagebox.showinfo("Info", "No pending changes to push.")
        return

    with lock:
        output_area.config(state=tk.NORMAL)
        output_area.insert(tk.END, "Pushing changes to remote...\n", ('bold'))

        # Run the git push command
        result = run_git_command(['git', 'push', '--verbose', 'origin', 'main'])

        # Display push results with relevant information only
        if result.stdout:
            lines = result.stdout.strip().splitlines()
            push_result_lines = []
            for line in lines:
                # Capture lines related to the push result (successful output)
                if line.startswith('Enumerating objects:') or line.startswith('Counting objects:') or \
                   line.startswith('Compressing objects:') or line.startswith('Writing objects:') or \
                   line.startswith('Total ') or '->' in line:  # Keep only the essential details
                    push_result_lines.append(line)

            if push_result_lines:
                output_area.insert(tk.END, "Push result:\n" + "\n".join(push_result_lines) + "\n", ('bold'))

        # Handle actual errors only if there's no valid push output
        if result.stderr and not result.stdout.strip():
            error_lines = result.stderr.strip().splitlines()
            if error_lines:
                output_area.insert(tk.END, "Push error:\n" + "\n".join(error_lines) + "\n", ('bold', 'red'))

        # Reset pending push flag
        pending_push = False
        push_button.config(state=tk.DISABLED)  # Disable push button
        
        output_area.config(state=tk.DISABLED)

def start_monitor_thread():
    """Start a background thread to monitor changes."""
    monitor_thread = threading.Thread(target=monitor_changes, daemon=True)
    monitor_thread.start()

def reset_timer():
    """Reset the countdown timer."""
    global timer_value
    timer_value = 120  # Reset to 2 minutes

def update_timer():
    """Update the countdown timer display."""
    global timer_value
    if timer_value > 0:
        timer_value -= 1
        timer_display.config(text=f"Next Check In: {timer_value} seconds")
    else:
        timer_display.config(text="Time's up!")
        # Trigger a manual check or other actions if needed
        root.after(0, handle_user_input)  # Ensure user input is handled
        reset_timer()  # Reset the timer after it reaches zero
    root.after(1000, update_timer)  # Update every second

def periodic_check():
    """Periodically check for user input and update the GUI."""
    handle_user_input()
    root.after(100, periodic_check)  # Check every 100 milliseconds

def show_fetch_button():
    """Display the 'Fetch' button."""
    fetch_button.pack(side=tk.LEFT, padx=5, pady=5)
    fetch_button.config(state=tk.NORMAL)  # Ensure the button is enabled

def fetch_button_click():
    """Handle fetch button click."""
    output_area.config(state=tk.NORMAL)
    output_area.insert(tk.END, "Fetching changes from remote...\n", ('bold'))

    # Run git fetch command
    result = run_git_command(['git', 'fetch', 'origin', 'main'])

    with lock:
        output_area.config(state=tk.NORMAL)
        
        # Show fetch result from stderr since it contains the relevant information
        if result.stderr:
            output_area.insert(tk.END, f"Fetch result:\n{result.stderr.strip()}\n", ('bold'))

        # Ensure no unnecessary debug or error information is displayed
        output_area.config(state=tk.DISABLED)

# Define GUI components
frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

folder_button = tk.Button(frame, text="Select Git Folder", command=select_folder)
folder_button.pack(side=tk.LEFT, padx=5, pady=5)

push_button = tk.Button(frame, text="Push Changes", command=git_push, state=tk.DISABLED)
push_button.pack(side=tk.LEFT, padx=5, pady=5)

fetch_button = tk.Button(frame, text="Fetch", command=fetch_button_click, state=tk.DISABLED)
fetch_button.pack(side=tk.LEFT, padx=5, pady=5)

exit_button = tk.Button(frame, text="Exit", command=root.quit)
exit_button.pack(side=tk.RIGHT, padx=5, pady=5)

# Timer display
timer_display = tk.Label(root, text=f"Next Check In: {timer_value} seconds", font=('Helvetica', 12))
timer_display.pack(padx=10, pady=5)

# Output area
output_area = tk.Text(root, wrap=tk.WORD, height=15, width=80)
output_area.tag_configure('bold', font=('Helvetica', 10, 'bold'))
output_area.tag_configure('green', foreground='green')
output_area.tag_configure('red', foreground='red')
output_area.pack(padx=10, pady=10)
output_area.config(state=tk.DISABLED)

# Load folder path if exists
selected_folder = load_folder_from_file()
if selected_folder:
    check_git_installation(selected_folder)
    show_fetch_button()  # Show fetch button if folder is loaded
    folder_button.config(state=tk.DISABLED)  # Disable folder button

# Start the periodic update loop, timer, and monitoring
root.after(100, periodic_check)  # Start periodic check
update_timer()  # Start the timer
start_monitor_thread()  # Start monitoring in a separate thread

# Start Tkinter event loop
root.mainloop()
