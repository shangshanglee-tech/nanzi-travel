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

    def test_admin_can_create_activity_with_rich_content(self):
        response = self.client.post(
            "/api/admin/v1/activities",
            data=json.dumps({
                "title": "库佛维尔岛远足",
                "destination_id": self.destination.id,
                "content": "<h3>活动亮点</h3><ul><li>在企鹅群与冰川之间徒步</li></ul>",
                "status": "draft",
            }),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        activity = Activity.objects.get(title="库佛维尔岛远足")
        self.assertEqual(activity.destination, self.destination)
        self.assertEqual(list(activity.products.all()), [])
        self.assertEqual(response.json()["content"], "<h3>活动亮点</h3><ul><li>在企鹅群与冰川之间徒步</li></ul>")

    def test_admin_can_associate_activity_from_product(self):
        activity = Activity.objects.create(destination=self.destination, title="库佛维尔岛远足")
        response = self.client.patch(
            f"/api/admin/v1/products/{self.product.id}",
            data=json.dumps({"activity_ids": [activity.id]}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.product.refresh_from_db()
        self.assertEqual(list(self.product.activities.all()), [activity])

    def test_admin_can_create_activity_without_destination(self):
        response = self.client.post(
            "/api/admin/v1/activities",
            data=json.dumps({"title": "冰上皮划艇", "status": "draft"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertIsNone(Activity.objects.get(title="冰上皮划艇").destination)
