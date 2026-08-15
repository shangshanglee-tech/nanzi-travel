import json
import tempfile
from pathlib import Path

from django.core.management import call_command
from django.test import TestCase

from catalog.models import CabinDisplayGroup, CabinType, Vessel, VesselContentStatus, VesselExperience


class ImportVesselContentTests(TestCase):
    def test_imports_editorial_content_idempotently_and_can_publish(self):
        payload = {
            "vessel": {
                "slug": "roald-amundsen",
                "name": "阿蒙森号",
                "official_name": "MS Roald Amundsen",
                "short_pitch": "混合动力极地探险船。",
                "content_status": "draft",
            },
            "experiences": [{"kind": "science", "title_zh": "科学中心", "body_zh": "探险队讲座。"}],
            "cabin_groups": [{"slug": "suite", "title_zh": "探险套房", "cabin_codes": ["MA"]}],
            "cabins": [{
                "official_code": "MA",
                "name": "XL 阳台套房",
                "official_name": "XL Suite with balcony",
                "category": "suite",
                "description_zh": "带阳台的宽敞套房。",
                "amenities": ["私人阳台"],
            }],
        }
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "vessel.json"
            source.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            call_command("import_vessel_content", source, "--publish")
            call_command("import_vessel_content", source, "--publish")

        vessel = Vessel.objects.get(slug="roald-amundsen")
        self.assertEqual(vessel.content_status, VesselContentStatus.PUBLISHED)
        self.assertIsNotNone(vessel.published_at)
        self.assertEqual(VesselExperience.objects.filter(vessel=vessel).count(), 1)
        self.assertEqual(CabinType.objects.filter(vessel=vessel, official_code="MA").count(), 1)
        self.assertEqual(
            list(CabinDisplayGroup.objects.get(vessel=vessel, slug="suite").cabins.values_list("official_code", flat=True)),
            ["MA"],
        )
