from rest_framework import serializers

from .models import CabinType, Departure, Destination, ItineraryDay, Product, ProductImage, SiteSettings, Vessel


class DestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destination
        fields = ("name", "slug")


class VesselCardSerializer(serializers.ModelSerializer):
    hero_image = serializers.SerializerMethodField()

    class Meta:
        model = Vessel
        fields = ("slug", "name", "official_name", "summary", "hero_image", "capacity", "year_built", "features")

    def get_hero_image(self, vessel):
        if not vessel.hero_image:
            return ""
        request = self.context.get("request")
        url = vessel.hero_image.url
        return request.build_absolute_uri(url) if request else url


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
    vessel = VesselCardSerializer(read_only=True)

    class Meta:
        model = Departure
        fields = ("start_date", "end_date", "label", "consultation_status", "vessel")


class ItineraryDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = ItineraryDay
        fields = ("day_number", "source_range", "title", "description", "accommodation", "meals")


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
    vessels = VesselCardSerializer(many=True, read_only=True)
    departures = DepartureSerializer(many=True, read_only=True)
    itinerary_days = ItineraryDaySerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    consultation = serializers.SerializerMethodField()

    class Meta(ProductCardSerializer.Meta):
        fields = ProductCardSerializer.Meta.fields + (
            "vessel",
            "vessels",
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


class CabinTypeSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = CabinType
        fields = ("name", "category", "size_sqm", "bed_layout", "view_type", "summary", "highlights", "image")

    def get_image(self, cabin):
        if not cabin.image:
            return ""
        request = self.context.get("request")
        url = cabin.image.url
        return request.build_absolute_uri(url) if request else url


class VesselDetailSerializer(VesselCardSerializer):
    cabins = CabinTypeSerializer(many=True, read_only=True)
    products = ProductCardSerializer(many=True, read_only=True)

    class Meta(VesselCardSerializer.Meta):
        fields = VesselCardSerializer.Meta.fields + ("cabins", "products", "source_url")


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
