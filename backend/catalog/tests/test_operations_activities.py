import json

from django.contrib.auth import get_user_model
from django.test import TestCase

from catalog.models import Activity, Destination, Product


class OperationsActivityApiTests(TestCase):
    def setUp(self):
        admin = get_user_model().objects.create_superuser(username="admin", password="admin123456")
        self.client.force_login(admin)
        self.destination = Destination.objects.create(name="南极", slug="antarctica")
        self.product = Product.objects.create(destination=self.destination, title="南极半岛", slug="antarctica-peninsula")

    def test_admin_can_create_activity_with_destination_and_products(self):
        response = self.client.post(
            "/api/admin/v1/activities",
            data=json.dumps({
                "title": "库佛维尔岛远足",
                "destination_id": self.destination.id,
                "summary": "在企鹅群与冰川之间徒步。",
                "explanation": "登陆与远足将由探险队根据天气安排。",
                "product_ids": [self.product.id],
                "status": "draft",
            }),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        activity = Activity.objects.get(title="库佛维尔岛远足")
        self.assertEqual(activity.destination, self.destination)
        self.assertEqual(list(activity.products.all()), [self.product])
        self.assertEqual(response.json()["explanation"], "登陆与远足将由探险队根据天气安排。")
