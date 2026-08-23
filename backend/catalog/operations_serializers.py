from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from .models import (
    Departure,
    Destination,
    ItineraryDay,
    Product,
    ProductImage,
    ProductStatus,
    Vessel,
    VesselContentStatus,
    CabinDisplayGroup,
    CabinType,
    Activity,
    ActivityImage,
    MediaAsset,
    VesselPageBlock,
    VesselPageBlockImage,
    VesselPageBlockType,
    VesselDeckPlan,
)


class OperationsDestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destination
        fields = ("id", "name", "slug")


class OperationsDepartureSerializer(serializers.ModelSerializer):
    vessel_id = serializers.PrimaryKeyRelatedField(
        queryset=Vessel.objects.all(), source="vessel", allow_null=True, required=False
    )

    class Meta:
        model = Departure
        fields = ("id", "label", "start_date", "end_date", "vessel_id", "consultation_status", "sort_order")
        read_only_fields = ("id", "sort_order")


class OperationsItineraryDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = ItineraryDay
        fields = ("id", "day_number", "source_range", "title", "description", "accommodation", "meals", "sort_order")
        read_only_fields = ("id", "sort_order")


class OperationsProductImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ("id", "image", "alt_text", "sort_order")

    def get_image(self, product_image):
        request = self.context.get("request")
        url = product_image.image.url
        return request.build_absolute_uri(url) if request else url


class OperationsProductSerializer(serializers.ModelSerializer):
    destination_id = serializers.PrimaryKeyRelatedField(queryset=Destination.objects.all(), source="destination")
    vessel_ids = serializers.PrimaryKeyRelatedField(queryset=Vessel.objects.all(), many=True, source="vessels", required=False)
    activity_ids = serializers.PrimaryKeyRelatedField(queryset=Activity.objects.all(), many=True, source="activities", required=False)
    departures = OperationsDepartureSerializer(many=True, required=False)
    itinerary_days = OperationsItineraryDaySerializer(many=True, required=False)
    hero_image = serializers.SerializerMethodField()
    images = OperationsProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = (
            "id", "title", "slug", "subtitle", "summary", "season", "duration_days", "vessel",
            "departure_city", "tags", "highlights", "included", "excluded", "suitable_for", "notices",
            "status", "sort_order", "published_at", "destination_id", "vessel_ids", "activity_ids", "departures", "itinerary_days",
            "hero_image", "images",
        )
        read_only_fields = ("id", "published_at")

    def get_hero_image(self, product):
        if not product.hero_image:
            return ""
        request = self.context.get("request")
        url = product.hero_image.url
        return request.build_absolute_uri(url) if request else url

    def _normalize_publication(self, values, instance=None):
        status = values.get("status", instance.status if instance else ProductStatus.DRAFT)
        if status == ProductStatus.PUBLISHED and not (instance and instance.published_at):
            values["published_at"] = timezone.now()
        elif status != ProductStatus.PUBLISHED:
            values["published_at"] = None

    def _save_nested(self, product, vessels, activities, departures, itinerary_days):
        if vessels is not None:
            product.vessels.set(vessels)
        if activities is not None:
            product.activities.set(activities)
        if departures is not None:
            product.departures.all().delete()
            Departure.objects.bulk_create(
                [Departure(product=product, sort_order=index, **departure) for index, departure in enumerate(departures)]
            )
        if itinerary_days is not None:
            product.itinerary_days.all().delete()
            ItineraryDay.objects.bulk_create(
                [ItineraryDay(product=product, sort_order=index, **day) for index, day in enumerate(itinerary_days)]
            )

    @transaction.atomic
    def create(self, validated_data):
        vessels = validated_data.pop("vessels", None)
        activities = validated_data.pop("activities", None)
        departures = validated_data.pop("departures", None)
        itinerary_days = validated_data.pop("itinerary_days", None)
        self._normalize_publication(validated_data)
        product = Product.objects.create(**validated_data)
        self._save_nested(product, vessels, activities, departures, itinerary_days)
        return product

    @transaction.atomic
    def update(self, instance, validated_data):
        vessels = validated_data.pop("vessels", None)
        activities = validated_data.pop("activities", None)
        departures = validated_data.pop("departures", None)
        itinerary_days = validated_data.pop("itinerary_days", None)
        self._normalize_publication(validated_data, instance)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        self._save_nested(instance, vessels, activities, departures, itinerary_days)
        return instance


