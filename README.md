# waybar-lyrics
Put lyrics in time with your music in the waybar.


## Usage

```
$ # Create the directory .config/waybar/scripts if it doesn't already exist.
$ curl https://raw.githubusercontent.com/uukelele-scratch/waybar-lyrics/refs/heads/main/lyrics.py -o ~/.config/waybar/scripts/lyrics.py
```

Add this to `config.jsonc`:

```jsonc
  "custom/lyrics": {
    "exec": "python ~/.config/waybar/scripts/lyrics.py",
    "format": "   {} ",
    "escape": true,
    "restart-interval": 10
  }
```
