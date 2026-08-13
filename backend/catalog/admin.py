from django.contrib import admin
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.template.response import TemplateResponse
from django.utils import timezone

from .forms import ProductAdminForm
from .models import (
    Departure,
    Destination,
    ItineraryDay,
    Product,
    ProductImage,
    ProductStatus,
    SiteSettings,
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


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    readonly_fields = ("updated_at",)

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()
