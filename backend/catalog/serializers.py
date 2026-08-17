from rest_framework import serializers

from .models import (
    CabinType,
    CabinDisplayGroup,
    Departure,
    Destination,
    ItineraryDay,
    Product,
    ProductImage,
    SiteSettings,
    Vessel,
    VesselDeckPlan,
    VesselExperience,
    VesselMedia,
    VesselPageBlock,
)


class DestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destination
        fields = ("name", "slug")


class VesselCardSerializer(serializers.ModelSerializer):
    card_image = serializers.SerializerMethodField()

    class Meta:
        model = Vessel
        fields = (
            "slug",
            "name",
            "official_name",
            "summary",
            "card_image",
            "card_tone",
            "capacity",
            "year_built",
        )

    def get_card_image(self, vessel):
        if not vessel.card_image:
            return ""
        request = self.context.get("request")
        url = vessel.card_image.url
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
    media = serializers.SerializerMethodField()

    class Meta:
        model = CabinType
        fields = (
            "name", "official_code", "official_name", "category", "size_sqm", "max_guests", "deck",
            "bed_layout", "view_type", "summary", "description_zh", "description_en", "amenities",
            "display_tags", "is_accessible", "highlights", "image", "media",
        )

    def get_image(self, cabin):
        if not cabin.image:
            return ""
        request = self.context.get("request")
        url = cabin.image.url
        return request.build_absolute_uri(url) if request else url

    def get_media(self, cabin):
        return VesselMediaSerializer(cabin.media.all(), many=True, context=self.context).data


class VesselMediaSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = VesselMedia
        fields = ("image", "alt_zh", "alt_en", "source_note")

    def get_image(self, media):
        request = self.context.get("request")
        url = media.image.url
        return request.build_absolute_uri(url) if request else url


class VesselExperienceSerializer(serializers.ModelSerializer):
    media = VesselMediaSerializer(many=True, read_only=True)

    class Meta:
        model = VesselExperience
        fields = ("kind", "title_zh", "title_en", "body_zh", "body_en", "media")


class VesselPageBlockSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = VesselPageBlock
        fields = ("block_type", "title", "image", "body")

    def get_image(self, block):
        if not block.image:
            return ""
        request = self.context.get("request")
        url = block.image.url
        return request.build_absolute_uri(url) if request else url


class VesselDeckPlanSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = VesselDeckPlan
        fields = ("title", "description", "image")

    def get_image(self, deck_plan):
        request = self.context.get("request")
        url = deck_plan.image.url
        return request.build_absolute_uri(url) if request else url


class CabinDisplayGroupSerializer(serializers.ModelSerializer):
    cabins = serializers.SerializerMethodField()

    class Meta:
        model = CabinDisplayGroup
        fields = ("slug", "title_zh", "title_en", "cabins")

    def get_cabins(self, group):
        cabins = [cabin for cabin in group.cabins.all() if cabin.is_visible]
        return CabinTypeSerializer(cabins, many=True, context=self.context).data


class VesselDetailSerializer(VesselCardSerializer):
    cabins = CabinTypeSerializer(many=True, read_only=True)
    experiences = serializers.SerializerMethodField()
    cabin_groups = serializers.SerializerMethodField()
    page_blocks = serializers.SerializerMethodField()
    deck_plans = serializers.SerializerMethodField()
    media = VesselMediaSerializer(many=True, read_only=True)
    products = ProductCardSerializer(many=True, read_only=True)

    class Meta(VesselCardSerializer.Meta):
        fields = VesselCardSerializer.Meta.fields + (
            "operator_name", "is_hybrid", "has_science_center", "has_wifi", "has_stabilization_system",
            "restaurant_count", "bar_count", "has_fitness_center", "heated_pool_count", "has_infinity_pool",
            "has_sauna", "has_executive_lounge", "intro_zh", "year_refurbished",
            "show_cabins", "show_deck_plans", "page_blocks", "deck_plans",
            "experiences", "cabin_groups", "cabins", "media", "products",
        )

    def get_experiences(self, vessel):
        experiences = [experience for experience in vessel.experiences.all() if experience.is_visible]
        return VesselExperienceSerializer(experiences, many=True, context=self.context).data

    def get_page_blocks(self, vessel):
        blocks = [block for block in vessel.page_blocks.all() if block.is_visible]
        return VesselPageBlockSerializer(blocks, many=True, context=self.context).data

    def get_deck_plans(self, vessel):
        if not vessel.show_deck_plans:
            return []
        plans = [deck_plan for deck_plan in vessel.deck_plans.all() if deck_plan.is_visible]
        return VesselDeckPlanSerializer(plans, many=True, context=self.context).data

    def get_cabin_groups(self, vessel):
        groups = [group for group in vessel.cabin_groups.all() if group.is_visible]
        visible_groups = [
            group for group in groups
            if any(cabin.is_visible for cabin in group.cabins.all())
        ]
        payload = CabinDisplayGroupSerializer(visible_groups, many=True, context=self.context).data
        grouped_cabin_ids = {
            cabin.pk
            for group in visible_groups
            for cabin in group.cabins.all()
        }
        ungrouped = [
            cabin for cabin in vessel.cabins.all()
            if cabin.is_visible and cabin.pk not in grouped_cabin_ids
        ]
        if ungrouped:
            payload.append({
                "slug": "other",
                "title_zh": "其他舱位",
                "title_en": "Other cabins",
                "cabins": CabinTypeSerializer(ungrouped, many=True, context=self.context).data,
            })
        return payload


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
