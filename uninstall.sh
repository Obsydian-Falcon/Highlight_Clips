#!/usr/bin/env bash
set -e

echo "Stopping and disabling the Highlight Clips service..."
systemctl --user stop hc.service 2>/dev/null || true
systemctl --user disable hc.service 2>/dev/null || true

echo "Removing service and desktop files..."
rm -f ~/.config/systemd/user/hc.service
rm -f ~/.local/share/applications/hc.desktop

systemctl --user daemon-reload

# Ask before deleting cached data, so favorites can be kept
read -p "Remove cached thumbnails and favorites? [y/N] " answer
if [[ "$answer" =~ ^[Yy]$ ]]; then
    rm -rf ~/.cache/hc
    echo "Cache removed."
else
    echo "Cache kept."
fi

echo "Highlight Clips uninstalled. You can now delete the project folder."
