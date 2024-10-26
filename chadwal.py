#!/usr/bin/env python3

import os
import shutil
import sys
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Constants
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
HOME_DIR = os.path.expanduser("~")
TEMPLATE_SRC = {
    "dark": os.path.join(SCRIPT_DIR, "dark.lua"),
    "light": os.path.join(SCRIPT_DIR, "light.lua")
}
TEMPLATE_DST = {
    "dark": f"{HOME_DIR}/.config/wal/templates/base46-dark.lua",
    "light": f"{HOME_DIR}/.config/wal/templates/base46-light.lua"
}
CACHE_SRC = {
    "dark": f"{HOME_DIR}/.cache/wal/base46-dark.lua",
    "light": f"{HOME_DIR}/.cache/wal/base46-light.lua"
}
CACHE_DST = f"{HOME_DIR}/.local/share/nvim/lazy/base46/lua/base46/themes/chadwal.lua"
FALLBACK_THEME = f"{HOME_DIR}/.local/share/nvim/lazy/base46/lua/base46/themes/gruvchad.lua"
LOCK_FILE = "/tmp/wal_nvim_lock"
COLORS_FILE = f"{HOME_DIR}/.cache/wal/colors"

# Utility functions
def is_dark(hex_color):
    """Determine if the color is dark based on luminance."""
    hex_color = hex_color.lstrip('#')
    r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    return brightness < 128

def get_hex_from_colors_file():
    """Read the first color from the colors file."""
    try:
        with open(COLORS_FILE, 'r') as file:
            return file.readline().strip()
    except FileNotFoundError:
        sys.exit(f"Error: Colors file not found: {COLORS_FILE}")

def acquire_lock():
    """Create a lock file to prevent multiple instances."""
    if os.path.exists(LOCK_FILE):
        sys.exit("Another instance is already running. Exiting...")
    open(LOCK_FILE, 'w').close()

def release_lock():
    """Remove the lock file."""
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)

def copy_file(src, dst, skip_if_exists=False):
    """Copy a file from src to dst, optionally skipping if dst exists."""
    if skip_if_exists and os.path.exists(dst):
        print(f"File already exists at {dst}, skipping copy.")
        return

    try:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy(src, dst)
        print(f"File copied from {src} to {dst}.")
    except Exception as e:
        sys.exit(f"Error copying file from {src} to {dst}: {e}")

def on_file_modified():
    """Handle file modifications based on current color scheme."""
    is_dark_theme = is_dark(get_hex_from_colors_file())
    mode = "dark" if is_dark_theme else "light"
    
    copy_file(FALLBACK_THEME, CACHE_SRC[mode], skip_if_exists=True)
    copy_file(TEMPLATE_SRC[mode], TEMPLATE_DST[mode])
    copy_file(CACHE_SRC[mode], CACHE_DST)
    
    subprocess.run(['killall', '-SIGUSR1', 'nvim'])

# Watchdog event handler
class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path == CACHE_SRC["dark"]:
            on_file_modified()

def monitor_file(file_path):
    """Monitor the specified file for changes."""
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, os.path.dirname(file_path), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    on_file_modified()
    acquire_lock()
    try:
        on_file_modified()
        monitor_file(CACHE_SRC["dark"])
    finally:
        release_lock()
