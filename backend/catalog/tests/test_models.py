from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms import modelform_factory
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
    VesselMedia,
    VesselPageBlock,
    VesselPageBlockImage,
)


class VesselPublicationTests(TestCase):
    def test_vessel_structured_facilities_default_to_disabled_or_zero(self):
        vessel = Vessel.objects.create(slug="facility-defaults", name="设施默认值测试船")

        self.assertFalse(vessel.is_hybrid)
        self.assertFalse(vessel.has_science_center)
        self.assertFalse(vessel.has_wifi)
        self.assertFalse(vessel.has_stabilization_system)
        self.assertEqual(vessel.restaurant_count, 0)
        self.assertEqual(vessel.bar_count, 0)
        self.assertFalse(vessel.has_fitness_center)
        self.assertEqual(vessel.heated_pool_count, 0)
        self.assertFalse(vessel.has_infinity_pool)
        self.assertFalse(vessel.has_sauna)
        self.assertFalse(vessel.has_executive_lounge)

    def test_vessel_card_tone_accepts_a_hex_color(self):
        vessel = Vessel(slug="card-tint", name="卡片底色测试船", card_tone="#071A32")

        vessel.full_clean()

    def test_vessel_card_tone_rejects_an_invalid_color(self):
        vessel = Vessel(slug="bad-card-tint", name="错误卡片底色测试船", card_tone="navy")

        with self.assertRaisesRegex(ValidationError, "请输入 #071A32 形式"):
            vessel.full_clean()

    def test_published_vessel_requires_a_card_image(self):
        vessel = Vessel(
            slug="no-hero",
            name="无封面图测试船",
            content_status="published",
            published_at=timezone.now(),
        )

        with self.assertRaisesRegex(ValidationError, "卡片图"):
            vessel.full_clean()

    def test_public_vessel_list_excludes_vessels_without_a_card_image(self):
        hidden = Vessel.objects.create(
            slug="no-hero",
            name="无封面图测试船",
            content_status="published",
            published_at=timezone.now(),
        )
        visible = Vessel.objects.create(
            slug="with-card",
            name="有卡片图测试船",
            card_image="vessels/cards/with-card.webp",
            content_status="published",
            published_at=timezone.now(),
        )

        self.assertEqual(list(Vessel.objects.public()), [visible])


class VesselPageComposerTests(TestCase):
    def setUp(self):
        self.vessel = Vessel.objects.create(slug="composer", name="页面编排测试船")

    def test_content_card_requires_a_title_and_image(self):
        block = VesselPageBlock(vessel=self.vessel, block_type="card")

        with self.assertRaisesRegex(ValidationError, "图片"):
            block.full_clean()

    def test_heading_only_requires_its_title(self):
        block = VesselPageBlock(vessel=self.vessel, block_type="heading", title="船上体验")

        block.full_clean()

    def test_deck_plan_requires_an_image(self):
        deck_plan = VesselDeckPlan(vessel=self.vessel, title="7 层甲板")

        with self.assertRaises(ValidationError) as error:
            deck_plan.full_clean()
        self.assertIn("image", error.exception.message_dict)

    def test_deck_plan_accepts_an_svg_source_file(self):
        form = modelform_factory(VesselDeckPlan, fields=("title", "image", "is_visible"))(
            data={"title": "Deck 3", "is_visible": "on"},
            files={"image": SimpleUploadedFile(
                "deck-3.svg",
                b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"></svg>',
                content_type="image/svg+xml",
            )},
        )

        self.assertTrue(form.is_valid(), form.errors)

    def test_additional_card_image_must_belong_to_a_card_on_the_same_vessel(self):
        other_vessel = Vessel.objects.create(slug="other-composer", name="另一艘测试船")
        heading = VesselPageBlock.objects.create(
            vessel=self.vessel, block_type="heading", title="分组标题"
        )
        other_card = VesselPageBlock.objects.create(
            vessel=other_vessel,
            block_type="card",
            title="另一艘船的卡片",
            image="vessels/page-blocks/other.webp",
        )

        with self.assertRaisesRegex(ValidationError, "内容卡片"):
            VesselPageBlockImage(
                vessel=self.vessel,
                page_block=heading,
                image="vessels/page-block-images/heading.webp",
            ).full_clean()
        with self.assertRaisesRegex(ValidationError, "同一艘船"):
            VesselPageBlockImage(
                vessel=self.vessel,
                page_block=other_card,
                image="vessels/page-block-images/other-vessel.webp",
            ).full_clean()


class ProductPublishingTests(TestCase):
    def setUp(self):
        self.destination = Destination.objects.create(name="南极", slug="antarctica")

    def test_public_queryset_only_returns_published_products(self):
        Product.objects.create(
            destination=self.destination,
            title="草稿",
            slug="draft",
            status="draft",
        )
        live = Product.objects.create(
            destination=self.destination,
            title="已发布",
            slug="live",
            status="published",
            published_at=timezone.now(),
        )

        self.assertEqual(list(Product.objects.public()), [live])

    def test_published_product_requires_published_at(self):
        product = Product(
            destination=self.destination,
            title="未定时",
            slug="invalid",
            status="published",
        )

        with self.assertRaisesMessage(ValidationError, "published_at"):
            product.full_clean()


class SiteSettingsTests(TestCase):
    def test_saving_settings_replaces_the_single_site_record(self):
        SiteSettings.objects.create(brand_name="旧名称")
        SiteSettings.objects.create(brand_name="小楠子爱旅行")

        self.assertEqual(SiteSettings.objects.count(), 1)
        self.assertEqual(SiteSettings.objects.get().brand_name, "小楠子爱旅行")


class PolarContentRelationshipTests(TestCase):
    def setUp(self):
        self.destination = Destination.objects.create(name="南极", slug="antarctica")

    def test_route_and_vessel_are_peer_objects_linked_many_to_many(self):
        vessel = Vessel.objects.create(slug="roald-amundsen", name="阿蒙森号")
        product = Product.objects.create(
            destination=self.destination,
            title="南极半岛精华",
            slug="highlights",
        )
        product.vessels.add(vessel)
        departure = Departure.objects.create(
            product=product,
            vessel=vessel,
            start_date="2026-12-09",
        )

        self.assertEqual(list(vessel.products.all()), [product])
        self.assertEqual(departure.vessel, vessel)


class VesselEditorialContentTests(TestCase):
    def setUp(self):
        self.vessel = Vessel.objects.create(slug="roald-amundsen", name="阿蒙森号")

    def test_published_vessel_requires_published_at(self):
        self.vessel.content_status = VesselContentStatus.PUBLISHED

        with self.assertRaisesMessage(ValidationError, "published_at"):
            self.vessel.full_clean()

    def test_cabin_can_belong_to_multiple_display_groups(self):
        cabin = CabinType.objects.create(vessel=self.vessel, name="MA", official_code="MA")
        suite = CabinDisplayGroup.objects.create(vessel=self.vessel, slug="suite", title_zh="套房")
        balcony = CabinDisplayGroup.objects.create(vessel=self.vessel, slug="balcony", title_zh="阳台房")
        suite.cabins.add(cabin)
        balcony.cabins.add(cabin)

        self.assertEqual(list(cabin.display_groups.all()), [suite, balcony])

    def test_media_requires_exactly_one_parent(self):
        cabin = CabinType.objects.create(vessel=self.vessel, name="MA", official_code="MA")
        media = VesselMedia(vessel=self.vessel, cabin=cabin, image="vessels/test.jpg")

        with self.assertRaisesMessage(ValidationError, "一个媒体资源"):
            media.full_clean()
