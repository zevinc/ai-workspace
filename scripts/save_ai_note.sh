#!/usr/bin/env bash
set -euo pipefail

CATEGORY="${1:-agents}"
TOPIC="${2:-ai-note}"
CONTENT_FILE="${3:-}"

if [ -z "$CONTENT_FILE" ] || [ ! -f "$CONTENT_FILE" ]; then
  echo "Usage: scripts/save_ai_note.sh <category> <topic> <content_file>"
  exit 1
fi

mkdir -p "docs/ai/${CATEGORY}"

TS=$(date +"%Y-%m-%d-%H%M")
SAFE_TOPIC=$(echo "$TOPIC" | tr '[:upper:]' '[:lower:]' | sed 's/[^2026-05-13_AI_Knowledge_Base_Index.md-z0-9-]/-/g' | sed 's/-\+/-/g')
TARGET="docs/ai/${CATEGORY}/${TS}-${SAFE_TOPIC}.md"

cp "$CONTENT_FILE" "$TARGET"

echo "Saved: $TARGET"
