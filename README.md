## What is it?

This repository contains a color scheme template for wal, along with a script to run alongside wal to automatically change the color scheme for Neovim while it is running.

## Usage

1. Clone this repository by running: `git clone https://github.com/NvChad/pywal.git`
2. Change into the pywal directory: `cd pywal`
3. Run `python first_run.py` to copy the theme template into wals pywal template directory
4. Run wal, specifying the -o option with the path to reload.py. For example: `wal -i /path/to/image.png -o ~/pywal/reload.py`
