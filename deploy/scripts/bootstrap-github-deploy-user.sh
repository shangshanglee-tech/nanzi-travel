#!/usr/bin/env bash
set -euo pipefail

if [[ "${CONFIRM_GITHUB_DEPLOY_USER:-0}" != "1" ]]; then
  echo "Refusing server changes: set CONFIRM_GITHUB_DEPLOY_USER=1 after reviewing the release design." >&2
  exit 2
fi
if [[ "${EUID}" -ne 0 ]]; then
  echo "Run as root." >&2
  exit 2
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! id nanzi-deploy >/dev/null 2>&1; then
  useradd --create-home --shell /bin/bash nanzi-deploy
fi

install -d -o nanzi-deploy -g nanzi-deploy -m 0700 /home/nanzi-deploy/.ssh
touch /home/nanzi-deploy/.ssh/authorized_keys
chown nanzi-deploy:nanzi-deploy /home/nanzi-deploy/.ssh/authorized_keys
chmod 0600 /home/nanzi-deploy/.ssh/authorized_keys

install -o root -g root -m 0750 "$script_dir/github-release.sh" /usr/local/sbin/nanzi-github-release
cat >/etc/sudoers.d/nanzi-deploy <<'EOF'
nanzi-deploy ALL=(root) NOPASSWD: /usr/local/sbin/nanzi-github-release /tmp/nanzi-travel-release-*.tar.gz [0-9a-f]*
EOF
chmod 0440 /etc/sudoers.d/nanzi-deploy
visudo -cf /etc/sudoers.d/nanzi-deploy

echo "GitHub deployment account prepared. Add its public key to /home/nanzi-deploy/.ssh/authorized_keys."
