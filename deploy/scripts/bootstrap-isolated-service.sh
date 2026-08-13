#!/usr/bin/env bash
set -euo pipefail

if [[ "${CONFIRM_ISOLATED_BOOTSTRAP:-0}" != "1" ]]; then
  echo "Refusing server changes: set CONFIRM_ISOLATED_BOOTSTRAP=1 after checking DNS and the existing services." >&2
  exit 2
fi
if [[ "${EUID}" -ne 0 ]]; then
  echo "Run as root." >&2
  exit 2
fi
if [[ -z "${CERTBOT_EMAIL:-}" ]]; then
  echo "Set CERTBOT_EMAIL to the certificate contact email." >&2
  exit 2
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
deploy_dir="$(cd "$script_dir/.." && pwd)"

if [[ -e /etc/nginx/sites-enabled/nanzi-travel && ! -L /etc/nginx/sites-enabled/nanzi-travel ]]; then
  echo "Refusing to replace non-symlink /etc/nginx/sites-enabled/nanzi-travel." >&2
  exit 3
fi
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

certbot certonly --webroot --non-interactive --agree-tos --keep-until-expiring \
  --email "$CERTBOT_EMAIL" --cert-name api.nanzitravel.com \
  -w /var/www/html -d api.nanzitravel.com -d admin.nanzitravel.com

install -m 0644 "$deploy_dir/systemd/nanzi-travel-api.service" /etc/systemd/system/nanzi-travel-api.service
install -m 0644 "$deploy_dir/nginx/nanzi-travel.conf" /etc/nginx/sites-available/nanzi-travel
ln -sfn /etc/nginx/sites-available/nanzi-travel /etc/nginx/sites-enabled/nanzi-travel
install -m 0644 "$deploy_dir/logrotate/nanzi-travel" /etc/logrotate.d/nanzi-travel

systemctl daemon-reload
nginx -t
systemctl reload nginx
echo "Isolated bootstrap complete. Existing services were not changed."
