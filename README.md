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
Add this at the end of your `init.lua` file:
```lua
local nvim_config_path = vim.fn.stdpath('config')
local python_script = nvim_config_path .. "/pywal/chadwal.py"
os.execute("python3 " .. python_script .. " &> /dev/null &")
```
Now you need to generate you Pywal theme again using `wal -i <image>`. If not, `chadwal` will default to `gruvchad` colors.

Select `chadwal` theme and enjoy!
## Demo
https://github.com/user-attachments/assets/66e73083-6f83-472f-8cb0-7456f0a37069
