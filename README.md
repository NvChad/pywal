<h1 align="center">Base46: Pywal Edition</h1>

> [!NOTE]
> Support for Pywal requires these Python libraries to be installed:
> - `pywal`
> - `psutil`
> - `pynvim`
> - `inotify`

## Installation
```bash
git clone https://github.com/NvChad/pywal
mv pywal ~/.config/nvim/pywal
cd ~/.config/nvim
```
Add this line at the end of your `init.lua` file:
```lua
local nvim_config_path = vim.fn.stdpath('config')
local python_script = nvim_config_path .. "/pywal/reload.py"
os.execute("python3 " .. python_script .. " &> /dev/null &")
```

## Demo
https://github.com/user-attachments/assets/66e73083-6f83-472f-8cb0-7456f0a37069
