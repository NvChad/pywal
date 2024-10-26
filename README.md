<h1 align="center">Base46: Pywal Edition</h1>

<p align="center"><i>Pywal and Matugen support for NvChad!</i></p>

> [!NOTE]
> Support for Pywal requires these Python libraries to be installed:
> - `pywal`
> - `watchdog`

## Installation
```bash
cd ~/.config/nvim
git clone https://github.com/NvChad/pywal
```
Add this at the end of your `init.lua` file:
```lua
os.execute("python ~/.config/nvim/pywal/chadwal.py &> /dev/null &")

local autocmd = vim.api.nvim_create_autocmd

autocmd("Signal", {
  pattern = "SIGUSR1",
  callback = function()
    require('nvchad.utils').reload()
  end
})
```
Now you need to generate your Pywal theme again using `wal -i <image>`. If not, `chadwal` will default to `gruvchad` colors.

### Matugen support
Add this line to the `[templates]` section of your `~/.config/matugen/config.toml` file:
```
nvim = { input_path = '~/.config/nvim/pywal/matugen.lua', output_path = '~/.cache/wal/base46-dark.lua' }
```

Select `chadwal` theme and enjoy!
## Demo
https://github.com/user-attachments/assets/933c97f2-4566-406c-8c04-e2e9f0f3f6da
