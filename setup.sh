#!/bin/bash
set -e

echo &quot;Installing OSRS Agent prereqs...&quot;

sudo apt update &amp;&amp; sudo apt install -y \
  openjdk-17-jdk \
  tmux \
  xvfb \
  scrot \
  xdotool \
  wmctrl \
  x11-utils \
  tesseract-ocr \
  imagemagick \
  x11vnc \
  python3-pip

sudo snap install runelite --classic

pip3 install --user opencv-python pytesseract pillow numpy

mkdir -p ~/osrs-bot/{templates,screenshots} /tmp/osrs-bot
ln -s ~/osrs-bot /home/vhex/.openclaw/workspace/osrs-bot

echo &quot;Setup complete. Window title: RuneLite. VNC pass: osrsbot&quot;
echo &quot;Next: ./launch-osrs.sh&quot;
