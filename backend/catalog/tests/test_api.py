from django.test import TestCase
from django.utils import timezone

from catalog.models import Destination, Product, SiteSettings


class ProductApiTests(TestCase):
    def setUp(self):
        destination = Destination.objects.create(name="南极", slug="antarctica")
        self.live = Product.objects.create(
            destination=destination,
            title="南极精华",
            slug="antarctica-classic",
            subtitle="经典路线",
            summary="第一次前往南极的经典选择。",
            status="published",
            published_at=timezone.now(),
            duration_days=12,
            tags=["首次去南极", "摄影"],
            highlights=["登陆南极半岛"],
            notices=["实际行程受天气影响"],
        )
        Product.objects.create(
            destination=destination,
            title="签约中",
            slug="reserve",
            status="draft",
        )

    def test_product_list_hides_drafts(self):
        response = self.client.get("/api/v1/products")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [item["slug"] for item in response.json()["results"]],
            ["antarctica-classic"],
        )

    def test_product_list_filters_by_destination_duration_and_tag(self):
        response = self.client.get(
            "/api/v1/products",
            {
                "destination": "antarctica",
                "duration_min": "10",
                "duration_max": "14",
                "tag": "摄影",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["results"][0]["slug"], "antarctica-classic")

    def test_unknown_product_uses_stable_error_shape(self):
        response = self.client.get("/api/v1/products/not-found")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json(),
            {"error": {"code": "not_found", "message": "产品不存在或尚未发布"}},
        )

    def test_invalid_month_filter_uses_stable_error_shape(self):
        response = self.client.get("/api/v1/products", {"month": "2026/11"})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {
                "error": {
                    "code": "invalid_filter",
                    "message": "出发月份格式应为 YYYY-MM",
                }
            },
        )

    def test_public_product_responses_are_short_lived_cacheable(self):
        response = self.client.get("/api/v1/products/antarctica-classic")

        self.assertEqual(response["Cache-Control"], "public, max-age=60")
        self.assertNotIn("price", response.json())


class SiteAndHomeApiTests(TestCase):
    def setUp(self):
        destination = Destination.objects.create(name="南极", slug="antarctica")
        Product.objects.create(
            destination=destination,
            title="已发布产品",
            slug="published-product",
            status="published",
            published_at=timezone.now(),
        )
        Product.objects.create(
            destination=destination,
            title="预备产品",
            slug="draft-product",
            status="draft",
        )
        SiteSettings.objects.create(filing_number="渝ICP备2026003102号-1")

    def test_home_returns_only_public_products_and_active_destinations(self):
        response = self.client.get("/api/v1/home")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [item["slug"] for item in response.json()["featured_products"]],
            ["published-product"],
        )
        self.assertEqual(response.json()["destinations"][0]["slug"], "antarctica")

    def test_site_returns_brand_official_account_and_filing_copy(self):
        response = self.client.get("/api/v1/site")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["brand_name"], "小楠子爱旅行")
        self.assertEqual(response.json()["official_account_name"], "小楠子爱旅行俱乐部")
        self.assertEqual(response.json()["filing_number"], "渝ICP备2026003102号-1")

    def test_health_endpoint_does_not_require_catalog_data(self):
        response = self.client.get("/healthz")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})
