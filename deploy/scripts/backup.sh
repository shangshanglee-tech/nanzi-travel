#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run as root." >&2
  exit 2
fi
timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
backup_dir="/opt/backups/nanzi-travel/$timestamp"
database="/var/lib/nanzi-travel/db.sqlite3"

install -d -m 0700 "$backup_dir"
if [[ -f "$database" ]]; then
  sqlite3 "$database" ".backup '$backup_dir/db.sqlite3'"
fi
tar -czf "$backup_dir/runtime-config.tar.gz" -C / etc/nanzi-travel
[[ -d /var/lib/nanzi-travel/media ]] && tar -czf "$backup_dir/media.tar.gz" -C /var/lib/nanzi-travel media
for archive in "$backup_dir"/*.tar.gz; do tar -tf "$archive" >/dev/null; done
find /opt/backups/nanzi-travel -mindepth 1 -maxdepth 1 -type d -mtime +14 -exec rm -rf -- {} +
echo "Backup verified at $backup_dir"

