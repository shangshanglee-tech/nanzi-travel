from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .storage import build_media_storage


class ProductStatus(models.TextChoices):
    DRAFT = "draft", "草稿"
    REVIEW = "review", "待审核"
    PUBLISHED = "published", "已发布"
    ARCHIVED = "archived", "已下架"


class VesselContentStatus(models.TextChoices):
    DRAFT = "draft", "草稿"
    PUBLISHED = "published", "已发布"


class ProductQuerySet(models.QuerySet):
    def public(self):
        return self.filter(
            status=ProductStatus.PUBLISHED,
            published_at__isnull=False,
        )


class VesselQuerySet(models.QuerySet):
    def public(self):
        return self.filter(
            is_active=True,
            content_status=VesselContentStatus.PUBLISHED,
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


class Vessel(models.Model):
    slug = models.SlugField("英文标识", max_length=100, unique=True)
    name = models.CharField("中文名称", max_length=120)
    official_name = models.CharField("官方名称", max_length=160, blank=True)
    summary = models.TextField("中文简介", blank=True)
    operator_name = models.CharField("所属公司", max_length=160, blank=True)
    ship_type = models.CharField("船型定位", max_length=160, blank=True)
    short_pitch = models.CharField("首页一句话卖点", max_length=220, blank=True)
    intro_zh = models.TextField("中文完整介绍", blank=True)
    intro_en = models.TextField("英文原文介绍", blank=True)
    hero_image = models.ImageField(
        "封面图",
        upload_to="vessels/heroes/",
        storage=build_media_storage,
        blank=True,
    )
    capacity = models.PositiveSmallIntegerField("载客人数", null=True, blank=True)
    year_built = models.PositiveSmallIntegerField("建造年份", null=True, blank=True)
    year_refurbished = models.PositiveSmallIntegerField("翻新年份", null=True, blank=True)
    features = models.JSONField("体验特色", default=list, blank=True)
    source_url = models.URLField("官方来源", blank=True)
    source_fetched_at = models.DateTimeField("抓取时间", null=True, blank=True)
    source_checked_at = models.DateTimeField("资料核对时间", null=True, blank=True)
    review_status = models.CharField("复核状态", max_length=32, default="pending")
    content_status = models.CharField(
        "内容发布状态",
        max_length=16,
        choices=VesselContentStatus.choices,
        default=VesselContentStatus.DRAFT,
    )
    published_at = models.DateTimeField("内容发布时间", null=True, blank=True)
    is_active = models.BooleanField("启用", default=True)
    sort_order = models.PositiveIntegerField("排序", default=0)
    created_at = models.DateTimeField("创建时间", default=timezone.now, editable=False)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    objects = VesselQuerySet.as_manager()

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "船只"
        verbose_name_plural = "船只"

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        if self.content_status == VesselContentStatus.PUBLISHED and not self.published_at:
            raise ValidationError({"published_at": "published_at 是发布船只内容的必填项"})


class CabinType(models.Model):
    vessel = models.ForeignKey(Vessel, related_name="cabins", on_delete=models.CASCADE)
    name = models.CharField("舱型名称", max_length=120)
    official_code = models.CharField("官方舱位代码", max_length=40, blank=True)
    official_name = models.CharField("官方舱位名称", max_length=160, blank=True)
    category = models.CharField("舱型分类", max_length=80, blank=True)
    size_sqm = models.DecimalField("面积（平方米）", max_digits=5, decimal_places=1, null=True, blank=True)
    bed_layout = models.CharField("床型", max_length=160, blank=True)
    view_type = models.CharField("窗景/阳台", max_length=120, blank=True)
    summary = models.TextField("中文简介", blank=True)
    description_zh = models.TextField("中文完整介绍", blank=True)
    description_en = models.TextField("英文原文介绍", blank=True)
    max_guests = models.PositiveSmallIntegerField("最多入住人数", null=True, blank=True)
    deck = models.CharField("甲板", max_length=120, blank=True)
    amenities = models.JSONField("设施", default=list, blank=True)
    display_tags = models.JSONField("展示标签", default=list, blank=True)
    is_accessible = models.BooleanField("无障碍舱位", default=False)
    is_visible = models.BooleanField("展示", default=True)
    highlights = models.JSONField("舱型亮点", default=list, blank=True)
    image = models.ImageField("图片", upload_to="vessels/cabins/", storage=build_media_storage, blank=True)
    source_url = models.URLField("官方来源", blank=True)
    source_checked_at = models.DateTimeField("资料核对时间", null=True, blank=True)
    sort_order = models.PositiveIntegerField("排序", default=0)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "舱位类型"
        verbose_name_plural = "舱位类型"

    def __str__(self):
        return f"{self.vessel} · {self.name}"


class VesselExperience(models.Model):
    vessel = models.ForeignKey(
        Vessel,
        verbose_name="船只",
        related_name="experiences",
        on_delete=models.CASCADE,
    )
    kind = models.CharField("模块类型", max_length=80, blank=True)
    title_zh = models.CharField("中文标题", max_length=160)
    title_en = models.CharField("英文标题", max_length=160, blank=True)
    body_zh = models.TextField("中文内容", blank=True)
    body_en = models.TextField("英文原文", blank=True)
    is_visible = models.BooleanField("展示", default=True)
    sort_order = models.PositiveIntegerField("排序", default=0)
    source_url = models.URLField("官方来源", blank=True)
    source_checked_at = models.DateTimeField("资料核对时间", null=True, blank=True)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "船上体验模块"
        verbose_name_plural = "船上体验模块"

    def __str__(self):
        return f"{self.vessel} · {self.title_zh}"


class CabinDisplayGroup(models.Model):
    vessel = models.ForeignKey(
        Vessel,
        verbose_name="船只",
        related_name="cabin_groups",
        on_delete=models.CASCADE,
    )
    slug = models.SlugField("分组标识", max_length=80)
    title_zh = models.CharField("中文分组名称", max_length=120)
    title_en = models.CharField("英文分组名称", max_length=120, blank=True)
    is_visible = models.BooleanField("展示", default=True)
    sort_order = models.PositiveIntegerField("排序", default=0)
    cabins = models.ManyToManyField(CabinType, related_name="display_groups", blank=True)

    class Meta:
        ordering = ["sort_order", "id"]
        constraints = [models.UniqueConstraint(fields=("vessel", "slug"), name="unique_vessel_cabin_group_slug")]
        verbose_name = "舱位展示分组"
        verbose_name_plural = "舱位展示分组"

    def __str__(self):
        return f"{self.vessel} · {self.title_zh}"


class VesselMedia(models.Model):
    vessel = models.ForeignKey(
        Vessel,
        verbose_name="船只",
        related_name="media",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    experience = models.ForeignKey(
        VesselExperience,
        verbose_name="船上体验模块",
        related_name="media",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    cabin = models.ForeignKey(
        CabinType,
        verbose_name="舱位",
        related_name="media",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    image = models.ImageField("图片", upload_to="vessels/gallery/", storage=build_media_storage)
    alt_zh = models.CharField("中文图片说明", max_length=180, blank=True)
    alt_en = models.CharField("英文图片说明", max_length=180, blank=True)
    source_url = models.URLField("图片来源", blank=True)
    source_note = models.CharField("原始说明", max_length=240, blank=True)
    usage_note = models.CharField("使用备注", max_length=240, blank=True)
    source_checked_at = models.DateTimeField("资料核对时间", null=True, blank=True)
    sort_order = models.PositiveIntegerField("排序", default=0)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "船只媒体资源"
        verbose_name_plural = "船只媒体资源"

    def clean(self):
        super().clean()
        parent_count = sum(parent is not None for parent in (self.vessel, self.experience, self.cabin))
        if parent_count != 1:
            raise ValidationError("一个媒体资源必须且只能关联一条船、一个体验模块或一个舱位。")

    def __str__(self):
        return self.alt_zh or self.alt_en or "船只图片"


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
    vessels = models.ManyToManyField(Vessel, related_name="products", blank=True)
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
    vessel = models.ForeignKey(
        Vessel,
        verbose_name="执行船只",
        related_name="departures",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
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
    source_range = models.CharField("官方行程区间", max_length=32, blank=True)
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


class EditorialCollection(models.Model):
    title = models.CharField("专题名称", max_length=120)
    slug = models.SlugField("英文标识", max_length=120, unique=True)
    summary = models.TextField("专题简介", blank=True)
    is_active = models.BooleanField("启用", default=True)
    sort_order = models.PositiveIntegerField("排序", default=0)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "内容专题"
        verbose_name_plural = "内容专题"

    def __str__(self):
        return self.title


class EditorialEntry(models.Model):
    collection = models.ForeignKey(EditorialCollection, related_name="entries", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name="editorial_entries", on_delete=models.CASCADE, null=True, blank=True)
    vessel = models.ForeignKey(Vessel, related_name="editorial_entries", on_delete=models.CASCADE, null=True, blank=True)
    sort_order = models.PositiveIntegerField("排序", default=0)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "专题内容"
        verbose_name_plural = "专题内容"

    def clean(self):
        super().clean()
        if bool(self.product) == bool(self.vessel):
            raise ValidationError("专题内容必须且只能关联一条路线或一艘船")


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
