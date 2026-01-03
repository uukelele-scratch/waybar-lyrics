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

Recommended to use [waybar-cava](https://github.com/ray-pH/waybar-cava) as well for a music visualizer.

## How it works

The Python script retrieves the currently playing song information via MPRIS using DBus.

MPRIS would be controlled by an active running media player, for example Spotify, or your browser.

Sometimes, if your browser doesn't send MPRIS properly, you can use an add-on such as the [Plasma Integration](https://community.kde.org/Plasma/Browser_Integration) (for KDE Plasma) to connect your browser to the system.

The script retrieves the currently playing song details, as well as the song's currently playing position - e.g. 01:06. From here, the script uses [syncedlyrics](https://github.com/moehmeni/syncedlyrics/) to retrieve the currently playing song's lyrics, in the LRC format (synced to each line). After this, the player uses the currently playing position of the song and the synced lyric data to print the currently playing lyric to stdout. Waybar picks this up, and updates the text shown with the latest lyric.
