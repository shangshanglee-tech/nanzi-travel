#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run as root." >&2
  exit 2
fi
source_dir="${1:?Usage: deploy.sh /path/to/repository}"
timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
release_dir="/opt/nanzi-travel/releases/$timestamp"

install -d -o nanziapp -g nanziapp -m 0750 "$release_dir/backend"
rsync -a --delete \
  --exclude .venv --exclude db.sqlite3 --exclude media --exclude __pycache__ \
  "$source_dir/backend/" "$release_dir/backend/"
chown -R nanziapp:nanziapp "$release_dir"

sudo -u nanziapp python3 -m venv "$release_dir/backend/.venv"
sudo -u nanziapp "$release_dir/backend/.venv/bin/pip" install --requirement "$release_dir/backend/requirements.lock"
sudo -u nanziapp env DJANGO_DB_PATH=/var/lib/nanzi-travel/db.sqlite3 \
  "$release_dir/backend/.venv/bin/python" "$release_dir/backend/manage.py" migrate --noinput
sudo -u nanziapp env DJANGO_DB_PATH=/var/lib/nanzi-travel/db.sqlite3 \
  "$release_dir/backend/.venv/bin/python" "$release_dir/backend/manage.py" collectstatic --noinput

ln -sfn "$release_dir" /opt/nanzi-travel/current
chown -h nanziapp:nanziapp /opt/nanzi-travel/current
systemctl enable --now nanzi-travel-api.service
systemctl restart nanzi-travel-api.service
curl --fail --silent --show-error --retry 10 --retry-delay 2 http://127.0.0.1:8001/healthz >/dev/null
echo "Deployed release $timestamp"

