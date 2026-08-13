import os
import subprocess
import sys

from django.conf import settings
from django.test import SimpleTestCase


class SettingsTests(SimpleTestCase):
    def test_public_hosts_and_time_zone_are_explicit(self):
        self.assertEqual(settings.TIME_ZONE, "Asia/Shanghai")
        self.assertIn("api.nanzitravel.com", settings.ALLOWED_HOSTS)
        self.assertIn("admin.nanzitravel.com", settings.ALLOWED_HOSTS)

    def test_sqlite_uses_wal_and_immediate_transactions(self):
        options = settings.DATABASES["default"]["OPTIONS"]

        self.assertIn("PRAGMA journal_mode=WAL", options["init_command"])
        self.assertEqual(options["transaction_mode"], "IMMEDIATE")

    def test_reverse_proxy_https_is_explicit(self):
        self.assertEqual(settings.SECURE_PROXY_SSL_HEADER, ("HTTP_X_FORWARDED_PROTO", "https"))

    def test_admin_origin_and_persistent_media_directory_are_explicit(self):
        self.assertIn("https://admin.nanzitravel.com", settings.CSRF_TRUSTED_ORIGINS)

        environment = {
            **os.environ,
            "DJANGO_MEDIA_ROOT": "/var/lib/nanzi-travel/media",
        }
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    "from config import settings; "
                    "assert str(settings.MEDIA_ROOT) == '/var/lib/nanzi-travel/media'"
                ),
            ],
            cwd=settings.BASE_DIR,
            env=environment,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_production_mode_enables_secure_cookies(self):
        environment = {
            **os.environ,
            "DJANGO_DEBUG": "false",
            "DJANGO_SECRET_KEY": "production-test-key",
        }

        result = subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    "from config import settings; "
                    "assert settings.SESSION_COOKIE_SECURE is True; "
                    "assert settings.CSRF_COOKIE_SECURE is True; "
                    "assert settings.SECURE_SSL_REDIRECT is True; "
                    "assert settings.SECURE_HSTS_SECONDS == 31536000"
                ),
            ],
            cwd=settings.BASE_DIR,
            env=environment,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