class OperationsVesselSerializer(serializers.ModelSerializer):
    card_image = serializers.SerializerMethodField()

    class Meta:
        model = Vessel
        fields = (
            "id", "slug", "name", "official_name", "summary", "intro_zh", "operator_name",
            "card_image", "card_tone", "capacity", "year_built", "year_refurbished",
            "content_status", "published_at", "is_active", "show_cabins", "show_deck_plans", "sort_order",
            "is_hybrid", "has_science_center", "has_wifi", "has_stabilization_system",
            "restaurant_count", "bar_count", "has_fitness_center", "heated_pool_count",
            "has_infinity_pool", "has_sauna", "has_executive_lounge",
        )
        read_only_fields = ("id", "card_image", "published_at")

    def get_card_image(self, vessel):
        if not vessel.card_image:
            return ""
        request = self.context.get("request")
        url = vessel.card_image.url
        return request.build_absolute_uri(url) if request else url

    def validate(self, attrs):
        content_status = attrs.get("content_status", self.instance.content_status if self.instance else VesselContentStatus.DRAFT)
        if content_status == VesselContentStatus.PUBLISHED:
            has_card_image = bool(self.instance and self.instance.card_image)
            if not has_card_image:
                raise serializers.ValidationError({"content_status": "发布前请先上传卡片图"})
        return attrs

    def update(self, instance, validated_data):
        content_status = validated_data.get("content_status", instance.content_status)
        if content_status == VesselContentStatus.PUBLISHED and not instance.published_at:
            validated_data["published_at"] = timezone.now()
        elif content_status != VesselContentStatus.PUBLISHED:
            validated_data["published_at"] = None
        return super().update(instance, validated_data)


class OperationsVesselPageBlockImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = VesselPageBlockImage
        fields = ("id", "image", "sort_order")

    def get_image(self, block_image):
        request = self.context.get("request")
        url = block_image.image.url
        return request.build_absolute_uri(url) if request else url


class OperationsVesselPageBlockSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    additional_images = OperationsVesselPageBlockImageSerializer(many=True, read_only=True)

    class Meta:
        model = VesselPageBlock
        fields = ("id", "block_type", "title", "image", "body", "sort_order", "additional_images")
        read_only_fields = ("id", "image", "sort_order", "additional_images")

    def get_image(self, block):
        if not block.image:
            return ""
        request = self.context.get("request")
        url = block.image.url
        return request.build_absolute_uri(url) if request else url

    def validate(self, attrs):
        block_type = attrs.get("block_type", self.instance.block_type if self.instance else None)
        if block_type == VesselPageBlockType.HEADING:
            attrs["body"] = ""
        return attrs


class OperationsCabinSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = CabinType
        fields = (
            "id", "name", "official_code", "official_name", "category", "size_sqm", "bed_layout", "view_type",
            "summary", "description_zh", "description_en", "max_guests", "deck", "amenities", "display_tags",
            "is_accessible", "is_visible", "highlights", "image", "sort_order",
        )
        read_only_fields = ("id", "image", "sort_order")

    def get_image(self, cabin):
        if not cabin.image:
            return ""
        request = self.context.get("request")
        url = cabin.image.url
        return request.build_absolute_uri(url) if request else url


class OperationsCabinDisplayGroupSerializer(serializers.ModelSerializer):
    cabin_ids = serializers.PrimaryKeyRelatedField(queryset=CabinType.objects.all(), many=True, source="cabins", required=False)

    class Meta:
        model = CabinDisplayGroup
        fields = ("id", "slug", "title_zh", "title_en", "is_visible", "sort_order", "cabin_ids")
        read_only_fields = ("id", "sort_order")


class OperationsVesselDeckPlanSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = VesselDeckPlan
        fields = ("id", "title", "image", "sort_order")
        read_only_fields = ("id", "image", "sort_order")

    def get_image(self, deck_plan):
        request = self.context.get("request")
        url = deck_plan.image.url
        return request.build_absolute_uri(url) if request else url


class OperationsActivityImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ActivityImage
        fields = ("id", "image", "alt_text", "sort_order")

    def get_image(self, item):
        request = self.context.get("request")
        url = item.image.url
        return request.build_absolute_uri(url) if request else url


class OperationsMediaAssetSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = MediaAsset
        fields = ("id", "image", "title", "tags", "created_at")
        read_only_fields = ("id", "image", "created_at")

    def get_image(self, item):
        request = self.context.get("request")
        url = item.image.url
        return request.build_absolute_uri(url) if request else url


class OperationsActivitySerializer(serializers.ModelSerializer):
    destination_id = serializers.PrimaryKeyRelatedField(
        queryset=Destination.objects.all(), source="destination", allow_null=True, required=False
    )
    hero_image = serializers.SerializerMethodField()
    images = OperationsActivityImageSerializer(many=True, read_only=True)

    class Meta:
        model = Activity
        fields = ("id", "title", "content", "destination_id", "hero_image", "images", "status", "sort_order")
        read_only_fields = ("id", "hero_image", "images")

    def get_hero_image(self, item):
        if not item.hero_image:
            return ""
        request = self.context.get("request")
        url = item.hero_image.url
        return request.build_absolute_uri(url) if request else url
