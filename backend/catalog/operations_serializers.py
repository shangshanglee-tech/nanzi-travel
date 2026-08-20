from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from .models import Departure, Destination, ItineraryDay, Product, ProductStatus, Vessel


class OperationsDestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destination
        fields = ("id", "name", "slug", "is_active", "sort_order")


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


class OperationsProductSerializer(serializers.ModelSerializer):
    destination_id = serializers.PrimaryKeyRelatedField(queryset=Destination.objects.all(), source="destination")
    vessel_ids = serializers.PrimaryKeyRelatedField(queryset=Vessel.objects.all(), many=True, source="vessels", required=False)
    departures = OperationsDepartureSerializer(many=True, required=False)
    itinerary_days = OperationsItineraryDaySerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = (
            "id", "title", "slug", "subtitle", "summary", "season", "duration_days", "vessel",
            "departure_city", "tags", "highlights", "included", "excluded", "suitable_for", "notices",
            "status", "sort_order", "published_at", "destination_id", "vessel_ids", "departures", "itinerary_days",
        )
        read_only_fields = ("id", "published_at")

    def _normalize_publication(self, values, instance=None):
        status = values.get("status", instance.status if instance else ProductStatus.DRAFT)
        if status == ProductStatus.PUBLISHED and not (instance and instance.published_at):
            values["published_at"] = timezone.now()
        elif status != ProductStatus.PUBLISHED:
            values["published_at"] = None

    def _save_nested(self, product, vessels, departures, itinerary_days):
        if vessels is not None:
            product.vessels.set(vessels)
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
        departures = validated_data.pop("departures", None)
        itinerary_days = validated_data.pop("itinerary_days", None)
        self._normalize_publication(validated_data)
        product = Product.objects.create(**validated_data)
        self._save_nested(product, vessels, departures, itinerary_days)
        return product

    @transaction.atomic
    def update(self, instance, validated_data):
        vessels = validated_data.pop("vessels", None)
        departures = validated_data.pop("departures", None)
        itinerary_days = validated_data.pop("itinerary_days", None)
        self._normalize_publication(validated_data, instance)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        self._save_nested(instance, vessels, departures, itinerary_days)
        return instance
