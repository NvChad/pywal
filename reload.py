#!/usr/bin/env python3

"""
This file should run every time the 'wal' command is called.
The user could add it to their command like this:
wal -i /path/to/image.png -o /path/to/reload.py
"""

import os
import shutil
import psutil
import pynvim

home_dir = os.path.expanduser("~")

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
            nvim.command('lua require("nvchad.utils").reload("themes.wal")')
            nvim.close()
            print(f"Neovim instance at {socket} reloaded successfully.")
        except Exception as e:
            print(f"Error connecting to Neovim at {socket}: {e}")

copy_file("./base46-pywal.lua", f"{home_dir}/.config/wal/templates/base46-pywal.lua")

copy_file(f"{home_dir}/.cache/wal/base46-pywal.lua", f"{home_dir}/.config/nvim/lua/themes/wal.lua")
reload_nvim()
