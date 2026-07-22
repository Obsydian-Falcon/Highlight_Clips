from pathlib import Path  # Find paths on the system
from datetime import datetime  # Working with dates and times
from flask import Flask, render_template, send_file, redirect, request  # Webserver
from flask.typing import ResponseReturnValue  # Value for responses from functions
import subprocess  # Allow python to run other programs
import hashlib  # Make unique identifiers for each video path
import json  # Use JSON to store favorites.
import os 
from dotenv import load_dotenv # Get the env file

# Load the environment file
load_dotenv(Path(__file__).parent / ".env") # Make sure that .env is in the root directory

app = Flask(__name__)  # Make the app

# Define where videos from GPU_Screen_Recorder live
# Additionally, note which file extensions are allowed
VIDEO_DIR = Path(os.environ.get("HC_VIDEO_DIR", Path.home() / "Videos"))
VIDEO_EXTENSIONS = {".mp4", ".mkv", ".mov", ".webm", ".flv"}

# DEFINE where thumbnails are stored
THUMBNAIL_DIR = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "hc"
THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)  # Create a thumbnail directory if it doesn't exist yet

# PORT
PORT = int(os.environ.get("HC_PORT", 5000))  # Default to 5000 if unset

# INDEX
CLIP_INDEX: dict[str, Path] = {}  # Maps clip_id to the real path of the video file

# FAVORITES FILE
FAVORITES_FILE = THUMBNAIL_DIR / "favorites.json"  # Save favorites in the cache


# Find the clips and add them to a list of dictionaries
def find_clips() -> list[dict]:
    clips: list[dict] = []  # Empty array to hold clip paths
    favorites = load_favorites()
    for path in VIDEO_DIR.glob("*"):  # Go through each item in the folder
        if path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS:
            clip_id = make_thumbnail(path)  # Make a thumbnail and return its ID
            CLIP_INDEX[clip_id] = path  # Map the clip_id to the video path
            clips.append({  # Each clip is now a dictionary.
                          "name": path.name,
                          "modified": path.stat().st_mtime,  # When the file was last saved
                          "clip_id": clip_id,
                          "is_favorite": clip_id in favorites,
                          })

    clips.sort(key=lambda clip: clip["modified"], reverse=True)  # Newest first
    return clips


# Create a date/time label for a given timestamp
def date_label(timestamp: float) -> str:
    clip_date = datetime.fromtimestamp(timestamp).date()  # Get the date of the clip
    today = datetime.now().date()
    days_ago = (today - clip_date).days  # How many days ago the clip is

    if days_ago == 0:
        return "Today"
    if days_ago == 1:
        return "Yesterday"
    return clip_date.strftime("%A, %d %B %Y")  # Eg. Monday, 14 July 2026


# Make a thumbnail for a given video path if it doesn't exist
def make_thumbnail(video_path: Path) -> str:
    # Turn the full file path into a unique ID
    clip_id = hashlib.md5(str(video_path).encode()).hexdigest()
    thumb_path = THUMBNAIL_DIR / f"{clip_id}.jpg"

    if not thumb_path.exists():  # Generate a thumbnail if one isn't there
        for seek in ["15", "1"]:  # Try 15s in, fall back to 1s for short clips
            subprocess.run([
                "ffmpeg", "-ss", seek, "-i", str(video_path),
                "-frames:v", "1", "-vf", "scale=640:-2", "-y",
                str(thumb_path),
                ], capture_output=True)
            if thumb_path.exists():
                break  # Got a frame, stop trying

    return clip_id


def load_favorites() -> set[str]:
    if FAVORITES_FILE.exists():
        return set(json.loads(FAVORITES_FILE.read_text()))
    return set()


def save_favorites(favorites: set[str]) -> None:
    FAVORITES_FILE.write_text(json.dumps(list(favorites)))


# ======== ROUTES =======
@app.route("/")
def home() -> ResponseReturnValue:
    clips = find_clips()  # Get the clips (they are dictionaries)

    groups: dict[str, list[dict]] = {}
    for clip in clips:
        label = date_label(clip["modified"])  # Make the label for this clip
        if label not in groups:
            groups[label] = []
        groups[label].append(clip)

    # Sort each group so stars rise within their own day.
    for label in groups:
        groups[label].sort(key=lambda clip: clip["is_favorite"], reverse=True)

    return render_template("index.html", groups=groups)


@app.route("/thumbnails/<clip_id>")  # clip_id is a variable in the URL
def thumbnail(clip_id: str) -> ResponseReturnValue:
    thumb_path = THUMBNAIL_DIR / f"{clip_id}.jpg"
    if not thumb_path.exists():  # Make sure it exists before send_file
        return "Thumbnail not found", 404

    return send_file(thumb_path)


@app.route("/video/<clip_id>")
def video(clip_id: str) -> ResponseReturnValue:
    video_path: Path | None = CLIP_INDEX.get(clip_id)
    if video_path is None:  # Make sure the video path exists
        return "Clip not found", 404

    return send_file(video_path)


@app.route("/favorite/<clip_id>", methods=["POST"])
def toggle_favorite(clip_id: str) -> ResponseReturnValue:
    favorites = load_favorites()
    if clip_id in favorites:
        favorites.remove(clip_id)
    else:
        favorites.add(clip_id)

    save_favorites(favorites)
    return redirect("/")


# Add a deletion route
@app.route("/delete/<clip_id>", methods=["POST"])
def video_delete(clip_id: str) -> ResponseReturnValue:
    if not CLIP_INDEX:  # index empty, rebuild it
        find_clips()

    video_path: Path | None = CLIP_INDEX.get(clip_id)  # Get the video's path
    if video_path is None:
        return "Clip not found", 404

    video_path.unlink()  # Delete the video

    thumb_path = THUMBNAIL_DIR / f"{clip_id}.jpg"  # Delete its thumbnail
    thumb_path.unlink(missing_ok=True)

    favorites = load_favorites()  # Delete its favorites entry if present
    if clip_id in favorites:
        favorites.discard(clip_id)
        save_favorites(favorites)

    return redirect("/")


@app.route("/rename/<clip_id>", methods=["POST"])
def rename_clip(clip_id: str) -> ResponseReturnValue:
    if not CLIP_INDEX: # Index empty, rebuild it
        find_clips()

    old_path: Path | None = CLIP_INDEX.get(clip_id) # Get the current path of the clip
    if old_path is None:
        return "Clip not found", 404

    new_name = request.form.get("new_name", "").strip() # Get the new name, strip spaces
    if not new_name:
        return "Name required", 400
    # Make sure renames don't touch files outside the given video folder
    if "/" in new_name or ".." in new_name:
        return "Invalid name", 400

    # Keep the original extension and use the filename given by the user
    new_path = old_path.with_name(new_name).with_suffix(old_path.suffix)

    old_path.rename(new_path) # Rename the file
    new_id = hashlib.md5(str(new_path).encode()).hexdigest()

    # Migrate the thumbnail to the new id
    old_thumb = THUMBNAIL_DIR / f"{clip_id}.jpg"
    new_thumb = THUMBNAIL_DIR / f"{new_id}.jpg"
    if old_thumb.exists():
        old_thumb.rename(new_thumb)

    # Migrate the favorites, if it was a favorite
    favorites = load_favorites()
    if clip_id in favorites:
        favorites.discard(clip_id)
        favorites.add(new_id)
        save_favorites(favorites)

    return redirect("/")



# ===== MAIN ======
if __name__ == "__main__":
    app.run(debug=True, port=5001)  # DEBUG MODE
