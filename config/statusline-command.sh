#!/usr/bin/env bash
input=$(cat)

model=$(echo "$input" | jq -r '.model.display_name // "Unknown"')
used_pct=$(echo "$input" | jq -r '.context_window.used_percentage // empty')
remaining_pct=$(echo "$input" | jq -r '.context_window.remaining_percentage // empty')
ctx_size=$(echo "$input" | jq -r '.context_window.context_window_size // empty')

# Format context window size (e.g. 200000 -> 200k)
if [ -n "$ctx_size" ]; then
  ctx_display=$(awk "BEGIN { printf \"%dk\", $ctx_size / 1000 }")
else
  ctx_display="?"
fi

# Build context usage segment
if [ -n "$used_pct" ] && [ -n "$remaining_pct" ]; then
  printf "\033[0;36m%s\033[0m  ctx: \033[0;33m%.0f%%\033[0m used / \033[0;32m%.0f%%\033[0m left  [%s]" \
    "$model" "$used_pct" "$remaining_pct" "$ctx_display"
else
  printf "\033[0;36m%s\033[0m  ctx: \033[2mno data\033[0m  [%s]" "$model" "$ctx_display"
fi
