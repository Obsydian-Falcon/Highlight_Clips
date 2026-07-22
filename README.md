<h1 align="center">ClipVault - A local GUI to view videos clipped by GPU Screen Recorder</h1>

<p align="center">
  <img alt="ClipVault - A local GUI to view videos clipped by GPU Screen Recorder" src="https://github.com/Obsydian-Falcon/Personal_Projects/blob/main/clipvault/image.png">
</p>

## About

ClipVault is a small locally-hosted web application that shows the user clips made by GPU Screen Recorder. This project was made because I couldn't find a program that displayed my videos that layered on top of GPU Screen Recorder's existing functionality

## Features

- Videos are sorted by date
- Search
- Favorites
- Video rename
- Video deletion
- Click to play
- Runs as a background service (using systemd)

## Requirements
- ffmpeg
- Python 3.13+
- Linux with systemd

## Installation

### Git
1. Clone the repository:
2. Change directory to "clipvault"
3. Change permissions on the installation script
4. Install with the script.

```bash
git clone git@github.com:Obsydian-Falcon/clipvault.git
cd clipvault
chmod +x install.sh
./install.sh
```

## Configuration

1. Create a `.env` file in the root of the project directory.
2. Set the following variables.
  * CLIPVAULT_VIDEO_DIR, the directory in which GPU Screen Recorder videos are stored.
  * CLIPVAULT_PORT, the port you wish the service to run on.

```
CLIPVAULT_VIDEO_DIR=<video_directory>
CLIPVAULT_PORT=<port>
```

## Uninstall

1. Stop the systemd service
2. Disable the systemd service
3. Remove the installed service and desktop files
4. Tell systemd that the service has been removed
5. (Optional) remove cached thumbnails and favorites

```bash
systemctl --user stop clipvault
systemctl --user disable clipvault

rm ~/.config/systemd/user/clipvault.service
rm ~/.local/share/applications/clipvault.desktop

systemctl --user daemon-reload

rm -rf ~/.cache/clipvault
```
