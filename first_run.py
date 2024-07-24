#!/usr/bin/env python3

"""
This file should run the first time NvChad starts to create the template file.
"""

import os
import shutil

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

copy_file("./base46-pywal.lua", f"{home_dir}/.config/wal/templates/base46-pywal.lua")
