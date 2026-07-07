#!/bin/sh
set -eu

# Installs codealmanac@latest via uv, installing uv first if missing.

if ! command -v uv >/dev/null 2>&1; then
  echo "uv not found, installing it first..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi

uv tool install codealmanac@latest

echo ""
echo "codealmanac installed."
echo "next: codealmanac setup"
