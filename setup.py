import sys
from cx_Freeze import setup, Executable

# General build options for both platforms
build_exe_options = {
    "packages": ["os"],  # Include necessary packages
    "include_files": [],  # Add additional files (if any)
}

# Executables configuration
executables = [
    Executable(
        "Gliph.py",                 # Path to your main Python script
        target_name="Gliph.exe" if sys.platform == "win32" else "Gliph",  # Name of the output executable
        icon="app.ico" if sys.platform == "win32" else "app.icns"             # Optional: platform-specific icon
    )
]

# Setup function
setup(
    name="Gliph",
    version="1.0",
    description="Mask sensitive data before feeding to Ai!",
    options={"build_exe": build_exe_options},
    executables=executables
)
