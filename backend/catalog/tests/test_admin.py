from django.contrib.admin.sites import site
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.urls import reverse

from catalog.admin import ProductAdmin, SiteSettingsAdmin
from catalog.forms import ProductAdminForm
from catalog.models import Destination, Product, ProductStatus, SiteSettings


class CatalogAdminTests(TestCase):
    def setUp(self):
        self.destination = Destination.objects.create(name="南极", slug="antarctica")

    def test_anonymous_user_cannot_open_product_admin(self):
        response = self.client.get(reverse("admin:catalog_product_changelist"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response.url)

    def test_product_is_registered_with_admin(self):
        self.assertIn(Product, site._registry)

    def test_publish_action_requires_confirmation_before_changing_status(self):
        product = Product.objects.create(
            destination=self.destination,
            title="待发布产品",
            slug="pending-product",
        )
        request = RequestFactory().post("/admin/catalog/product/")
        request.user = get_user_model().objects.create_superuser(
            username="operator",
            password="strong-password",
        )
        product_admin = ProductAdmin(Product, site)

        response = product_admin.publish_products(request, Product.objects.filter(pk=product.pk))

        product.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(product.status, ProductStatus.DRAFT)

    def test_confirmed_publish_action_sets_status_and_publish_time(self):
        product = Product.objects.create(
            destination=self.destination,
            title="待发布产品",
            slug="confirmed-product",
        )
        request = RequestFactory().post(
            "/admin/catalog/product/",
            {"confirm": "yes"},
        )
        request.user = get_user_model().objects.create_superuser(
            username="publisher",
            password="strong-password",
        )
        product_admin = ProductAdmin(Product, site)

        response = product_admin.publish_products(request, Product.objects.filter(pk=product.pk))

        product.refresh_from_db()
        self.assertIsNone(response)
        self.assertEqual(product.status, ProductStatus.PUBLISHED)
        self.assertIsNotNone(product.published_at)

    def test_archive_action_keeps_product_and_changes_its_status(self):
        product = Product.objects.create(
            destination=self.destination,
            title="准备下架",
            slug="archive-product",
            status=ProductStatus.PUBLISHED,
        )
        request = RequestFactory().post("/admin/catalog/product/")
        product_admin = ProductAdmin(Product, site)

        product_admin.archive_products(request, Product.objects.filter(pk=product.pk))

        product.refresh_from_db()
        self.assertEqual(Product.objects.filter(pk=product.pk).count(), 1)
        self.assertEqual(product.status, ProductStatus.ARCHIVED)

    def test_site_settings_admin_disallows_a_second_record(self):
        SiteSettings.objects.create()
        request = RequestFactory().get("/admin/catalog/sitesettings/add/")
        request.user = get_user_model().objects.create_superuser(
            username="settings-operator",
            password="strong-password",
        )
        settings_admin = SiteSettingsAdmin(SiteSettings, site)

        self.assertFalse(settings_admin.has_add_permission(request))


class ProductAdminFormTests(TestCase):
    def setUp(self):
        self.destination = Destination.objects.create(name="南极", slug="antarctica")
        self.base_data = {
            "destination": self.destination.pk,
            "title": "南极产品",
            "slug": "antarctica-product",
            "tags": "[]",
            "highlights": "[]",
            "included": "[]",
            "excluded": "[]",
            "suitable_for": "[]",
            "notices": "[]",
            "status": ProductStatus.DRAFT,
            "sort_order": 0,
        }

    def test_json_content_fields_reject_non_list_values(self):
        data = {**self.base_data, "tags": '{"name":"摄影"}'}

        form = ProductAdminForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("必须是列表", form.errors["tags"][0])

    def test_json_content_fields_reject_blank_list_items(self):
        data = {**self.base_data, "highlights": '["登陆南极", " "]'}

        form = ProductAdminForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("空白项", form.errors["highlights"][0])
