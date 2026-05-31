#!/usr/bin/env bash
# Installs the Kilo Code VSCode extension on DevPod workspace start.
# Wired via devfile.yaml postStart. Idempotent: short-circuits if already installed.
# If open-vsx.org is unreachable from the cluster, set KILO_VSIX to a Nexus-hosted VSIX.
set -euo pipefail

EXT_ID="kilocode.kilo-code"
VSIX_SRC="${KILO_VSIX:-}"   # optional override: Nexus-hosted/local VSIX (URL or path)

log() { echo "[kilo-install] $*"; }

CLI=""
for candidate in code-server openvscode-server code; do
  if command -v "$candidate" >/dev/null 2>&1; then
    CLI="$candidate"
    break
  fi
done
if [ -z "$CLI" ]; then
  log "ERROR: no VS Code CLI (code-server / openvscode-server / code) on PATH." >&2
  exit 1
fi
log "using editor CLI: $CLI"

if "$CLI" --list-extensions 2>/dev/null | grep -qix "$EXT_ID"; then
  log "$EXT_ID already installed; nothing to do."
  exit 0
fi

if [ -n "$VSIX_SRC" ]; then
  case "$VSIX_SRC" in
    http://*|https://*)
      tmp="$(mktemp --suffix=.vsix)"
      log "downloading VSIX: $VSIX_SRC"
      curl -fsSL "$VSIX_SRC" -o "$tmp"
      VSIX_SRC="$tmp"
      ;;
  esac
  log "installing from VSIX: $VSIX_SRC"
  "$CLI" --install-extension "$VSIX_SRC"
else
  log "installing $EXT_ID from configured gallery (Open VSX)"
  "$CLI" --install-extension "$EXT_ID"
fi

if "$CLI" --list-extensions 2>/dev/null | grep -qix "$EXT_ID"; then
  log "OK — $EXT_ID is installed."
else
  log "ERROR — $EXT_ID not present after install attempt." >&2
  exit 1
fi
