import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from catalog.models import (
    Departure,
    Destination,
    ItineraryDay,
    Product,
    ProductImage,
    ProductStatus,
)


PRODUCT_FIELDS = {
    "slug",
    "title",
    "subtitle",
    "destination",
    "summary",
    "season",
    "duration_days",
    "hero_image",
    "vessel",
    "departure_city",
    "tags",
    "highlights",
    "included",
    "excluded",
    "suitable_for",
    "notices",
    "departures",
    "itinerary",
    "images",
    "sort_order",
}
DESTINATION_FIELDS = {"name", "slug"}
DEPARTURE_FIELDS = {"start_date", "end_date", "label", "consultation_status", "sort_order"}
ITINERARY_FIELDS = {"day_number", "title", "description", "accommodation", "meals", "sort_order"}
IMAGE_FIELDS = {"image", "alt_text", "sort_order"}
LIST_FIELDS = {"tags", "highlights", "included", "excluded", "suitable_for", "notices"}
REQUIRED_FIELDS = {"slug", "title", "destination", "summary", "duration_days", "itinerary", "departures"}


def reject_unknown_keys(item, allowed, location):
    unknown = set(item) - allowed
    if unknown:
        raise CommandError(f"{location} 包含未知字段：{', '.join(sorted(unknown))}")


def validate_payload(payload, status):
    if not isinstance(payload, dict) or not isinstance(payload.get("products"), list):
        raise CommandError("文件根节点必须包含 products 列表")
    for index, product in enumerate(payload["products"], start=1):
        location = f"products[{index}]"
        if not isinstance(product, dict):
            raise CommandError(f"{location} 必须是对象")
        reject_unknown_keys(product, PRODUCT_FIELDS, location)
        missing = REQUIRED_FIELDS - set(product)
        if missing:
            raise CommandError(f"{location} 缺少字段：{', '.join(sorted(missing))}")
        reject_unknown_keys(product["destination"], DESTINATION_FIELDS, f"{location}.destination")
        for field in LIST_FIELDS:
            value = product.get(field, [])
            if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
                raise CommandError(f"{location}.{field} 必须是无空白项的文字列表")
        for nested_name, allowed in (
            ("departures", DEPARTURE_FIELDS),
            ("itinerary", ITINERARY_FIELDS),
            ("images", IMAGE_FIELDS),
        ):
            values = product.get(nested_name, [])
            if not isinstance(values, list):
                raise CommandError(f"{location}.{nested_name} 必须是列表")
            for nested_index, value in enumerate(values, start=1):
                if not isinstance(value, dict):
                    raise CommandError(f"{location}.{nested_name}[{nested_index}] 必须是对象")
                reject_unknown_keys(value, allowed, f"{location}.{nested_name}[{nested_index}]")
        if status == ProductStatus.PUBLISHED:
            complete = (
                product.get("hero_image")
                and product.get("highlights")
                and product.get("itinerary")
                and product.get("notices")
            )
            if not complete:
                raise CommandError(f"{location} 未满足发布条件：封面图、亮点、行程和提醒均不能为空")


class Command(BaseCommand):
    help = "从标准 JSON 文件导入或更新旅行产品"

    def add_arguments(self, parser):
        parser.add_argument("file", type=Path)
        parser.add_argument(
            "--status",
            choices=[choice for choice, _ in ProductStatus.choices],
            default=ProductStatus.DRAFT,
        )

    def handle(self, *args, **options):
        source = options["file"]
        try:
            payload = json.loads(source.read_text(encoding="utf-8"))
        except FileNotFoundError as error:
            raise CommandError(f"找不到导入文件：{source}") from error
        except json.JSONDecodeError as error:
            raise CommandError(f"JSON 格式错误：{error}") from error

        status = options["status"]
        validate_payload(payload, status)
        created_count = 0
        updated_count = 0

        with transaction.atomic():
            for item in payload["products"]:
                destination_data = item["destination"]
                destination, _ = Destination.objects.update_or_create(
                    slug=destination_data["slug"],
                    defaults={"name": destination_data["name"]},
                )
                defaults = {
                    field: item.get(field, [] if field in LIST_FIELDS else "")
                    for field in (
                        "title",
                        "subtitle",
                        "summary",
                        "season",
                        "hero_image",
                        "vessel",
                        "departure_city",
                        "tags",
                        "highlights",
                        "included",
                        "excluded",
                        "suitable_for",
                        "notices",
                    )
                }
                defaults.update(
                    destination=destination,
                    duration_days=item["duration_days"],
                    sort_order=item.get("sort_order", 0),
                    status=status,
                    published_at=timezone.now() if status == ProductStatus.PUBLISHED else None,
                )
                product, created = Product.objects.update_or_create(
                    slug=item["slug"],
                    defaults=defaults,
                )
                created_count += int(created)
                updated_count += int(not created)

                product.departures.all().delete()
                Departure.objects.bulk_create(
                    [Departure(product=product, **value) for value in item.get("departures", [])]
                )
                product.itinerary_days.all().delete()
                ItineraryDay.objects.bulk_create(
                    [ItineraryDay(product=product, **value) for value in item.get("itinerary", [])]
                )
                product.images.all().delete()
                ProductImage.objects.bulk_create(
                    [ProductImage(product=product, **value) for value in item.get("images", [])]
                )

        self.stdout.write(
            self.style.SUCCESS(f"导入完成：新增 {created_count}，更新 {updated_count}，状态 {status}")
        )

