#!/bin/bash
# Relay IRC message to Moltbook (openclaws submolt)
# Usage: ./relay-moltbook.sh "message text" [title]
set -euo pipefail

CRED_FILE="$HOME/.config/moltbook/credentials.json"
if [[ ! -f "$CRED_FILE" ]]; then
  echo "Error: Moltbook credentials not found at $CRED_FILE" >&2
  exit 1
fi

KEY=$(jq -r .api_key "$CRED_FILE")
if [[ -z "$KEY" || "$KEY" == "null" ]]; then
  echo "Error: No api_key in credentials" >&2
  exit 1
fi

MSG="${1:?Usage: relay-moltbook.sh \"message\" [title]}"
TITLE="${2:-IRC Relay}"

# Use jq to safely construct JSON (prevents injection)
PAYLOAD=$(jq -n \
  --arg submolt "openclaws" \
  --arg title "$TITLE" \
  --arg content "$MSG" \
  '{submolt: $submolt, title: $title, content: $content}')

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "https://moltbook.com/api/v1/posts" \
  -H "X-API-Key: $KEY" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -n -1)

if [[ "$HTTP_CODE" -ge 200 && "$HTTP_CODE" -lt 300 ]]; then
  echo "✓ Relayed to Moltbook (HTTP $HTTP_CODE)"
  echo "$BODY"
else
  echo "✗ Moltbook relay failed (HTTP $HTTP_CODE)" >&2
  echo "$BODY" >&2
  exit 1
fi
