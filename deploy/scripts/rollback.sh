#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run as root." >&2
  exit 2
fi
target="${1:-}"
if [[ -z "$target" ]]; then
  current="$(readlink -f /opt/nanzi-travel/current)"
  target="$(find /opt/nanzi-travel/releases -mindepth 1 -maxdepth 1 -type d ! -path "$current" -print | sort | tail -n 1)"
fi
if [[ -z "$target" || ! -x "$target/backend/.venv/bin/python" ]]; then
  echo "No valid rollback release found." >&2
  exit 3
fi

ln -sfn "$target" /opt/nanzi-travel/current
chown -h nanziapp:nanziapp /opt/nanzi-travel/current
sudo -u nanziapp env DJANGO_DB_PATH=/var/lib/nanzi-travel/db.sqlite3 \
  "$target/backend/.venv/bin/python" "$target/backend/manage.py" migrate --noinput
systemctl restart nanzi-travel-api.service
curl --fail --silent --show-error --retry 10 --retry-delay 2 http://127.0.0.1:8001/healthz >/dev/null
echo "Rolled back to $target"

