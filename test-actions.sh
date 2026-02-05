#!/bin/bash
echo &quot;Test 1: Screenshot&quot;
./screenshot.sh

echo &quot;Test 2: Activate window&quot;
xdotool search --name &quot;RuneLite&quot; windowactivate --sync

echo &quot;Test 3: Jitter click minimap center (assume 1920x1080, minimap ~1800,200)&quot;
./jitter-click.sh 1800 200

echo &quot;Test 4: Type chat&quot;
xdotool key c
sleep 0.5
xdotool type &quot;test from agent&quot;
xdotool key Return

echo &quot;Tests done. Check /tmp/osrs.png&quot;
