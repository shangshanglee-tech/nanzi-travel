import re
from pathlib import Path

from django.http import HttpResponse, JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import render
from django.utils.cache import patch_cache_control
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Destination, Product, SiteSettings, Vessel
from .serializers import (
    DestinationSerializer,
    ProductCardSerializer,
    ProductDetailSerializer,
    SiteSettingsSerializer,
    VesselCardSerializer,
    VesselDetailSerializer,
)


MONTH_PATTERN = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
ICON_TONE_PATTERN = re.compile(r"^[0-9A-Fa-f]{6}$")
VESSEL_ICON_DIRECTORY = Path(__file__).resolve().parent / "static" / "catalog" / "vessel-icons"
VESSEL_ICON_NAMES = frozenset(
    {
        "verified-badge",
        "capacity",
        "science_center",
        "wifi",
        "hybrid",
        "modern_stable_tech",
        "restaurants",
        "bars",
        "lounge",
        "spa",
        "swimming_pool",
        "hot_tubs",
        "fitness",
    }
)


def cache_public(response):
    patch_cache_control(response, public=True, max_age=60)
    return response


def error_response(code, message, status):
    return Response({"error": {"code": code, "message": message}}, status=status)


def healthz(request):
    return JsonResponse({"status": "ok"})


def operations_console(request):
    return render(
        request,
        "operations/index.html",
        {"csrf_token_value": get_token(request)},
    )


def build_filter_options(products):
    destinations = {}
    months = set()
    durations = set()
    tags = []
    seen_tags = set()
    for product in products:
        destinations[product.destination.slug] = {
            "name": product.destination.name,
            "slug": product.destination.slug,
        }
        if product.duration_days:
            durations.add(product.duration_days)
        for departure in product.departures.all():
            if departure.start_date:
                months.add(departure.start_date.strftime("%Y-%m"))
        for tag in product.tags:
            if tag not in seen_tags:
                tags.append(tag)
                seen_tags.add(tag)
    return {
        "destinations": list(destinations.values()),
        "months": sorted(months),
        "durations": sorted(durations),
        "tags": tags,
    }


class SiteView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        settings = SiteSettings.objects.first() or SiteSettings()
        return cache_public(Response(SiteSettingsSerializer(settings).data))


class HomeView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        products = Product.objects.public().select_related("destination")[:8]
        vessels = Vessel.objects.public().prefetch_related("products")[:3]
        public_destination_ids = products.values_list("destination_id", flat=True)
        destinations = Destination.objects.filter(
            is_active=True,
            id__in=public_destination_ids,
        )
        response = Response(
            {
                "featured_products": ProductCardSerializer(
                    products,
                    many=True,
                    context={"request": request},
                ).data,
                "destinations": DestinationSerializer(destinations, many=True).data,
                "featured_vessels": VesselCardSerializer(vessels, many=True, context={"request": request}).data,
            }
        )
        return cache_public(response)


class ProductListView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        base_queryset = Product.objects.public().select_related("destination").prefetch_related("departures")
        filter_options = build_filter_options(base_queryset)
        queryset = Product.objects.public().select_related("destination")
        month = request.query_params.get("month", "")
        if month and not MONTH_PATTERN.fullmatch(month):
            return error_response("invalid_filter", "出发月份格式应为 YYYY-MM", 400)
        if month:
            year, month_number = (int(value) for value in month.split("-"))
            queryset = queryset.filter(
                departures__start_date__year=year,
                departures__start_date__month=month_number,
            )

        destination = request.query_params.get("destination")
        if destination:
            queryset = queryset.filter(destination__slug=destination)

        for parameter, lookup in (
            ("duration_min", "duration_days__gte"),
            ("duration_max", "duration_days__lte"),
        ):
            value = request.query_params.get(parameter)
            if value:
                if not value.isdigit():
                    return error_response("invalid_filter", "行程天数必须是整数", 400)
                queryset = queryset.filter(**{lookup: int(value)})

        tag = request.query_params.get("tag")
        queryset = queryset.distinct()
        if tag:
            queryset = [product for product in queryset if tag in product.tags]
        response = Response(
            {
                "filters": filter_options,
                "results": ProductCardSerializer(
                    queryset,
                    many=True,
                    context={"request": request},
                ).data
            }
        )
        return cache_public(response)


class ProductDetailView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, slug):
        try:
            product = (
                Product.objects.public()
                .select_related("destination")
                .prefetch_related("vessels", "departures__vessel", "itinerary_days", "images")
                .get(slug=slug)
            )
        except Product.DoesNotExist:
            return error_response("not_found", "产品不存在或尚未发布", 404)

        response = Response(
            ProductDetailSerializer(product, context={"request": request}).data
        )
        return cache_public(response)


class VesselListView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        vessels = Vessel.objects.public()
        return cache_public(Response({"results": VesselCardSerializer(vessels, many=True, context={"request": request}).data}))


class VesselIconView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, icon):
        tone = request.query_params.get("tone", "143f35")
        if icon not in VESSEL_ICON_NAMES or not ICON_TONE_PATTERN.fullmatch(tone):
            return error_response("not_found", "图标不存在", 404)

        source = VESSEL_ICON_DIRECTORY / f"{icon}.svg"
        if not source.is_file():
            return error_response("not_found", "图标不存在", 404)

        svg = source.read_text(encoding="utf-8").replace("#323332", f"#{tone.upper()}")
        response = HttpResponse(svg, content_type="image/svg+xml")
        patch_cache_control(response, public=True, max_age=86400)
        return response


class VesselDetailView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, slug):
        try:
            vessel = Vessel.objects.public().prefetch_related(
                "media", "experiences__media", "page_blocks__additional_images", "cabins__media",
                "cabin_groups__cabins__media", "products__destination"
            ).get(slug=slug)
        except Vessel.DoesNotExist:
            return error_response("not_found", "船只不存在或暂未开放", 404)
        return cache_public(Response(VesselDetailSerializer(vessel, context={"request": request}).data))
