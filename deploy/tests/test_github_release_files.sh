#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "$0")/../.." && pwd)"
wrapper="$root/deploy/scripts/github-release.sh"
bootstrap="$root/deploy/scripts/bootstrap-github-deploy-user.sh"

[[ -x "$wrapper" ]]
[[ -x "$bootstrap" ]]
grep -q 'tar -xzf' "$wrapper"
grep -q 'rollback.sh' "$wrapper"
grep -q '/usr/local/lib/nanzi-travel' "$wrapper"
grep -q 'nanzi-github-release' "$bootstrap"
grep -q '/usr/local/lib/nanzi-travel' "$bootstrap"
grep -q 'nanzi-deploy ALL=(root) NOPASSWD:' "$bootstrap"
if grep -q 'nanzi-ai' "$wrapper" "$bootstrap"; then
  echo "GitHub deployment scripts must not manage the legacy AI service" >&2
  exit 1
fi

workflow="$root/.github/workflows/release.yml"
tests_workflow="$root/.github/workflows/tests.yml"
grep -q '^name: Release' "$workflow"
grep -q 'concurrency:' "$workflow"
grep -q 'DEPLOY_SSH_PRIVATE_KEY' "$workflow"
grep -q 'healthz' "$workflow"
grep -q 'WECHAT_PRIVATE_KEY' "$workflow"
grep -q 'upload-wechat-experience.cjs' "$workflow"
grep -A4 '^  upload-wechat-experience:' "$workflow" | grep -q 'timeout-minutes: 5'
grep -q '^name: Tests' "$tests_workflow"
