from django.contrib.admin.sites import site
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import QueryDict
from django.test import RequestFactory, TestCase
from django.urls import reverse
from pathlib import Path

from catalog.admin import ProductAdmin, SiteSettingsAdmin, VesselAdmin, VesselDeckPlanInline, VesselPageBlockInlineForm
from catalog.forms import AdditionalImagesPreviewWidget, ProductAdminForm
from catalog.models import (
    CabinDisplayGroup,
    Destination,
    Product,
    ProductStatus,
    SiteSettings,
    Vessel,
    VesselContentStatus,
    VesselDeckPlan,
    VesselExperience,
    VesselMedia,
    VesselPageBlock,
    VesselPageBlockImage,
)


class CatalogAdminTests(TestCase):
    def setUp(self):
        self.destination = Destination.objects.create(name="南极", slug="antarctica")

    def test_existing_card_image_delete_widget_submits_all_selected_image_ids(self):
        data = QueryDict("", mutable=True)
        data.setlist("page_blocks-0-existing_additional_images", ["17", "18"])

        selected_ids = AdditionalImagesPreviewWidget().value_from_datadict(
            data,
            {},
            "page_blocks-0-existing_additional_images",
        )

        self.assertEqual(selected_ids, ["17", "18"])

    def test_anonymous_user_cannot_open_product_admin(self):
        response = self.client.get(reverse("admin:catalog_product_changelist"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response.url)

    def test_operations_sidebar_contains_only_daily_editorial_entries(self):
        user = get_user_model().objects.create_superuser(
            username="operations-sidebar-user",
            password="strong-password",
        )
        self.client.force_login(user)

        response = self.client.get(reverse("admin:catalog_vessel_changelist"))

        self.assertContains(response, 'data-operations-nav="true"')
        self.assertContains(response, "内容配置")
        self.assertContains(response, "旅行产品")
        self.assertContains(response, "目的地")
        self.assertContains(response, "船只")
        self.assertContains(response, "站点设置")
        self.assertNotContains(response, "内容管理")
        self.assertNotContains(response, ">系统<")
        self.assertContains(response, 'data-operations-nav-item="vessel" data-active="true"')
        self.assertNotContains(response, 'data-operations-nav-item="用户"')
        self.assertNotContains(response, 'data-operations-nav-item="组"')

    def test_admin_home_uses_the_streamlined_operations_navigation(self):
        user = get_user_model().objects.create_superuser(
            username="operations-home-user",
            password="strong-password",
        )
        self.client.force_login(user)

        response = self.client.get(reverse("admin:index"))

        self.assertContains(response, "内容配置")
        self.assertContains(response, "站点设置")
        self.assertContains(response, reverse("admin:catalog_product_changelist"))
        self.assertContains(response, reverse("admin:catalog_destination_changelist"))
        self.assertContains(response, reverse("admin:catalog_vessel_changelist"))
        self.assertContains(response, reverse("admin:catalog_sitesettings_changelist"))
        self.assertNotContains(response, "最近动作")
        self.assertNotContains(response, ">增加<")
        self.assertNotContains(response, ">修改<")

    def test_vessel_editor_renders_six_tabs_without_replacing_formsets(self):
        vessel = Vessel.objects.create(slug="tabbed-editor", name="Tab 编辑测试船")
        user = get_user_model().objects.create_superuser(
            username="tabbed-vessel-editor-user",
            password="strong-password",
        )
        self.client.force_login(user)

        response = self.client.get(reverse("admin:catalog_vessel_change", args=[vessel.pk]))

        self.assertContains(response, 'data-vessel-editor-tabs="true"')
        for label in ("基础信息", "首页卡片", "结构化事实", "页面内容", "舱位", "甲板图"):
            self.assertContains(response, label)
        self.assertContains(response, 'name="page_blocks-TOTAL_FORMS"')
        self.assertContains(response, 'name="page_blocks-INITIAL_FORMS"')
        self.assertContains(response, 'class="vessel-editor-page-header"')
        self.assertContains(response, 'form="vessel_form" name="_save"')
        self.assertContains(response, 'class="deletelink"')
        self.assertNotContains(response, "保存并增加另一个")
        self.assertNotContains(response, "历史")

        source = (Path(__file__).resolve().parents[1] / "static/catalog/vessel-editor-tabs.js").read_text(encoding="utf-8")
        self.assertIn("firstInvalidPanel", source)
        self.assertIn("data-vessel-tab", source)

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

    def test_vessel_editor_is_registered_with_content_inlines(self):
        self.assertIn(Vessel, site._registry)
        vessel_admin = site._registry[Vessel]
        inline_models = {inline.model for inline in vessel_admin.inlines}

        self.assertEqual(vessel_admin.__class__, VesselAdmin)
        self.assertTrue({CabinDisplayGroup, VesselPageBlock, VesselDeckPlan}.issubset(inline_models))
        self.assertNotIn(VesselPageBlockImage, inline_models)
        self.assertNotIn(VesselExperience, inline_models)
        self.assertNotIn(VesselMedia, inline_models)

    def test_vessel_editor_has_page_composer_switches_and_grouping_script(self):
        vessel_admin = VesselAdmin(Vessel, site)
        editable_fields = {
            field
            for _, options in vessel_admin.fieldsets
            for field in options["fields"]
        }

        self.assertIn("show_cabins", editable_fields)
        self.assertNotIn("show_deck_plans", editable_fields)
        self.assertIn("catalog/vessel-page-blocks-admin.js", vessel_admin.media._js)
        self.assertIn("catalog/deck-plan-upload-admin.js", vessel_admin.media._js)

    def test_vessel_deck_plan_editor_exposes_only_name_and_image(self):
        self.assertEqual(
            VesselDeckPlanInline.fields,
            ("title", "image", "sort_order"),
        )

    def test_vessel_deck_plan_editor_shows_uploaded_preview_with_delete_control(self):
        vessel = Vessel.objects.create(slug="deck-preview", name="甲板缩略图测试船")
        VesselDeckPlan.objects.create(
            vessel=vessel,
            title="Deck 3",
            image="vessels/deck-plans/deck-3.svg",
        )
        user = get_user_model().objects.create_superuser(username="deck-preview-operator", password="strong-password")
        self.client.force_login(user)

        response = self.client.get(reverse("admin:catalog_vessel_change", args=[vessel.pk]))

        self.assertContains(response, 'data-deck-plan-upload="true"')
        self.assertContains(response, 'data-deck-plan-preview="true"')
        self.assertContains(response, 'data-deck-plan-delete="true"')
        self.assertContains(response, 'class="deck-plan-preview-image"')
        self.assertContains(response, 'data-deck-plan-row-delete="true"')
        self.assertContains(response, 'class="deck-plan-editor__delete-control" hidden')
        self.assertNotContains(response, 'name="deck_plans-0-description"')
        self.assertNotContains(response, 'name="deck_plans-0-is_visible"')
        stylesheet = (Path(__file__).resolve().parents[1] / "static/catalog/admin-operations.css").read_text(encoding="utf-8")
        self.assertRegex(
            stylesheet,
            r"\.deck-plan-preview-image\s*\{[^}]*width:\s*400px[^}]*height:\s*300px[^}]*object-fit:\s*contain",
        )
        script = (Path(__file__).resolve().parents[1] / "static/catalog/deck-plan-upload-admin.js").read_text(encoding="utf-8")
        self.assertIn("data-deck-plan-row-delete", script)
        self.assertIn("pendingDelete", script)

    def test_current_vessel_change_form_includes_page_block_management_fields(self):
        vessel = Vessel.objects.create(slug="admin-page-blocks", name="后台页面内容测试船")
        block = VesselPageBlock.objects.create(
            vessel=vessel,
            block_type="card",
            title="可增加图片的内容卡片",
            image="vessels/page-blocks/primary.jpg",
        )
        VesselPageBlockImage.objects.create(
            vessel=vessel,
            page_block=block,
            image="vessels/page-block-images/secondary.jpg",
            sort_order=1,
        )
        user = get_user_model().objects.create_superuser(username="page-block-operator", password="strong-password")
        self.client.force_login(user)

        response = self.client.get(reverse("admin:catalog_vessel_change", args=[vessel.pk]))

        self.assertContains(response, 'name="page_blocks-TOTAL_FORMS"')
        self.assertContains(response, 'name="page_blocks-INITIAL_FORMS"')
        self.assertContains(response, 'name="page_blocks-0-additional_images"')
        self.assertContains(response, "已上传图片")
        self.assertContains(response, "secondary.jpg")
        self.assertNotContains(response, 'name="page_blocks-0-is_visible"')
        self.assertContains(response, 'data-page-block-list="true"')
        self.assertContains(response, 'data-page-block-create="heading"')
        self.assertContains(response, 'data-page-block-create="card"')
        self.assertContains(response, '<div class="add-row" hidden>')
        self.assertNotContains(response, "船只媒体资源")

    def test_heading_editor_hides_image_configuration(self):
        source = (Path(__file__).resolve().parents[1] / "static/catalog/vessel-page-blocks-admin.js").read_text(encoding="utf-8")
        stylesheet = (Path(__file__).resolve().parents[1] / "static/catalog/admin-operations.css").read_text(encoding="utf-8")

        self.assertIn('row.classList.toggle("is-heading", isHeading)', source)
        self.assertIn(".page-block-editor__rows > .inline-related.is-heading .field-image", stylesheet)

    def test_content_card_editor_uploads_multiple_additional_images_directly(self):
        vessel = Vessel.objects.create(slug="card-image-upload", name="多图上传测试船")
        block = VesselPageBlock.objects.create(
            vessel=vessel,
            block_type="card",
            title="极地景观",
            image="vessels/page-blocks/primary.jpg",
        )
        form = VesselPageBlockInlineForm(
            data={
                "block_type": "card",
                "title": block.title,
                "body": "",
                "is_visible": "on",
                "sort_order": "0",
            },
            files={
                "additional_images": [
                    SimpleUploadedFile("second.jpg", b"second", content_type="image/jpeg"),
                    SimpleUploadedFile("third.jpg", b"third", content_type="image/jpeg"),
                ]
            },
            instance=block,
        )

        self.assertTrue(form.is_valid(), form.errors)
        form.save()

        self.assertEqual(block.additional_images.count(), 2)
        self.assertEqual(
            list(block.additional_images.values_list("sort_order", flat=True)),
            [0, 1],
        )

    def test_content_card_editor_shows_existing_additional_images_for_review(self):
        vessel = Vessel.objects.create(slug="card-image-review", name="多图回显测试船")
        block = VesselPageBlock.objects.create(
            vessel=vessel,
            block_type="card",
            title="Explorer Lounge & Bar",
            image="vessels/page-blocks/primary.jpg",
        )
        extra_image = VesselPageBlockImage.objects.create(
            vessel=vessel,
            page_block=block,
            image="vessels/page-block-images/explorer-lounge-second.jpg",
        )

        form = VesselPageBlockInlineForm(instance=block)

        self.assertIn("existing_additional_images", form.fields)
        self.assertEqual(list(form.fields["existing_additional_images"].choices), [
            (str(extra_image.pk), "explorer-lounge-second.jpg"),
        ])
        self.assertIn("explorer-lounge-second.jpg", form.as_p())
        self.assertIn("<img", form.as_p())
        self.assertIn(f'name="existing_additional_images" value="{extra_image.pk}"', form.as_p())
        self.assertIn('data-delete-image="true"', form.as_p())
        self.assertIn("删除图片", form.as_p())

    def test_content_card_editor_deletes_selected_additional_image_when_saved(self):
        vessel = Vessel.objects.create(slug="card-image-delete", name="多图删除测试船")
        block = VesselPageBlock.objects.create(
            vessel=vessel,
            block_type="card",
            title="Explorer Lounge & Bar",
            image="vessels/page-blocks/primary.jpg",
        )
        extra_image = VesselPageBlockImage.objects.create(
            vessel=vessel,
            page_block=block,
            image="vessels/page-block-images/explorer-lounge-second.jpg",
        )
        form = VesselPageBlockInlineForm(
            data={
                "block_type": "card",
                "title": block.title,
                "body": "",
                "is_visible": "on",
                "sort_order": "0",
                "existing_additional_images": [str(extra_image.pk)],
            },
            instance=block,
        )

        self.assertTrue(form.is_valid(), form.errors)
        form.save()

        self.assertFalse(VesselPageBlockImage.objects.filter(pk=extra_image.pk).exists())

    def test_page_composer_admin_script_renders_a_list_and_edits_rows_in_a_dialog(self):
        script = Path(__file__).resolve().parents[1] / "static/catalog/vessel-page-blocks-admin.js"
        source = script.read_text(encoding="utf-8")

        self.assertIn("data-page-block-list", source)
        self.assertIn('django.jQuery(document).on("formset:added", refresh)', source)
        self.assertIn('"additional_images"', source)
        self.assertIn('"existing_additional_images"', source)
        self.assertIn("data-delete-image", source)
        self.assertIn('input[type="checkbox"][name$="-DELETE"]', source)
        self.assertIn("openEditor", source)
        self.assertIn("moveBlock", source)
        self.assertIn("上移", source)
        self.assertIn("下移", source)
        self.assertIn("编辑", source)

    def test_vessel_editor_hides_manual_sort_fields_and_syncs_them_on_save(self):
        script = Path(__file__).resolve().parents[1] / "static/catalog/vessel-page-blocks-admin.js"
        stylesheet = Path(__file__).resolve().parents[1] / "static/catalog/admin-operations.css"

        self.assertIn("syncAllInlineSortOrders", script.read_text(encoding="utf-8"))
        self.assertIn('document.addEventListener("submit", syncAllInlineSortOrders)', script.read_text(encoding="utf-8"))
        self.assertIn("#vessel_form .inline-group .field-sort_order", stylesheet.read_text(encoding="utf-8"))

    def test_page_block_dialog_keeps_the_delete_state_hidden(self):
        template = Path(__file__).resolve().parents[1] / "templates/admin/catalog/vessel/page_blocks_inline.html"
        source = template.read_text(encoding="utf-8")

        self.assertIn('class="page-block-editor__delete-control"', source)
        self.assertNotIn("deletion_field.label_tag", source)

    def test_vessel_structured_facts_follow_the_editorial_order(self):
        vessel_admin = VesselAdmin(Vessel, site)
        structured_facts = next(options for title, options in vessel_admin.fieldsets if title == "结构化事实")

        self.assertEqual(
            structured_facts["fields"],
            (
                "is_hybrid",
                "has_science_center",
                "has_wifi",
                "has_stabilization_system",
                "restaurant_count",
                "bar_count",
                "has_fitness_center",
                "heated_pool_count",
                "has_infinity_pool",
                "has_sauna",
                "has_executive_lounge",
                "capacity",
                "year_built",
                "year_refurbished",
            ),
        )

    def test_vessel_publish_action_sets_status_and_publish_time(self):
        vessel = Vessel.objects.create(slug="roald-amundsen", name="阿蒙森号")
        request = RequestFactory().post("/admin/catalog/vessel/")
        request.user = get_user_model().objects.create_superuser(
            username="vessel-publisher",
            password="strong-password",
        )
        vessel_admin = VesselAdmin(Vessel, site)

        vessel_admin.publish_vessels(request, Vessel.objects.filter(pk=vessel.pk))

        vessel.refresh_from_db()
        self.assertEqual(vessel.content_status, VesselContentStatus.PUBLISHED)
        self.assertIsNotNone(vessel.published_at)


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


class VesselAdminFieldsTests(TestCase):
    def test_vessel_editor_hides_removed_and_audit_fields(self):
        editable_fields = {
            field
            for _, options in VesselAdmin.fieldsets
            for field in options["fields"]
        }

        self.assertNotIn("short_pitch", editable_fields)
        self.assertNotIn("features", editable_fields)
        self.assertNotIn("hero_image", editable_fields)
        self.assertNotIn("intro_en", editable_fields)
        self.assertNotIn("source_url", editable_fields)
        self.assertNotIn("source_fetched_at", editable_fields)
        self.assertNotIn("source_checked_at", editable_fields)
        self.assertNotIn("review_status", editable_fields)
        self.assertNotIn("created_at", editable_fields)
        self.assertNotIn("updated_at", editable_fields)
