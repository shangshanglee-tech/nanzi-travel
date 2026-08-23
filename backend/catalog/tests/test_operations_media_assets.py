from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from catalog.models import MediaAsset, Vessel


class OperationsMediaAssetApiTests(TestCase):
    def setUp(self):
        admin = get_user_model().objects.create_superuser(username="admin", password="admin123456")
        self.client.force_login(admin)
        self.vessel = Vessel.objects.create(name="阿蒙森号", slug="roald-amundsen")

    def test_admin_can_upload_and_list_media_assets(self):
        response = self.client.post(
            "/api/admin/v1/media-assets",
            data={"image": SimpleUploadedFile("ship.webp", b"image-data", content_type="image/webp"), "title": "阿蒙森号日落", "tags": "船只,阿蒙森号"},
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["title"], "阿蒙森号日落")
        self.assertEqual(response.json()["tags"], ["船只", "阿蒙森号"])

        listed = self.client.get("/api/admin/v1/media-assets")
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(listed.json()["results"][0]["id"], response.json()["id"])

    def test_upload_uses_file_name_and_asset_metadata_can_be_edited(self):
        created = self.client.post(
            "/api/admin/v1/media-assets",
            data={"image": SimpleUploadedFile("roald-amundsen-sunset.webp", b"image-data", content_type="image/webp")},
        )
        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.json()["title"], "roald-amundsen-sunset")
        updated = self.client.patch(
            f"/api/admin/v1/media-assets/{created.json()['id']}",
            data={"title": "阿蒙森号日落", "tags": ["船只", "南极"]},
            content_type="application/json",
        )
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.json()["tags"], ["船只", "南极"])

    def test_vessel_can_reuse_a_media_asset_as_its_card_image(self):
        asset = MediaAsset.objects.create(image="assets/images/ship.webp", title="阿蒙森号日落")
        response = self.client.post(f"/api/admin/v1/vessels/{self.vessel.id}/card-image", data={"asset_id": asset.id})
        self.assertEqual(response.status_code, 200)
        self.vessel.refresh_from_db()
        self.assertEqual(self.vessel.card_image.name, asset.image.name)

    def test_vessel_content_and_cabin_can_reuse_a_media_asset(self):
        asset = MediaAsset.objects.create(image="assets/images/ship.webp", title="阿蒙森号日落")
        block = self.client.post(
            f"/api/admin/v1/vessels/{self.vessel.id}/page-blocks",
            data={"block_type": "card", "title": "探索中心", "asset_id": asset.id},
        )
        self.assertEqual(block.status_code, 201)
        self.assertIn(asset.image.name, block.json()["image"])

        cabin = self.client.post(f"/api/admin/v1/vessels/{self.vessel.id}/cabins", data={"name": "极地套房"})
        image = self.client.post(f"/api/admin/v1/vessels/{self.vessel.id}/cabins/{cabin.json()['id']}/image", data={"asset_id": asset.id})
        self.assertEqual(image.status_code, 200)
        self.assertIn(asset.image.name, image.json()["image"])
