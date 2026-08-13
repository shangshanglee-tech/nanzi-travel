#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

for script in "$root_dir"/deploy/scripts/*.sh; do
  bash -n "$script"
done

if CONFIRM_SERVER_BOOTSTRAP=0 bash "$root_dir/deploy/scripts/bootstrap-server.sh" >/dev/null 2>&1; then
  echo "bootstrap must refuse to run without explicit confirmation" >&2
  exit 1
fi

ROOT_DIR="$root_dir" python3 - <<'PY'
import configparser
import os
import pathlib
import re

root = pathlib.Path(os.environ["ROOT_DIR"])
unit = configparser.ConfigParser(strict=False)
unit.optionxform = str
unit.read(root / "deploy/systemd/nanzi-travel-api.service")
assert unit["Service"]["User"] == "nanziapp"
assert "--bind 127.0.0.1:8001" in unit["Service"]["ExecStart"]
assert unit["Service"]["EnvironmentFile"] == "/etc/nanzi-travel/backend.env"

nginx = (root / "deploy/nginx/nanzi-travel.conf").read_text()
assert re.search(r"server_name\s+api\.nanzitravel\.com;", nginx)
assert re.search(r"server_name\s+admin\.nanzitravel\.com;", nginx)
assert "proxy_pass http://127.0.0.1:8001;" in nginx
assert "ssl_certificate" in nginx

secret_assignment = re.compile(r"(?im)^\s*(?:DJANGO_SECRET_KEY|OSS_SECRET_ACCESS_KEY|PASSWORD)\s*=\s*[^\s#].+$")
for path in (root / "deploy").rglob("*"):
    if path.is_file():
        assert not secret_assignment.search(path.read_text(errors="ignore")), f"secret-like value in {path}"
PY
