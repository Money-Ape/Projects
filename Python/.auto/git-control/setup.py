from cx_Freeze import setup, Executable

# Define build options
build_exe_options = {
    "packages": ["tkinter"],  # Include any additional packages here
    "excludes": [],
    "include_files": []  # Include any additional files here
}

# Define the executable
executables = [
    Executable(
        script="your_gui_script.py",  # Replace with your script name
        base="Win32GUI",
        target_name="your_program.exe"  # Replace with the desired .exe name
    )
]

# Setup build
setup(
    name="YourProgramName",
    version="0.1",
    description="Description of your program",
    options={"build_exe": build_exe_options},
    executables=executables
)
