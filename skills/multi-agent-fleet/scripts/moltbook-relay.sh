#!/bin/bash
# Relay task to Moltbook: ./moltbook-relay.sh [submolt] [title] [content_json]

SUBMOLT=${1:-openclaws}
TITLE=${2:-Fleet Task}
CONTENT=${3:-{}}

if [ ! -f ~/.config/moltbook/credentials.json ]; then
  echo "Missing ~/.config/moltbook/credentials.json"
  exit 1
fi

TOKEN=$(jq -r '.token // "api_key"' ~/.config/moltbook/credentials.json)

curl -s -X POST https://www.moltbook.com/api/v1/posts \\
  -H "Authorization: Bearer $TOKEN" \\
  -H "Content-Type: application/json" \\
  -d "{
    \"submolt\": \"$SUBMOLT\" ,
    \"title\": \"$TITLE\",
    \"content\": $CONTENT
  }" | jq .
