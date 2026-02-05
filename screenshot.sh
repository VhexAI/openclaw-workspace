#!/bin/bash
WIN=$(xdotool search --name &quot;RuneLite&quot; | head -1)
if [ -z &quot;$WIN&quot; ]; then
  echo &quot;No RuneLite window found.&quot; &gt;&amp;2
  exit 1
fi
xdotool windowactivate $WIN
scrot -z /tmp/osrs.png
echo &quot;Screenshot: /tmp/osrs.png&quot;
