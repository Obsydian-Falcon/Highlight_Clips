#!/usr/bin/env bash
set -e

echo "Stopping and disabling the ClipVault service..."
systemctl --user stop clipvault.service 2>/dev/null || true
systemctl --user disable clipvault.service 2>/dev/null || true

echo "Removing service and desktop files..."
rm -f ~/.config/systemd/user/clipvault.service
rm -f ~/.local/share/applications/clipvault.desktop

systemctl --user daemon-reload

# Ask before deleting cached data, so favorites can be kept
read -p "Remove cached thumbnails and favorites? [y/N] " answer
if [[ "$answer" =~ ^[Yy]$ ]]; then
    rm -rf ~/.cache/clipvault
    echo "Cache removed."
else
    echo "Cache kept."
fi

echo "ClipVault uninstalled. You can now delete the project folder."
