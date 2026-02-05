#!/bin/bash
tmux kill-session -t osrs &gt;/dev/null 2&gt;&amp;1 || true
tmux new-session -d -s osrs &#39;bash&#39;

tmux send-keys -t osrs &quot;export DISPLAY=:99&quot; Enter
tmux send-keys -t osrs &quot;Xvfb :99 -screen 0 1920x1080x24 &amp;&quot; Enter
tmux send-keys -t osrs &quot;sleep 3&quot; Enter
tmux send-keys -t osrs &quot;x11vnc -display :99 -auth guess -forever -loop -noxdamage -repeat -rfbauth vncpass:osrsbot -rfbport 5900 -shared &amp;&quot; Enter
tmux send-keys -t osrs &quot;sleep 2&quot; Enter
tmux send-keys -t osrs &quot;runelite&quot; Enter

echo &quot;OSRS launched. tmux: osrs. VNC: localhost:5900 pass=&#39;osrsbot&#39; (login/setup).&quot;
echo &quot;After login: Ctrl+B D detach tmux.&quot;
