from django.core.exceptions import ValidationError
from django.db import models

from .storage import build_media_storage


class ProductStatus(models.TextChoices):
    DRAFT = "draft", "草稿"
    REVIEW = "review", "待审核"
    PUBLISHED = "published", "已发布"
    ARCHIVED = "archived", "已下架"


class ProductQuerySet(models.QuerySet):
    def public(self):
        return self.filter(
            status=ProductStatus.PUBLISHED,
            published_at__isnull=False,
        )


class Destination(models.Model):
    name = models.CharField("目的地名称", max_length=80)
    slug = models.SlugField("英文标识", max_length=80, unique=True)
    is_active = models.BooleanField("启用", default=True)
    sort_order = models.PositiveIntegerField("排序", default=0)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "目的地"
        verbose_name_plural = "目的地"

    def __str__(self):
        return self.name


class Product(models.Model):
    destination = models.ForeignKey(
        Destination,
        verbose_name="目的地",
        related_name="products",
        on_delete=models.PROTECT,
    )
    title = models.CharField("产品名称", max_length=160)
    slug = models.SlugField("英文标识", max_length=180, unique=True)
    subtitle = models.CharField("简短副标题", max_length=220, blank=True)
    summary = models.TextField("产品简介", blank=True)
    season = models.CharField("航季/季节", max_length=100, blank=True)
    duration_days = models.PositiveSmallIntegerField("行程天数", null=True, blank=True)
    hero_image = models.ImageField(
        "封面图",
        upload_to="products/heroes/",
        storage=build_media_storage,
        blank=True,
    )
    vessel = models.CharField("船只/核心资源", max_length=160, blank=True)
    departure_city = models.CharField("出发地", max_length=100, blank=True)
    tags = models.JSONField("标签", default=list, blank=True)
    highlights = models.JSONField("产品亮点", default=list, blank=True)
    included = models.JSONField("费用包含", default=list, blank=True)
    excluded = models.JSONField("费用不含", default=list, blank=True)
    suitable_for = models.JSONField("适合人群", default=list, blank=True)
    notices = models.JSONField("重要提醒", default=list, blank=True)
    status = models.CharField(
        "发布状态",
        max_length=16,
        choices=ProductStatus.choices,
        default=ProductStatus.DRAFT,
    )
    sort_order = models.PositiveIntegerField("排序", default=0)
    published_at = models.DateTimeField("发布时间", null=True, blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    objects = ProductQuerySet.as_manager()

    class Meta:
        ordering = ["sort_order", "-published_at", "id"]
        verbose_name = "旅行产品"
        verbose_name_plural = "旅行产品"

    def clean(self):
        super().clean()
        if self.status == ProductStatus.PUBLISHED and not self.published_at:
            raise ValidationError({"published_at": "published_at 是发布产品的必填项"})

    def __str__(self):
        return self.title


class Departure(models.Model):
    product = models.ForeignKey(
        Product,
        verbose_name="产品",
        related_name="departures",
        on_delete=models.CASCADE,
    )
    start_date = models.DateField("出发日期", null=True, blank=True)
    end_date = models.DateField("结束日期", null=True, blank=True)
    label = models.CharField("团期说明", max_length=160, blank=True)
    consultation_status = models.CharField("咨询状态", max_length=80, default="可咨询")
    sort_order = models.PositiveIntegerField("排序", default=0)

    class Meta:
        ordering = ["sort_order", "start_date", "id"]
        verbose_name = "出发团期"
        verbose_name_plural = "出发团期"

    def __str__(self):
        return self.label or str(self.start_date or "待定团期")


class ItineraryDay(models.Model):
    product = models.ForeignKey(
        Product,
        verbose_name="产品",
        related_name="itinerary_days",
        on_delete=models.CASCADE,
    )
    day_number = models.PositiveSmallIntegerField("第几天")
    title = models.CharField("行程标题", max_length=180)
    description = models.TextField("行程内容")
    accommodation = models.CharField("住宿", max_length=160, blank=True)
    meals = models.CharField("餐食", max_length=120, blank=True)
    sort_order = models.PositiveIntegerField("排序", default=0)

    class Meta:
        ordering = ["sort_order", "day_number", "id"]
        verbose_name = "每日行程"
        verbose_name_plural = "每日行程"

    def __str__(self):
        return f"第{self.day_number}天 · {self.title}"


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        verbose_name="产品",
        related_name="images",
        on_delete=models.CASCADE,
    )
    image = models.ImageField(
        "图片",
        upload_to="products/gallery/",
        storage=build_media_storage,
    )
    alt_text = models.CharField("图片说明", max_length=180, blank=True)
    sort_order = models.PositiveIntegerField("排序", default=0)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "产品图片"
        verbose_name_plural = "产品图片"

    def __str__(self):
        return self.alt_text or f"{self.product} 图片"


class SiteSettings(models.Model):
    brand_name = models.CharField("品牌名称", max_length=100, default="小楠子爱旅行")
    brand_summary = models.TextField("品牌介绍", blank=True)
    official_account_name = models.CharField(
        "公众号名称",
        max_length=100,
        default="小楠子爱旅行俱乐部",
    )
    official_account_guide = models.TextField("公众号关注指引", blank=True)
    service_description = models.TextField("服务说明", blank=True)
    about_us = models.TextField("关于我们", blank=True)
    agreement_text = models.TextField("用户协议", blank=True)
    privacy_text = models.TextField("隐私政策", blank=True)
    filing_number = models.CharField("备案号", max_length=100, blank=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "站点设置"
        verbose_name_plural = "站点设置"

    def save(self, *args, **kwargs):
        self.pk = 1
        kwargs.pop("force_insert", None)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.brand_name
