from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from catalog.models import Vessel


class OperationsVesselApiTests(TestCase):
    def setUp(self):
        admin = get_user_model().objects.create_superuser(username="admin", password="admin123456")
        self.client.force_login(admin)
        self.vessel = Vessel.objects.create(
            name="阿蒙森号",
            official_name="MS Roald Amundsen",
            slug="roald-amundsen",
            card_image="vessels/cards/amundsen.webp",
        )

    def test_admin_can_list_and_update_vessel_core_content(self):
        response = self.client.get("/api/admin/v1/vessels")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["results"][0]["name"], "阿蒙森号")

        response = self.client.patch(
            f"/api/admin/v1/vessels/{self.vessel.pk}",
            data={
                "summary": "搭载科学团队的极地探险船。",
                "card_tone": "#071A32",
                "capacity": 490,
                "has_science_center": True,
                "content_status": "published",
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["capacity"], 490)
        self.assertTrue(response.json()["has_science_center"])
        self.assertIsNotNone(response.json()["published_at"])

    def test_admin_can_upload_vessel_card_image(self):
        response = self.client.post(
            f"/api/admin/v1/vessels/{self.vessel.pk}/card-image",
            data={"image": SimpleUploadedFile("amundsen.webp", b"not-a-real-image", content_type="image/webp")},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("card_image", response.json())
