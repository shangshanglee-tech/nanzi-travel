from django.conf import settings
from django.test import SimpleTestCase


class SettingsTests(SimpleTestCase):
    def test_public_hosts_and_time_zone_are_explicit(self):
        self.assertEqual(settings.TIME_ZONE, "Asia/Shanghai")
        self.assertIn("api.nanzitravel.com", settings.ALLOWED_HOSTS)
        self.assertIn("admin.nanzitravel.com", settings.ALLOWED_HOSTS)
