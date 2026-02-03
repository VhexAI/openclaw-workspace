#!/bin/bash
# Empire Builder Setup
SCRIPT_DIR=$(dirname &quot;$0&quot;)
EMPIRE_DIR=$(dirname &quot;$SCRIPT_DIR&quot;)

echo &quot;Setting up Empire Builder crons...&quot;

# Add to crontab
(crontab -l 2&gt;/dev/null; echo &quot;0 9 * * * $EMPIRE_DIR/scripts/network-loop.sh&quot;) | crontab -
(crontab -l 2&gt;/dev/null; echo &quot;0 18 * * * $EMPIRE_DIR/scripts/income-loop.sh&quot;) | crontab -

echo &quot;Empire crons installed. Edit crontab for customization.&quot;
echo &quot;Test runs:&quot;
$EMPIRE_DIR/scripts/network-loop.sh
$EMPIRE_DIR/scripts/income-loop.sh
