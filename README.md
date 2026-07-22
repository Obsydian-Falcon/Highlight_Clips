<h1 align="center">Highlight Clips - A local GUI to view videos clipped by GPU Screen Recorder</h1>

<p align="center">
  <img alt="Highlight Clips - A local GUI to view videos clipped by GPU Screen Recorder" src="https://github.com/Obsydian-Falcon/Personal_Projects/blob/main/hc/image.png">
</p>

## About

Highlight Clips is a small locally-hosted web application that showcases the video clips made by GPU Screen Recorder. 

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
2. Change directory to "Highlight Clips"
3. Change permissions on the installation script
4. Install with the script.

```bash
git clone https://github.com/Obsydian-Falcon/Highlight_Clips.git
cd Highlight_Clips
chmod +x install.sh
./install.sh
```

## Configuration

1. Create a `.env` file in the root of the project directory.
2. Set the following variables.
  * HC_VIDEO_DIR, the directory in which GPU Screen Recorder videos are stored.
  * HC_PORT, the port you wish the service to run on.

```
HC_VIDEO_DIR=<video_directory>
HC_PORT=<port>
```

## Uninstall

1. Stop the systemd service
2. Disable the systemd service
3. Remove the installed service and desktop files
4. Tell systemd that the service has been removed
5. (Optional) remove cached thumbnails and favorites

```bash
systemctl --user stop hc
systemctl --user disable hc

rm ~/.config/systemd/user/hc.service
rm ~/.local/share/applications/hc.desktop

systemctl --user daemon-reload

rm -rf ~/.cache/hc
```
