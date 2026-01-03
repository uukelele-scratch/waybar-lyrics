#!/usr/bin/env python3
from functools import lru_cache
import os
import sys
import time
import dbus
import threading
import re
import syncedlyrics

DEFAULTS = {
    "title": "No Music",
    "artist": "",
    "duration": 0
}

current_lyrics_data = None  # [(time, text), ...]
is_fetching = False
cached_track_id = None
last_written_text = None

def get_player_props():
    try:
        bus = dbus.SessionBus()
        player = bus.get_object('org.mpris.MediaPlayer2.playerctld', '/org/mpris/MediaPlayer2')
        props = dbus.Interface(player, 'org.freedesktop.DBus.Properties')
        return props
    except Exception:
        return None

def to_python(obj):
    if isinstance(obj, dbus.Array):
        return [to_python(x) for x in obj]
    if isinstance(obj, dbus.Dictionary):
        return {to_python(k): to_python(v) for k, v in obj.items()}
    if isinstance(obj, (dbus.String, dbus.ObjectPath)):
        return str(obj)
    if isinstance(obj, (dbus.Int64, dbus.Int32, dbus.Double)):
        return float(obj)
    if isinstance(obj, (dbus.Boolean,)):
        return bool(obj)
    return obj

def get_metadata_raw(props):
    if not props: return {}
    try:
        md = props.Get('org.mpris.MediaPlayer2.Player', 'Metadata')
        return to_python(md)
    except Exception:
        return {}

def get_position(props):
    if not props: return 0
    try:
        pos = props.Get('org.mpris.MediaPlayer2.Player', 'Position')
        # convert microseconds to seconds
        return pos / 1_000_000
    except Exception:
        return 0

def get_title(md):
    title = md.get('xesam:title') or DEFAULTS["title"]
    return str(title)

def get_artist(md):
    artists = md.get('xesam:artist') or []
    if isinstance(artists, list):
        artist = ", ".join([str(a) for a in artists if a])
    else:
        artist = str(artists)
    return artist.strip() or DEFAULTS["artist"]

def parse_lrc(lrc_content):
    if not lrc_content:
        return None
    
    lines = []
    regex = re.compile(r'\[(\d+):(\d+(?:\.\d+)?)\](.*)')
    
    for line in lrc_content.split('\n'):
        match = regex.match(line)
        if match:
            minutes = int(match.group(1))
            seconds = float(match.group(2))
            text = match.group(3).strip()
            total_seconds = minutes * 60 + seconds
            lines.append((total_seconds, text))
            
    lines.sort(key=lambda x: x[0])
    return lines

@lru_cache
def search(query: str):
    return syncedlyrics.search(query, synced_only=True)

def fetch_lyrics_thread(query_term):
    global current_lyrics_data, is_fetching
    is_fetching = True
    try:
        lrc_content = search(query_term)
        if lrc_content:
            current_lyrics_data = parse_lrc(lrc_content)
        else:
            current_lyrics_data = None
    except Exception as e:
        current_lyrics_data = None
    finally:
        is_fetching = False

def write(text):
    global last_written_text
    if text != last_written_text:
        try:
            print(text, flush=True)
            last_written_text = text
        except Exception:
            pass

def main():
    global cached_track_id, current_lyrics_data, is_fetching
    
    write("")

    while True:
        try:
            props = get_player_props()
            
            if not props:
                write("")
                time.sleep(2)
                continue

            md = get_metadata_raw(props)
            title = get_title(md)
            artist = get_artist(md)
            current_track_id = f"{title} - {artist}"

            if current_track_id != cached_track_id:
                cached_track_id = current_track_id
                current_lyrics_data = None
                
                if title != DEFAULTS["title"]:
                    if not is_fetching:
                        t = threading.Thread(target=fetch_lyrics_thread, args=(current_track_id,))
                        t.start()
            
            output_text = ""

            if current_lyrics_data:
                position = get_position(props)
                
                current_line = ""
                for timestamp, text in current_lyrics_data:
                    if position >= timestamp:
                        current_line = text
                    else:
                        break
                
                output_text = current_line
            else:
                if is_fetching:
                    output_text = f"Downloading... {title}"
                elif title != DEFAULTS["title"]:
                    output_text = f"{title} | {artist}"
                else:
                    output_text = ""

            # 4. Write result
            write(output_text)
            
            time.sleep(0.2)

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
