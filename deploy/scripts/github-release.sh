#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run as root." >&2
  exit 2
fi

archive="${1:-}"
commit="${2:-}"
case "$archive" in
  /tmp/nanzi-travel-release-*.tar.gz) ;;
  *) echo "Invalid release archive path." >&2; exit 3 ;;
esac
[[ -f "$archive" ]] || { echo "Release archive not found." >&2; exit 3; }
[[ "$commit" =~ ^[0-9a-f]{7,40}$ ]] || { echo "Invalid commit identifier." >&2; exit 3; }

release_scripts_dir="/usr/local/lib/nanzi-travel"
source_dir="$(mktemp -d /tmp/nanzi-travel-release-XXXXXX)"
trap 'rm -rf "$source_dir"' EXIT

tar -xzf "$archive" -C "$source_dir"
[[ -f "$source_dir/backend/manage.py" ]] || { echo "Release archive is missing backend/manage.py." >&2; exit 4; }

"$release_scripts_dir/backup.sh"
"$release_scripts_dir/deploy.sh" "$source_dir"

if ! curl --fail --silent --show-error --retry 5 --retry-connrefused --retry-delay 2 http://127.0.0.1:8001/healthz >/dev/null; then
  echo "Health check failed; rolling back." >&2
  "$release_scripts_dir/rollback.sh"
  curl --fail --silent --show-error --retry 5 --retry-connrefused --retry-delay 2 http://127.0.0.1:8001/healthz >/dev/null
  exit 5
fi

echo "GitHub release deployed for commit $commit"
