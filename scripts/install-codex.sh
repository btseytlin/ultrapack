#!/bin/sh
# Install ultrapack into Codex by symlinking from this repo into ~/.codex.
# Re-run is safe; symlinks are replaced.
set -e
REPO="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$HOME/.codex/skills" "$HOME/.codex/agents"
ln -sfn "$REPO/plugins/up/skills" "$HOME/.codex/skills/ultrapack"
for f in "$REPO/.codex/agents"/*.toml; do
  ln -sfn "$f" "$HOME/.codex/agents/$(basename "$f")"
done
echo "Installed ultrapack into ~/.codex. Restart Codex to pick up the skills and subagents."
