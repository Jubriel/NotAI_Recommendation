#!/bin/bash
set -e

echo "Starting virtual display..."

rm -f /tmp/.X99-lock
rm -rf /tmp/.X11-unix/X99

Xvfb :99 -screen 0 1280x800x24 -ac &
XVFB_PID=$!

export DISPLAY=:99

# Wait for X server
for i in $(seq 1 50); do
    if xdpyinfo -display :99 >/dev/null 2>&1; then
        break
    fi
    sleep 0.2
done

if ! xdpyinfo -display :99 >/dev/null 2>&1; then
    echo "ERROR: Xvfb failed to start"
    exit 1
fi

echo "Xvfb started successfully"

echo "Starting window manager..."
fluxbox &

echo "Starting VNC server..."
x11vnc -display :99 \
    -forever \
    -shared \
    -nopw \
    -listen 0.0.0.0 \
    -rfbport 5900 &

sleep 2

for i in $(seq 1 30); do
    if (echo > /dev/tcp/127.0.0.1/5900) 2>/dev/null; then
        echo "VNC server started successfully"
        break
    fi
    sleep 1
done

if ! (echo > /dev/tcp/127.0.0.1/5900) 2>/dev/null; then
    echo "ERROR: VNC server failed to start"
    exit 1
fi

echo "Starting noVNC web server..."

websockify \
    --web=/usr/share/novnc \
    0.0.0.0:6080 \
    localhost:5900 &

sleep 2

echo "=================================="
echo "noVNC: http://localhost:6080/vnc.html"
echo "=================================="

echo "Starting Python application..."

exec python -m main