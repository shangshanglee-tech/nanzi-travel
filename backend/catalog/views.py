import re

from django.http import JsonResponse
from django.utils.cache import patch_cache_control
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Destination, Product, SiteSettings
from .serializers import (
    DestinationSerializer,
    ProductCardSerializer,
    ProductDetailSerializer,
    SiteSettingsSerializer,
)


MONTH_PATTERN = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


def cache_public(response):
    patch_cache_control(response, public=True, max_age=60)
    return response


def error_response(code, message, status):
    return Response({"error": {"code": code, "message": message}}, status=status)


def healthz(request):
    return JsonResponse({"status": "ok"})


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
            }
        )
        return cache_public(response)


class ProductListView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
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
                .prefetch_related("departures", "itinerary_days", "images")
                .get(slug=slug)
            )
        except Product.DoesNotExist:
            return error_response("not_found", "产品不存在或尚未发布", 404)

        response = Response(
            ProductDetailSerializer(product, context={"request": request}).data
        )
        return cache_public(response)
