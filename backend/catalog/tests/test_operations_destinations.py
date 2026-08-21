import json

from django.contrib.auth import get_user_model
from django.test import TestCase

from catalog.models import Destination


class OperationsDestinationApiTests(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_superuser(
            username="admin",
            password="admin123456",
        )
        self.client.force_login(self.admin)

    def test_admin_can_create_destination(self):
        response = self.client.post(
            "/api/admin/v1/destinations",
            data=json.dumps({"name": "北极", "slug": "arctic"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["name"], "北极")
        self.assertNotIn("is_active", response.json())
        self.assertNotIn("sort_order", response.json())
        self.assertTrue(Destination.objects.filter(slug="arctic").exists())

    def test_admin_can_list_update_and_delete_destinations(self):
        destination = Destination.objects.create(name="南极", slug="antarctica", is_active=False, sort_order=20)

        list_response = self.client.get("/api/admin/v1/destinations")
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list_response.json()["results"][0]["slug"], "antarctica")
        self.assertNotIn("is_active", list_response.json()["results"][0])
        self.assertNotIn("sort_order", list_response.json()["results"][0])

        delete_response = self.client.delete(f"/api/admin/v1/destinations/{destination.pk}")
        self.assertEqual(delete_response.status_code, 204)
        self.assertFalse(Destination.objects.filter(pk=destination.pk).exists())

    def test_non_admin_cannot_read_destinations(self):
        self.client.logout()

        response = self.client.get("/api/admin/v1/destinations")

        self.assertIn(response.status_code, {401, 403})
