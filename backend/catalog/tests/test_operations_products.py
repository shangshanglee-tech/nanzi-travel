import json

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from catalog.models import Destination, ItineraryDay, Product, Vessel


class OperationsProductApiTests(TestCase):
    def setUp(self):
        admin = get_user_model().objects.create_superuser(username="admin", password="admin123456")
        self.client.force_login(admin)
        self.destination = Destination.objects.create(name="南极", slug="antarctica")
        self.vessel = Vessel.objects.create(name="阿蒙森号", slug="roald-amundsen")

    def test_admin_can_save_product_with_departure_and_daily_itinerary(self):
        payload = {
            "title": "12天南极半岛精华",
            "slug": "antarctica-12-days",
            "subtitle": "南极初体验",
            "summary": "从乌斯怀亚出发的经典南极航线。",
            "destination_id": self.destination.id,
            "vessel_ids": [self.vessel.id],
            "status": "draft",
            "duration_days": 12,
            "tags": ["南极", "探险"],
            "departures": [
                {
                    "label": "2027年1月团期",
                    "start_date": "2027-01-03",
                    "end_date": "2027-01-14",
                    "vessel_id": self.vessel.id,
                    "consultation_status": "可咨询",
                }
            ],
            "itinerary_days": [
                {"day_number": 1, "title": "抵达乌斯怀亚", "description": "登船前自由活动。"}
            ],
        }

        response = self.client.post(
            "/api/admin/v1/products",
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        product = Product.objects.get(slug="antarctica-12-days")
        self.assertEqual(product.destination, self.destination)
        self.assertEqual(list(product.vessels.all()), [self.vessel])
        self.assertEqual(product.departures.count(), 1)
        self.assertEqual(ItineraryDay.objects.get(product=product).title, "抵达乌斯怀亚")
        self.assertEqual(response.json()["departures"][0]["vessel_id"], self.vessel.id)

    def test_admin_can_list_update_and_delete_product(self):
        product = Product.objects.create(
            destination=self.destination,
            title="南极经典",
            slug="antarctica-classic",
        )

        self.assertEqual(self.client.get("/api/admin/v1/products").status_code, 200)

        update_response = self.client.patch(
            f"/api/admin/v1/products/{product.pk}",
            data=json.dumps({"title": "南极经典路线", "status": "published"}),
            content_type="application/json",
        )
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.json()["status"], "published")
        self.assertIsNotNone(Product.objects.get(pk=product.pk).published_at)

        self.assertEqual(self.client.delete(f"/api/admin/v1/products/{product.pk}").status_code, 204)
        self.assertFalse(Product.objects.filter(pk=product.pk).exists())

    def test_admin_can_upload_hero_and_manage_gallery_images(self):
        product = Product.objects.create(destination=self.destination, title="南极经典", slug="antarctica-classic")
        image = SimpleUploadedFile("antarctica.webp", b"not-a-real-image", content_type="image/webp")

        hero_response = self.client.post(
            f"/api/admin/v1/products/{product.pk}/hero-image",
            data={"image": image},
        )
        self.assertEqual(hero_response.status_code, 200)
        self.assertIn("hero_image", hero_response.json())

        gallery_response = self.client.post(
            f"/api/admin/v1/products/{product.pk}/images",
            data={"image": SimpleUploadedFile("gallery.webp", b"gallery", content_type="image/webp"), "alt_text": "南极冰山"},
        )
        self.assertEqual(gallery_response.status_code, 201)
        image_id = gallery_response.json()["id"]
        self.assertEqual(gallery_response.json()["alt_text"], "南极冰山")

        self.assertEqual(self.client.delete(f"/api/admin/v1/products/{product.pk}/images/{image_id}").status_code, 204)
