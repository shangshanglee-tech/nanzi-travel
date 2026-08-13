import tempfile
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase, override_settings

from catalog.models import Product, ProductStatus


HX_SOURCE = Path(__file__).resolve().parents[3] / "content" / "imports" / "hx-antarctica.json"
HX_HEROES = Path(__file__).resolve().parents[3] / "content" / "imports" / "hx-heroes"


class ImportHxAntarcticaTests(TestCase):
    def test_import_creates_published_products_and_managed_hero_files(self):
        with tempfile.TemporaryDirectory() as directory:
            media_root = Path(directory)
            with override_settings(MEDIA_ROOT=media_root):
                call_command(
                    "import_hx_antarctica",
                    HX_SOURCE,
                    heroes_dir=HX_HEROES,
                    status="published",
                )

                self.assertEqual(Product.objects.count(), 11)
                product = Product.objects.get(slug="highlights-of-antarctica")
                self.assertEqual(product.status, ProductStatus.PUBLISHED)
                self.assertTrue((media_root / product.hero_image.name).is_file())
                self.assertGreater(product.departures.count(), 0)
                self.assertGreater(product.itinerary_days.count(), 0)

    def test_import_updates_existing_products_without_duplicates(self):
        with tempfile.TemporaryDirectory() as directory:
            with override_settings(MEDIA_ROOT=Path(directory)):
                call_command("import_hx_antarctica", HX_SOURCE, heroes_dir=HX_HEROES, status="published")
                call_command("import_hx_antarctica", HX_SOURCE, heroes_dir=HX_HEROES, status="published")

        self.assertEqual(Product.objects.count(), 11)

    def test_imported_products_are_available_from_public_list_and_detail_apis(self):
        with tempfile.TemporaryDirectory() as directory:
            with override_settings(MEDIA_ROOT=Path(directory)):
                call_command("import_hx_antarctica", HX_SOURCE, heroes_dir=HX_HEROES, status="published")

                listing = self.client.get("/api/v1/products")
                detail = self.client.get("/api/v1/products/highlights-of-antarctica")

        self.assertEqual(listing.status_code, 200)
        self.assertEqual(len(listing.json()["results"]), 11)
        self.assertEqual(detail.status_code, 200)
        self.assertTrue(detail.json()["departures"])
