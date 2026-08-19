from django.test import TestCase
from django.utils import timezone

from catalog.models import (
    CabinDisplayGroup,
    CabinType,
    Departure,
    Destination,
    Product,
    SiteSettings,
    Vessel,
    VesselContentStatus,
    VesselDeckPlan,
    VesselExperience,
    VesselPageBlock,
    VesselPageBlockImage,
)


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
        self.vessel = Vessel.objects.create(
            slug="roald-amundsen",
            name="阿蒙森号",
            content_status=VesselContentStatus.PUBLISHED,
            published_at=timezone.now(),
        )
        self.live.vessels.add(self.vessel)
        Departure.objects.create(
            product=self.live,
            vessel=self.vessel,
            start_date="2027-01-05",
            end_date="2027-01-16",
            label="2027年1月团期",
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

    def test_product_list_exposes_only_filter_values_present_in_public_products(self):
        response = self.client.get("/api/v1/products")

        self.assertEqual(
            response.json()["filters"],
            {
                "destinations": [{"name": "南极", "slug": "antarctica"}],
                "months": ["2027-01"],
                "durations": [12],
                "tags": ["首次去南极", "摄影"],
            },
        )

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

    def test_product_detail_exposes_possible_vessels_and_departure_vessel(self):
        response = self.client.get("/api/v1/products/antarctica-classic")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["vessels"][0]["slug"], "roald-amundsen")
        self.assertEqual(response.json()["departures"][0]["vessel"]["slug"], "roald-amundsen")


class VesselApiTests(TestCase):
    def setUp(self):
        self.vessel = Vessel.objects.create(
            slug="roald-amundsen",
            name="阿蒙森号",
            intro_zh="面向极地探索的旗舰探险船。",
            card_image="vessels/cards/roald-amundsen-card.webp",
            card_tone="#071A32",
            is_hybrid=True,
            has_science_center=True,
            has_wifi=True,
            has_stabilization_system=True,
            restaurant_count=3,
            bar_count=2,
            has_fitness_center=True,
            heated_pool_count=1,
            has_infinity_pool=True,
            has_sauna=True,
            has_executive_lounge=True,
            content_status=VesselContentStatus.PUBLISHED,
            published_at=timezone.now(),
        )
        Vessel.objects.create(slug="draft-vessel", name="草稿船", content_status=VesselContentStatus.DRAFT)
        experience = VesselExperience.objects.create(
            vessel=self.vessel,
            kind="science-centre",
            title_zh="科学中心",
            title_en="Science Center",
            body_zh="跟随探险队深入理解目的地。",
        )
        cabin = CabinType.objects.create(
            vessel=self.vessel,
            name="XL 探险套房",
            official_code="MA",
            max_guests=2,
            deck="8层甲板",
            amenities=["迷你吧"],
        )
        group = CabinDisplayGroup.objects.create(vessel=self.vessel, slug="suite", title_zh="套房")
        group.cabins.add(cabin)
        VesselPageBlock.objects.create(
            vessel=self.vessel, block_type="heading", title="探索与学习", sort_order=10
        )
        science_block = VesselPageBlock.objects.create(
            vessel=self.vessel,
            block_type="card",
            title="科学中心",
            image="vessels/page-blocks/science-centre.webp",
            body="和探险队一起理解极地。",
            sort_order=20,
        )
        VesselPageBlockImage.objects.create(
            vessel=self.vessel,
            page_block=science_block,
            image="vessels/page-block-images/science-centre-2.webp",
            sort_order=10,
        )
        VesselPageBlockImage.objects.create(
            vessel=self.vessel,
            page_block=science_block,
            image="vessels/page-block-images/science-centre-hidden.webp",
            is_visible=False,
            sort_order=20,
        )
        VesselPageBlock.objects.create(
            vessel=self.vessel,
            block_type="card",
            title="隐藏卡片",
            image="vessels/page-blocks/hidden.webp",
            is_visible=False,
            sort_order=30,
        )
        VesselDeckPlan.objects.create(
            vessel=self.vessel,
            title="7 层甲板",
            description="公共活动空间",
            image="vessels/deck-plans/deck-7.webp",
        )
        self.vessel.show_deck_plans = False
        self.vessel.save(update_fields=["show_deck_plans", "updated_at"])
        self.experience = experience

    def test_vessel_list_hides_drafts(self):
        response = self.client.get("/api/v1/vessels")

        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["slug"] for item in response.json()["results"]], ["roald-amundsen"])
        self.assertEqual(response.json()["results"][0]["card_tone"], "#071A32")
        self.assertTrue(response.json()["results"][0]["card_image"].endswith("roald-amundsen-card.webp"))

    def test_vessel_detail_exposes_editorial_modules_and_grouped_cabins(self):
        response = self.client.get("/api/v1/vessels/roald-amundsen")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["intro_zh"], "面向极地探索的旗舰探险船。")
        for removed_field in ("short_pitch", "features", "hero_image", "intro_en", "source_url"):
            self.assertNotIn(removed_field, payload)
        self.assertTrue(payload["is_hybrid"])
        self.assertTrue(payload["has_science_center"])
        self.assertTrue(payload["has_wifi"])
        self.assertTrue(payload["has_stabilization_system"])
        self.assertEqual(payload["restaurant_count"], 3)
        self.assertEqual(payload["bar_count"], 2)
        self.assertTrue(payload["has_fitness_center"])
        self.assertEqual(payload["heated_pool_count"], 1)
        self.assertTrue(payload["has_infinity_pool"])
        self.assertTrue(payload["has_sauna"])
        self.assertTrue(payload["has_executive_lounge"])
        self.assertTrue(payload["show_cabins"])
        self.assertTrue(payload["show_deck_plans"])
        self.assertEqual(
            [(block["block_type"], block["title"]) for block in payload["page_blocks"]],
            [("heading", "探索与学习"), ("card", "科学中心")],
        )
        self.assertEqual(
            [image.rsplit("/", 1)[-1] for image in payload["page_blocks"][1]["images"]],
            ["science-centre.webp", "science-centre-2.webp"],
        )
        self.assertEqual(payload["deck_plans"][0]["title"], "7 层甲板")
        self.assertTrue(payload["deck_plans"][0]["image"].endswith("deck-7.webp"))
        self.assertNotIn("description", payload["deck_plans"][0])
        self.assertEqual(payload["experiences"][0]["title_zh"], "科学中心")
        self.assertEqual(payload["cabin_groups"][0]["cabins"][0]["official_code"], "MA")
        self.assertEqual(payload["cabin_groups"][0]["cabins"][0]["amenities"], ["迷你吧"])

    def test_draft_vessel_detail_returns_not_found(self):
        response = self.client.get("/api/v1/vessels/draft-vessel")

        self.assertEqual(response.status_code, 404)

    def test_vessel_icon_endpoint_applies_the_requested_vessel_tone(self):
        response = self.client.get("/api/v1/vessel-icons/lounge.svg", {"tone": "071A32"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "image/svg+xml")
        self.assertIn(b'fill="#071A32"', response.content)
        self.assertNotIn(b'#323332', response.content)


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
