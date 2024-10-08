#!/usr/bin/env python3

import os
import subprocess
import shutil
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

home_dir = os.path.expanduser("~")
template_src_dark = "./dark.lua"
template_src_light = "./light.lua"
template_dst_dark = f"{home_dir}/.config/wal/templates/base46-dark.lua"
template_dst_light = f"{home_dir}/.config/wal/templates/base46-light.lua"
cache_src_dark = f"{home_dir}/.cache/wal/base46-dark.lua"
cache_src_light = f"{home_dir}/.cache/wal/base46-light.lua"
cache_dst = f"{home_dir}/.local/share/nvim/lazy/base46/lua/base46/themes/chadwal.lua"
fallback_theme = f"{home_dir}/.local/share/nvim/lazy/base46/lua/base46/themes/gruvchad.lua"
lock_file = "/tmp/wal_nvim_lock"
colors_file = f"{home_dir}/.cache/wal/colors"

def is_dark(hex_color):
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    return brightness < 128

def get_hex_from_colors_file():
    try:
        with open(colors_file, 'r') as file:
            first_line = file.readline().strip()
            return first_line
    except FileNotFoundError:
        print(f"Colors file not found: {colors_file}")
        return None

def acquire_lock():
    if os.path.exists(lock_file):
        print("Another instance is already running. Exiting...")
        sys.exit(0)
    else:
        open(lock_file, 'w').close()

def release_lock():
    if os.path.exists(lock_file):
        os.remove(lock_file)

def copy_file_if_not_exists(src, dst):
    try:
        if not os.path.exists(dst):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy(src, dst)
            print(f"File successfully copied from {src} to {dst}.")
        else:
            print(f"File already exists at {dst}, skipping copy.")
    except FileNotFoundError:
        print(f"File not found: {src}")
    except PermissionError:
        print(f"Permission denied to copy from {src} to {dst}")
    except Exception as e:
        print(f"An error occurred while copying from {src} to {dst}: {e}")

def copy_file(src, dst):
    try:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy(src, dst)
        print(f"File successfully copied from {src} to {dst}.")
    except FileNotFoundError:
        print(f"File not found: {src}")
    except PermissionError:
        print(f"Permission denied to copy from {src} to {dst}")
    except Exception as e:
        print(f"An error occurred while copying from {src} to {dst}: {e}")

def on_file_modified():
    if is_dark(get_hex_from_colors_file()):
        template_src = template_src_dark
        template_dst = template_dst_dark
        cache_src = cache_src_dark
    else:
        template_src = template_src_light
        template_dst = template_dst_light
        cache_src = cache_src_light

    copy_file_if_not_exists(fallback_theme, cache_src)
    copy_file(template_src, template_dst)
    copy_file(cache_src, cache_dst)
    
    subprocess.run(['killall', '-SIGUSR1', 'nvim'])

class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path == cache_src_dark:
            on_file_modified()

def monitor_file(file_path):
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
        monitor_file(cache_src_dark)
    finally:
        release_lock()
