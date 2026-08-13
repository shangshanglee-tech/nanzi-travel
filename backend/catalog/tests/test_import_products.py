import json
import tempfile
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from catalog.models import Product, ProductStatus


EXAMPLE_FILE = Path(__file__).resolve().parents[3] / "content" / "examples" / "antarctica-demo.json"


class ImportProductsTests(TestCase):
    def test_importing_same_slug_twice_updates_without_duplicate(self):
        call_command("import_products", EXAMPLE_FILE, status="draft")
        call_command("import_products", EXAMPLE_FILE, status="draft")

        self.assertEqual(Product.objects.filter(slug="antarctica-demo").count(), 1)
        self.assertEqual(Product.objects.get().status, ProductStatus.DRAFT)

    def test_unknown_product_keys_are_rejected_before_database_writes(self):
        payload = json.loads(EXAMPLE_FILE.read_text(encoding="utf-8"))
        payload["products"][0]["unexpected_field"] = "不应静默忽略"
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "invalid.json"
            source.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

            with self.assertRaisesMessage(CommandError, "unexpected_field"):
                call_command("import_products", source, status="draft")

        self.assertFalse(Product.objects.exists())

    def test_published_import_requires_complete_public_content(self):
        with self.assertRaisesMessage(CommandError, "发布条件"):
            call_command("import_products", EXAMPLE_FILE, status="published")

        self.assertFalse(Product.objects.exists())
