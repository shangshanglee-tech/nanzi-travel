from rest_framework import serializers

from .models import Departure, Destination, ItineraryDay, Product, ProductImage, SiteSettings


class DestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destination
        fields = ("name", "slug")


class ProductCardSerializer(serializers.ModelSerializer):
    destination = DestinationSerializer(read_only=True)
    hero_image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "title",
            "slug",
            "subtitle",
            "summary",
            "season",
            "duration_days",
            "hero_image",
            "destination",
            "tags",
            "highlights",
        )

    def get_hero_image(self, product):
        if not product.hero_image:
            return ""
        request = self.context.get("request")
        url = product.hero_image.url
        return request.build_absolute_uri(url) if request else url


class DepartureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departure
        fields = ("start_date", "end_date", "label", "consultation_status")


class ItineraryDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = ItineraryDay
        fields = ("day_number", "title", "description", "accommodation", "meals")


class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ("image", "alt_text")

    def get_image(self, product_image):
        request = self.context.get("request")
        url = product_image.image.url
        return request.build_absolute_uri(url) if request else url


class ProductDetailSerializer(ProductCardSerializer):
    departures = DepartureSerializer(many=True, read_only=True)
    itinerary_days = ItineraryDaySerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    consultation = serializers.SerializerMethodField()

    class Meta(ProductCardSerializer.Meta):
        fields = ProductCardSerializer.Meta.fields + (
            "vessel",
            "departure_city",
            "departures",
            "itinerary_days",
            "images",
            "included",
            "excluded",
            "suitable_for",
            "notices",
            "consultation",
        )

    def get_consultation(self, product):
        return {
            "product_title": product.title,
            "copy": f"我想咨询：{product.title}",
        }


class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = (
            "brand_name",
            "brand_summary",
            "official_account_name",
            "official_account_guide",
            "service_description",
            "about_us",
            "agreement_text",
            "privacy_text",
            "filing_number",
        )

