import logging.config

from django.conf import settings
from django.test import SimpleTestCase


class LoggingSettingsTests(SimpleTestCase):
    def test_logging_configuration_accepts_the_structured_formatter(self):
        logging.config.dictConfig(settings.LOGGING)
