from django.contrib import admin
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.template.response import TemplateResponse
from django.utils import timezone

from .forms import ProductAdminForm, VesselDeckPlanInlineForm, VesselPageBlockInlineForm
from .models import (
    CabinDisplayGroup,
    CabinType,
    Departure,
    Destination,
    ItineraryDay,
    Product,
    ProductImage,
    ProductStatus,
    SiteSettings,
    Vessel,
    VesselDeckPlan,
    VesselExperience,
    VesselMedia,
    VesselPageBlock,
    VesselPageBlockImage,
)


class DepartureInline(admin.TabularInline):
    model = Departure
    extra = 0


class ItineraryDayInline(admin.StackedInline):
    model = ItineraryDay
    extra = 0


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0


class CabinTypeInline(admin.StackedInline):
    model = CabinType
    extra = 0


class CabinDisplayGroupInline(admin.StackedInline):
    model = CabinDisplayGroup
    filter_horizontal = ("cabins",)
    extra = 0


class VesselMediaInline(admin.TabularInline):
    model = VesselMedia
    extra = 0


class VesselPageBlockInline(admin.StackedInline):
    model = VesselPageBlock
    form = VesselPageBlockInlineForm
    template = "admin/catalog/vessel/page_blocks_inline.html"
    extra = 0
    fields = ("block_type", "title", "image", "additional_images", "existing_additional_images", "body", "is_visible", "sort_order")


class VesselDeckPlanInline(admin.StackedInline):
    model = VesselDeckPlan
    form = VesselDeckPlanInlineForm
    classes = ("vessel-deck-plan-inline",)
    template = "admin/catalog/vessel/deck_plans_inline.html"
    extra = 0
    fields = ("title", "image", "sort_order")


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "sort_order")
    list_editable = ("is_active", "sort_order")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    inlines = (DepartureInline, ItineraryDayInline, ProductImageInline)
    list_display = (
        "title",
        "destination",
        "season",
        "status",
        "sort_order",
        "published_at",
        "updated_at",
    )
    list_filter = ("status", "destination")
    search_fields = ("title", "subtitle", "summary", "slug")
    readonly_fields = ("created_at", "updated_at")
    prepopulated_fields = {"slug": ("title",)}
    actions = ("publish_products", "archive_products")

    @admin.action(description="发布所选产品")
    def publish_products(self, request, queryset):
        if request.POST.get("confirm") == "yes":
            queryset.update(
                status=ProductStatus.PUBLISHED,
                published_at=timezone.now(),
            )
            return None

        context = {
            **self.admin_site.each_context(request),
            "title": "确认发布产品",
            "products": queryset,
            "action_checkbox_name": ACTION_CHECKBOX_NAME,
            "opts": self.model._meta,
        }
        return TemplateResponse(request, "admin/catalog/confirm_publish.html", context)

    @admin.action(description="下架所选产品")
    def archive_products(self, request, queryset):
        queryset.update(status=ProductStatus.ARCHIVED)


@admin.register(Vessel)
class VesselAdmin(admin.ModelAdmin):
    change_form_template = "admin/catalog/vessel/change_form.html"
    inlines = (
        VesselPageBlockInline,
        CabinTypeInline,
        CabinDisplayGroupInline,
        VesselDeckPlanInline,
    )
    list_display = ("name", "official_name", "operator_name", "content_status", "published_at", "is_active", "updated_at")
    list_filter = ("content_status", "is_active", "operator_name")
    search_fields = ("name", "official_name", "operator_name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    actions = ("publish_vessels", "unpublish_vessels")
    fieldsets = (
        ("基础与发布", {"fields": ("name", "official_name", "operator_name", "slug", "content_status", "published_at", "is_active", "sort_order")}),
        ("中文展示文案", {"fields": ("summary", "intro_zh")}),
        ("首页卡片展示", {"fields": ("card_image", "card_tone")}),
        ("舱位", {"fields": ("show_cabins",)}),
        (
            "结构化事实",
            {
                "fields": (
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
                )
            },
        ),
    )

    @admin.action(description="发布所选船只内容")
    def publish_vessels(self, request, queryset):
        queryset.update(content_status="published", published_at=timezone.now())

    @admin.action(description="撤回为草稿")
    def unpublish_vessels(self, request, queryset):
        queryset.update(content_status="draft", published_at=None)

    class Media:
        css = {"all": ("catalog/admin-operations.css",)}
        js = ("catalog/vessel-page-blocks-admin.js", "catalog/deck-plan-upload-admin.js", "catalog/vessel-editor-tabs.js")


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    readonly_fields = ("updated_at",)

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()
