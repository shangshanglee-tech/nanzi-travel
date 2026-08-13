from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from catalog.models import Destination, Product, SiteSettings


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
