#!/usr/bin/env bash
set -e # Stop on the first error

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)" # Where the script will live

poetry install # dependencies

mkdir -p ~/.config/systemd/user ~/.local/share/applications

# Generate a service file with realpath baked in
sed "s|__PROJECT_DIR__|$PROJECT_DIR|g" hc.service.template \
    > ~/.config/systemd/user/hc.service

sed "s|__PROJECT_DIR__|$PROJECT_DIR|g" hc.desktop.template \
    > ~/.local/share/applications/hc.desktop

# Make a venv
python3 -m venv "$PROJECT_DIR/venv"
"$PROJECT_DIR/venv/bin/pip" install -r requirements.txt

# Set systemctl
systemctl --user daemon-reload
systemctl --user enable --now hc.service

echo "Highlight Clips installed. Runing at http://localhost:5000"
