import subprocess
import platform
import os
import tkinter as tk
from tkinter import filedialog

current_os = platform.system()

def select_folder():
    # Create a Tk root widget (it won't be displayed)
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Open a folder selection dialog
    folder_selected = filedialog.askdirectory(title="Select your Git repository folder")
    
    return folder_selected

def check_git_installation(directory):
    # Check if the platform is Linux (or adjust for your desired platform)
    if current_os == "Linux":
        print("\033[33m \033[1mPlatform detected.! = 'Linux'\033[0m")
        try:
            # Change to the selected directory
            os.chdir(directory)

            # Try to check if Git is installed by running 'git --version'
            result = subprocess.run(['git', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                print(f"\033[33m \033[1mGit is installed : {result.stdout}\033[0m")

                # Now check the Git user name and email
                user_name = subprocess.run(['git', 'config', 'user.name'], stdout=subprocess.PIPE, text=True)
                user_email = subprocess.run(['git', 'config', 'user.email'], stdout=subprocess.PIPE, text=True)

                # Check if the values are set and not empty
                if user_name.stdout.strip():
                    print(f"\033[32m \033[1mGit User Name: {user_name.stdout.strip()}\033[0m")
                else:
                    print("\033[31m \033[1mGit User Name is not configured.\033[0m")

                if user_email.stdout.strip():
                    print(f"\033[32m \033[1mGit User Email: {user_email.stdout.strip()}\033[0m")
                else:
                    print("\033[31m \033[1mGit User Email is not configured.\033[0m")

                # Call the git operation function with user input
                git_operation()

        except FileNotFoundError:
            print("\033[31mGit is not installed.\033[0m")
        except Exception as e:
            print(f"\033[31m \033[1mError: {str(e)}\033[0m")
    else:
        print("\033[31m \033[1mPlease Install appropriate Operating system\nOtherwise throw this into the Garbage.!\033[0m \033[33m:)\033[0m")


import subprocess

import subprocess

def git_operation():
    while True:
        print("\n\033[34m \033[1mChoose a Git operation:\033[0m")
        print("1. View Git status")
        print("2. Fetch from origin main")
        print("3. Pull from origin main")
        print("4. Push to origin main")
        print("5. Add changes")
        print("6. Commit changes")
        print("7. Exit")

        choice = input("\nEnter your choice (status/fetch/pull/push/add/commit/exit): ")

        if choice == 'status':
            # Git status
            print("\033[34m \033[1mFetching status...\033[0m")
            status_result = subprocess.run(['git', 'status'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if status_result.returncode == 0:
                print(f"\033[32m \033[1mStatus:\n{status_result.stdout}\033[0m")
            else:
                print(f"\033[31m \033[1mStatus check failed: {status_result.stderr}\033[0m")

        elif choice == 'fetch':
            # Git fetch origin main
            print("\033[34m \033[1mFetching from origin main...\033[0m")
            fetch_result = subprocess.run(['git', 'fetch', 'origin', 'main'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if fetch_result.returncode == 0:
                print(f"\033[32m \033[1mFetch successful: {fetch_result.stdout}\033[0m")
            else:
                print(f"\033[31m \033[1mFetch failed: {fetch_result.stderr}\033[0m")

        elif choice == 'pull':
            # Git pull origin main
            print("\033[34m \033[1mPulling from origin main...\033[0m")
            pull_result = subprocess.run(['git', 'pull', 'origin', 'main'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if pull_result.returncode == 0:
                print(f"\033[32m \033[1mPull successful: {pull_result.stdout}\033[0m")
            else:
                print(f"\033[31m \033[1mPull failed: {pull_result.stderr}\033[0m")

        elif choice == 'push':
            # Git push origin main
            print("\033[34m \033[1mPushing to origin main...\033[0m")
            push_result = subprocess.run(['git', 'push', 'origin', 'main'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if push_result.returncode == 0:
                print(f"\033[32m \033[1mPush successful: {push_result.stdout}\033[0m")
            else:
                print(f"\033[31m \033[1mPush failed: {push_result.stderr}\033[0m")

        elif choice == 'add':
            # Git add .
            print("\033[34m \033[1mAdding changes...\033[0m")
            add_result = subprocess.run(['git', 'add', '.'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if add_result.returncode == 0:
                print(f"\033[32m \033[1mAdd successful: {add_result.stdout}\033[0m")
            else:
                print(f"\033[31m \033[1mAdd failed: {add_result.stderr}\033[0m")

        elif choice == 'commit':
            # Git commit -m "<Message>"
            commit_message = input("\033[34m \033[1mEnter commit message: \033[0m")
            if commit_message.strip() == "":
                print("\033[31m \033[1mCommit message cannot be empty.\033[0m")
                continue
            print("\033[34m \033[1mCommitting changes...\033[0m")
            commit_result = subprocess.run(['git', 'commit', '-m', commit_message], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if commit_result.returncode == 0:
                print(f"\033[32m \033[1mCommit successful: {commit_result.stdout}\033[0m")
            else:
                print(f"\033[31m \033[1mCommit failed: {commit_result.stderr}\033[0m")

        elif choice == 'exit':
            # Exit the loop
            print("\033[33mExiting...\033[0m")
            break

        else:
            print("\033[31mInvalid choice! Please enter 'status', 'fetch', 'pull', 'push', 'add', 'commit', or 'exit'.\033[0m")


# Main execution flow
if __name__ == "__main__":
    selected_folder = select_folder()
    if selected_folder:
        check_git_installation(selected_folder)
    else:
        print("\033[31mNo folder selected. Exiting...\033[0m")
