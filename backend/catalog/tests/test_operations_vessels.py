from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from catalog.models import CabinDisplayGroup, CabinType, Vessel, VesselPageBlock


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

    def test_admin_can_manage_ordered_vessel_page_blocks(self):
        heading = self.client.post(
            f"/api/admin/v1/vessels/{self.vessel.pk}/page-blocks",
            data={"block_type": "heading", "title": "探索与学习"},
        )
        self.assertEqual(heading.status_code, 201)
        heading_id = heading.json()["id"]

        card = self.client.post(
            f"/api/admin/v1/vessels/{self.vessel.pk}/page-blocks",
            data={
                "block_type": "card",
                "title": "科学中心",
                "body": "与探险队员一起探索极地。",
                "image": SimpleUploadedFile("science.webp", b"not-a-real-image", content_type="image/webp"),
            },
        )
        self.assertEqual(card.status_code, 201)
        card_id = card.json()["id"]

        extra = self.client.post(
            f"/api/admin/v1/vessels/{self.vessel.pk}/page-blocks/{card_id}/images",
            data={"image": SimpleUploadedFile("science-2.webp", b"second-image", content_type="image/webp")},
        )
        self.assertEqual(extra.status_code, 201)
        self.assertEqual(extra.json()["sort_order"], 0)

        reordered = self.client.patch(
            f"/api/admin/v1/vessels/{self.vessel.pk}/page-blocks/order",
            data={"ids": [card_id, heading_id]},
            content_type="application/json",
        )
        self.assertEqual(reordered.status_code, 200)
        self.assertEqual(list(VesselPageBlock.objects.values_list("id", flat=True)), [card_id, heading_id])

        self.assertEqual(self.client.delete(f"/api/admin/v1/vessels/{self.vessel.pk}/page-blocks/{card_id}").status_code, 204)

    def test_admin_can_manage_cabins_and_display_groups(self):
        cabin_response = self.client.post(
            f"/api/admin/v1/vessels/{self.vessel.pk}/cabins",
            data={"name": "极地套房", "category": "套房", "size_sqm": "28.0", "max_guests": 2, "is_visible": True},
        )
        self.assertEqual(cabin_response.status_code, 201)
        cabin_id = cabin_response.json()["id"]
        self.assertEqual(cabin_response.json()["name"], "极地套房")

        updated = self.client.patch(
            f"/api/admin/v1/vessels/{self.vessel.pk}/cabins/{cabin_id}",
            data={"summary": "带私人阳台的宽敞套房。", "display_tags": ["阳台", "套房"]},
            content_type="application/json",
        )
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.json()["display_tags"], ["阳台", "套房"])

        group_response = self.client.post(
            f"/api/admin/v1/vessels/{self.vessel.pk}/cabin-groups",
            data={"slug": "suite", "title_zh": "套房", "cabin_ids": [cabin_id]},
            content_type="application/json",
        )
        self.assertEqual(group_response.status_code, 201)
        self.assertEqual(list(CabinDisplayGroup.objects.get(pk=group_response.json()["id"]).cabins.values_list("id", flat=True)), [cabin_id])
        self.assertEqual(self.client.delete(f"/api/admin/v1/vessels/{self.vessel.pk}/cabins/{cabin_id}").status_code, 204)
