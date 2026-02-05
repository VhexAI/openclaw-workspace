#!/bin/bash
# Usage: ./jitter-click.sh X Y [button=1]
X=$1; Y=$2; BUTTON=${3:-1}

# Human jitter: 3-5 random moves ±10px
for i in {1..4}; do
  DX=$((RANDOM % 21 - 10))
  DY=$((RANDOM % 21 - 10))
  xdotool mousemove_relative -- $DX $DY
  sleep $(echo &quot;scale=2; 0.05 + 0.1 * $RANDOM / 32767&quot; | bc)
done
xdotool mousemove -- $X $Y click $BUTTON
