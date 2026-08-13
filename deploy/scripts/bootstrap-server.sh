#!/usr/bin/env bash
set -euo pipefail

if [[ "${CONFIRM_SERVER_BOOTSTRAP:-0}" != "1" ]]; then
  echo "Refusing server changes: set CONFIRM_SERVER_BOOTSTRAP=1 after reviewing the backup and DNS." >&2
  exit 2
fi
if [[ "${EUID}" -ne 0 ]]; then
  echo "Run as root." >&2
  exit 2
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
deploy_dir="$(cd "$script_dir/.." && pwd)"
timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
legacy_backup="/opt/backups/nanzi-ai/$timestamp"

install -d -m 0700 "$legacy_backup"
if [[ -d /opt/nanzi-ai ]]; then
  tar -C /opt -czf "$legacy_backup/nanzi-ai.tar.gz" nanzi-ai
fi
[[ -f /etc/systemd/system/nanzi-ai.service ]] && cp -a /etc/systemd/system/nanzi-ai.service "$legacy_backup/"
[[ -f /etc/nginx/sites-available/nanzi-ai ]] && cp -a /etc/nginx/sites-available/nanzi-ai "$legacy_backup/"
systemctl cat nanzi-ai.service >"$legacy_backup/systemd-unit.txt" 2>/dev/null || true
ss -lntup >"$legacy_backup/listeners.txt"
tar -tf "$legacy_backup/nanzi-ai.tar.gz" >/dev/null 2>&1 || [[ ! -f "$legacy_backup/nanzi-ai.tar.gz" ]]

if ! id nanziapp >/dev/null 2>&1; then
  useradd --system --home /opt/nanzi-travel --shell /usr/sbin/nologin nanziapp
fi
install -d -o nanziapp -g nanziapp -m 0750 /opt/nanzi-travel/releases /var/log/nanzi-travel
install -d -o nanziapp -g www-data -m 2750 /var/lib/nanzi-travel
install -d -o nanziapp -g www-data -m 2750 /var/lib/nanzi-travel/media /var/lib/nanzi-travel/static
install -d -o root -g nanziapp -m 0750 /etc/nanzi-travel

if [[ ! -f /etc/nanzi-travel/backend.env ]]; then
  echo "Create /etc/nanzi-travel/backend.env from backend/.env.example before continuing." >&2
  exit 3
fi
chmod 0640 /etc/nanzi-travel/backend.env

certbot certonly --nginx --non-interactive --agree-tos --expand \
  --cert-name api.nanzitravel.com \
  -d api.nanzitravel.com -d admin.nanzitravel.com

install -m 0644 "$deploy_dir/systemd/nanzi-travel-api.service" /etc/systemd/system/nanzi-travel-api.service
install -m 0644 "$deploy_dir/nginx/nanzi-travel.conf" /etc/nginx/sites-available/nanzi-travel
ln -sfn /etc/nginx/sites-available/nanzi-travel /etc/nginx/sites-enabled/nanzi-travel
rm -f /etc/nginx/sites-enabled/nanzi-ai
install -m 0644 "$deploy_dir/logrotate/nanzi-travel" /etc/logrotate.d/nanzi-travel

systemctl disable --now nanzi-ai.service 2>/dev/null || true
if command -v ufw >/dev/null 2>&1; then
  ufw deny 5000/tcp
else
  iptables -C INPUT -p tcp --dport 5000 -j DROP 2>/dev/null || iptables -I INPUT -p tcp --dport 5000 -j DROP
fi

systemctl daemon-reload
nginx -t
systemctl reload nginx
echo "Bootstrap complete. Also verify Alibaba Cloud security groups do not expose TCP 5000."
