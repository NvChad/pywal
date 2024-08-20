#!/usr/bin/env python3

import os
import psutil
import shutil
import pynvim
import re
import inotify.adapters
import sys
import time
from colorsys import rgb_to_hsv, hsv_to_rgb

home_dir = os.path.expanduser("~")
template_src = "./base46-pywal.lua"
template_dst = f"{home_dir}/.config/wal/templates/base46-pywal.lua"
cache_src = f"{home_dir}/.cache/wal/base46-pywal.lua"
cache_dst = f"{home_dir}/.local/share/nvim/lazy/base46/lua/base46/themes/chadwal.lua"
fallback_theme = f"{home_dir}/.local/share/nvim/lazy/base46/lua/base46/themes/gruvchad.lua"
lock_file = "/tmp/wal_nvim_lock"

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

def is_dark(hex_color):
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    return brightness < 128

def adjust_color(color_hex, percentage):
    color_hex = color_hex.lstrip('#')
    r, g, b = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
    h, s, v = rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)

    factor = 1 if is_dark(color_hex) else -1
    v = max(0, min(1, v + (percentage * factor / 100.0)))

    if v <= 0.01:
        v = max(0.05, v + abs(percentage) * 0.5 / 100.0)
    elif v >= 0.99:
        v = min(0.95, v - abs(percentage) * 0.5 / 100.0)

    r, g, b = hsv_to_rgb(h, s, v)
    return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"

def generate_colors(base_color, yellow_color):
    colors = {}
    colors['darker_black'] = adjust_color(base_color, -3)
    colors['black2'] = adjust_color(base_color, 6)
    colors['one_bg'] = adjust_color(base_color, 10)
    colors['one_bg2'] = adjust_color(colors['one_bg'], 6)
    colors['one_bg3'] = adjust_color(colors['one_bg2'], 6)
    colors['grey'] = adjust_color(base_color, 40)
    colors['grey_fg'] = adjust_color(colors['grey'], 10)
    colors['grey_fg2'] = adjust_color(colors['grey_fg'], 5)
    colors['line'] = adjust_color(base_color, 15)
    colors['sun'] = adjust_color(yellow_color, 8)
    return colors

def replace_colors_in_file(file_path):
    while True:
        with open(file_path, 'r') as file:
            content = file.read()

        black_match = re.search(r'black\s*=\s*"(#\w+)"', content)
        yellow_match = re.search(r'yellow\s*=\s*"(#\w+)"', content)

        if black_match and yellow_match:
            black_color = black_match.group(1)
            yellow_color = yellow_match.group(1)
            break
        else:
            print("black or yellow not found, retrying in 1 second...")
            time.sleep(1)

    new_colors = generate_colors(black_color, yellow_color)

    for name, color in new_colors.items():
        content = re.sub(rf'{name}\s*=\s*"(#\w+)"', f'{name} = "{color}"', content)

    with open(file_path, 'w') as file:
        file.write(content)

def get_nvim_sockets():
    sockets = []
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == 'nvim':
            try:
                for conn in proc.connections(kind='unix'):
                    if conn.laddr:
                        sockets.append(conn.laddr)
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                continue
    return sockets

def reload_nvim():
    sockets = get_nvim_sockets()
    for socket in sockets:
        try:
            nvim = pynvim.attach('socket', path=socket)
            nvim.command('lua require("nvchad.utils").reload("themes")')
            nvim.close()
            print(f"Neovim instance at {socket} reloaded successfully.")
        except Exception as e:
            print(f"Error connecting to Neovim at {socket}: {e}")

def on_file_modified():
    print(f"File {cache_src} modified. Executing functions...")

    copy_file_if_not_exists(fallback_theme, cache_src)
    copy_file(template_src, template_dst)
    copy_file(cache_src, cache_dst)
    replace_colors_in_file(cache_dst)
    reload_nvim()

def monitor_file(file_path):
    i = inotify.adapters.Inotify()
    i.add_watch(os.path.dirname(file_path))

    while True:
        for event in i.event_gen(yield_nones=False, timeout_s=1):
            (_, type_names, path, filename) = event

            if 'IN_MODIFY' in type_names and filename == os.path.basename(file_path):
                on_file_modified()

        if not get_nvim_sockets():
            print("No more Neovim processes running. Exiting...")
            release_lock()
            sys.exit(0)

        time.sleep(1)

if __name__ == "__main__":
    on_file_modified()
    acquire_lock()
    try:
        monitor_file(cache_src)
    finally:
        release_lock()
