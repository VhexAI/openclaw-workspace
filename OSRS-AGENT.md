# Vhex OSRS Agent - Comprehensive Setup & Plan

## Overview
- **1 Account per Agent**: Spawn subagents for multiple accts.
- **Emergent Play**: No fixed goals. LLM analyzes screenshot (inv/stats/chat/NPC) → plans emergent actions (bury bones, handle drops, bank/cook/tan/chat/quests).
- **Human Variance**: Random jitter, AFK sim, newb chat (&quot;how do i quest?&quot;), helpful/social.
- **Ban-Proof**: Random delays (1-10s), mouse curves (multi-move), variable paths, chat variance.
- **Tools Verified**: tmux/exec/process (sessions), image (vision OCR/detect), browser (acct mgmt), canvas/nodes (optional display), web_search (OSRS wiki).

## Prerequisites
Run `chmod +x setup.sh &amp;&amp; ./setup.sh` (sudo pw needed).

## Architecture
1. **Headless RuneLite**: tmux + xvfb + x11vnc (initial login/monitor).
2. **Screenshot**: `/tmp/osrs.png` via scrot/xdotool.
3. **Analyze**: `image(image=&quot;/tmp/osrs.png&quot;, prompt=...)` → JSON state.
4. **Act**: xdotool via exec (click/key with jitter).
5. **Loop**: Agent loop w/ random sleep.

## Setup Steps
1. `./setup.sh`
2. `./launch-osrs.sh` → tmux osrs, VNC localhost:5900 pass &#39;osrsbot&#39;.
3. VNC in → Login acct, setup:
   - Resizable Modern layout.
   - Plugins: Object/NPC Indicators (optional aids), disable display name title.
   - Window title: &quot;RuneLite&quot;.
   - ESC = Inventory.
4. Detach tmux, agent takes over.

## Agent Loop (Pseudocode)
```
while true:
  exec(&#39;./screenshot.sh&#39;)
  state = image(image=&#39;/tmp/osrs.png&#39;, prompt=STATE_PROMPT)
  action = llm_reasons(state)  # ARS: Analyze-Reason-Select plan/act
  exec(action.cmd)  # xdotool w/ jitter
  sleep(random(2,8))
```
**STATE_PROMPT** (agent-loop-prompt.txt):
```
Screenshot of OSRS RuneLite. Extract JSON:
{
  &quot;inventory&quot;: [{&quot;item&quot;:&quot;bone&quot;,&quot;count&quot;:5, &quot;slot&quot;:[x1,y1,x2,y2]}, ...],
  &quot;stats&quot;: {attack:1, strength:1, ...},
  &quot;chat&quot;: [&quot;Player: hi newb&quot;, ...],
  &quot;npcs&quot;: [{&quot;name&quot;:&quot;Cow&quot;, &quot;loc&quot;:[x,y]}, ...],
  &quot;hp&quot;:80/99, &quot;location&quot;:&quot;Lumbridge&quot;,
  &quot;quests&quot;: [&quot;Cook&#39;s Assistant&quot;]
}
```

**Action Examples** (LLM outputs cmd):
- Bury bones: `xdotool search --name RuneLite windowactivate --sync; xdotool mousemove 1700 900 click 1` (right-click bone) → use bone on ground.
- Bank: Walk to bank, click booth.
- Chat: `xdotool key c; sleep 0.5; xdotool type &quot;hey thx for tip :)&quot;`
- Jitter: Prepend `mousemove_rel -- -5 3; mousemove_rel 2 -1; ...` random path.

## Ban-Proof Features
- **Random**: Delays 1-10s, click offset ±5px, paths 3-5 moves.
- **Variance**: 10% AFK (sleep 60-300s), chat 5% (&quot;gf&quot;, &quot;new here&quot;).
- **Social**: Respond chat, ask quests/help.
- **Newb**: Lumbridge cows/chickens, simple quests.

## MVP Quests
1. Cook&#39;s Assistant: Detect egg/chicken, deliver.
2. X Marks the Spot: Follow map.
3. Sheep Shearer: Shear/bank wool.

## Test Checklist
See test-checklist.md. Run `./test-actions.sh`.

## OpenClaw Tools Verified
- **exec/process/tmux**: launch/screenshot/control.
- **image**: Accurate OCR/detection (test prompt).
- **browser**: OSRS acct create/login wiki.
- **canvas/nodes**: Optional VNC alt.
- **ClawHub**: Optional (search &#39;osrs&#39; skill).

## Files Created
- setup.sh: apt/snap/pip.
- launch-osrs.sh: tmux xvfb vnc runelite.
- screenshot.sh: scrot RuneLite window.
- jitter-click.sh: Human-like click util.
- agent-loop-prompt.txt: Vision/state prompt.
- test-checklist.md / test-actions.sh

## Docker Alt
```
git clone https://github.com/ivan-guerra/containerized_runescape
cd containerized_runescape/osrs-runelite
# Edit cache, docker build -t osrs .
docker run -v $HOME/osrs-cache:/root/.runelite -e DISPLAY=:99 ...
```
VNC 5901.

## Usage
1. Setup/launch/login.
2. Agent: Use tools per loop.
Post-setup: 100% ready (test verifies)."
