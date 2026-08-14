#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "$0")/../.." && pwd)"
wrapper="$root/deploy/scripts/github-release.sh"
bootstrap="$root/deploy/scripts/bootstrap-github-deploy-user.sh"

[[ -x "$wrapper" ]]
[[ -x "$bootstrap" ]]
grep -q 'tar -xzf' "$wrapper"
grep -q 'rollback.sh' "$wrapper"
grep -q 'nanzi-github-release' "$bootstrap"
grep -q 'nanzi-deploy ALL=(root) NOPASSWD:' "$bootstrap"
if grep -q 'nanzi-ai' "$wrapper" "$bootstrap"; then
  echo "GitHub deployment scripts must not manage the legacy AI service" >&2
  exit 1
fi
