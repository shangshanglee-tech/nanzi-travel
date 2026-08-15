import json
import tempfile
from pathlib import Path

from django.core.management import call_command
from django.test import TestCase

from catalog.models import CabinType, Departure, Destination, Product, Vessel


class ImportPolarContentTests(TestCase):
    def setUp(self):
        destination = Destination.objects.create(name="南极", slug="antarctica")
        Product.objects.create(
            destination=destination,
            title="12天南极半岛精华",
            slug="highlights-of-antarctica",
        )

    def test_import_expands_source_range_and_links_departure_to_vessel(self):
        payload = {
            "vessels": [{
                "slug": "roald-amundsen",
                "name": "阿蒙森号",
                "cabins": [{"name": "探险套房", "category": "套房", "summary": "拥有更充裕的私享空间。"}],
            }],
            "products": [{
                "slug": "highlights-of-antarctica",
                "summary": "一条适合第一次深入南极的经典线路。",
                "vessel_slugs": ["roald-amundsen"],
                "departures": [{"start_date": "2026-12-09", "vessel_slug": "roald-amundsen"}],
                "itinerary_segments": [{
                    "source_range": "Day 3-4",
                    "title": "穿越德雷克海峡",
                    "description": "在船上完成探险准备，并通过讲座了解南极。",
                }],
            }],
        }
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "polar.json"
            source.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            call_command("import_hx_polar_content", source)

        product = Product.objects.get(slug="highlights-of-antarctica")
        self.assertEqual(product.vessels.get().slug, "roald-amundsen")
        self.assertEqual(Vessel.objects.count(), 1)
        self.assertEqual(CabinType.objects.get().name, "探险套房")
        self.assertEqual(Departure.objects.get().vessel.slug, "roald-amundsen")
        self.assertEqual(product.itinerary_days.filter(source_range="Day 3-4").count(), 2)

    def test_default_import_preserves_manually_added_cabin(self):
        payload = {
            "vessels": [{
                "slug": "roald-amundsen",
                "name": "阿蒙森号",
                "cabins": [{"name": "官方舱型", "category": "套房"}],
            }],
            "products": [{
                "slug": "highlights-of-antarctica",
                "vessel_slugs": ["roald-amundsen"],
                "departures": [],
                "itinerary_segments": [],
            }],
        }
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "polar.json"
            source.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            call_command("import_hx_polar_content", source)
            CabinType.objects.create(
                vessel=Vessel.objects.get(slug="roald-amundsen"),
                name="人工舱型",
                summary="人工文案",
            )
            call_command("import_hx_polar_content", source)

        self.assertTrue(CabinType.objects.filter(name="人工舱型", summary="人工文案").exists())
