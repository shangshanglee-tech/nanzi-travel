import json
import re
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from catalog.models import CabinType, Departure, ItineraryDay, Product, Vessel


RANGE_PATTERN = re.compile(r"(?:Day|Days)\s*(\d+)(?:\s*-\s*(\d+))?", re.IGNORECASE)


def expanded_days(source_range):
    match = RANGE_PATTERN.fullmatch(source_range.strip())
    if not match:
        raise CommandError(f"无法识别行程区间：{source_range}")
    start = int(match.group(1))
    end = int(match.group(2) or start)
    if end < start:
        raise CommandError(f"行程区间结束日早于开始日：{source_range}")
    return range(start, end + 1)


class Command(BaseCommand):
    help = "导入已复核的 HX 极地中文内容、船只和执行船团期"

    def add_arguments(self, parser):
        parser.add_argument("source", type=Path)
        parser.add_argument(
            "--replace-source-data",
            action="store_true",
            help="用来源文件重置船只舱位、团期和逐日行程；会覆盖人工维护的数据。",
        )

    def handle(self, *args, **options):
        source = options["source"]
        try:
            payload = json.loads(source.read_text(encoding="utf-8"))
        except FileNotFoundError as error:
            raise CommandError(f"找不到极地内容文件：{source}") from error
        except json.JSONDecodeError as error:
            raise CommandError(f"极地内容文件格式错误：{error}") from error

        vessels = payload.get("vessels")
        products = payload.get("products")
        if not isinstance(vessels, list) or not isinstance(products, list):
            raise CommandError("内容文件必须包含 vessels 和 products 列表")

        with transaction.atomic():
            replace_source_data = options["replace_source_data"]
            vessel_by_slug = self.import_vessels(vessels, replace_source_data)
            for item in products:
                self.import_product(item, vessel_by_slug, replace_source_data)

        self.stdout.write(self.style.SUCCESS(f"极地内容导入完成：船只 {len(vessels)}，路线 {len(products)}"))

    def import_vessels(self, items, replace_source_data):
        vessels = {}
        for item in items:
            slug = item.get("slug")
            name = item.get("name")
            if not slug or not name:
                raise CommandError("船只必须包含 slug 和 name")
            defaults = {
                key: item.get(key, default)
                for key, default in (
                    ("official_name", ""), ("summary", ""), ("capacity", None), ("year_built", None),
                    ("features", []), ("source_url", ""), ("review_status", "pending"), ("sort_order", 0),
                )
            }
            defaults["name"] = name
            vessel, created = Vessel.objects.get_or_create(slug=slug, defaults=defaults)
            if replace_source_data and not created:
                for field, value in defaults.items():
                    setattr(vessel, field, value)
                vessel.save()
                vessel.cabins.all().delete()

            for index, cabin in enumerate(item.get("cabins", [])):
                cabin_defaults = {
                    "category": cabin.get("category", ""),
                    "size_sqm": cabin.get("size_sqm"),
                    "bed_layout": cabin.get("bed_layout", ""),
                    "view_type": cabin.get("view_type", ""),
                    "summary": cabin.get("summary", ""),
                    "highlights": cabin.get("highlights", []),
                    "source_url": cabin.get("source_url", ""),
                    "sort_order": index,
                }
                if replace_source_data:
                    CabinType.objects.update_or_create(
                        vessel=vessel,
                        name=cabin["name"],
                        defaults=cabin_defaults,
                    )
                else:
                    CabinType.objects.get_or_create(
                        vessel=vessel,
                        name=cabin["name"],
                        defaults=cabin_defaults,
                    )
            vessels[slug] = vessel
        return vessels

    def import_product(self, item, vessel_by_slug, replace_source_data):
        slug = item.get("slug")
        if not slug:
            raise CommandError("路线必须包含 slug")
        try:
            product = Product.objects.get(slug=slug)
        except Product.DoesNotExist as error:
            raise CommandError(f"路线不存在，不能补充内容：{slug}") from error

        vessel_slugs = item.get("vessel_slugs", [])
        vessels = []
        for vessel_slug in vessel_slugs:
            try:
                vessels.append(vessel_by_slug[vessel_slug])
            except KeyError as error:
                raise CommandError(f"{slug} 关联了未知船只：{vessel_slug}") from error
        if replace_source_data:
            product.vessels.set(vessels)
        else:
            product.vessels.add(*vessels)

        if replace_source_data:
            for field in ("summary", "subtitle", "season", "departure_city", "highlights", "tags", "suitable_for", "notices"):
                if field in item:
                    setattr(product, field, item[field])
            product.save()

        if replace_source_data:
            product.departures.all().delete()
        for index, departure in enumerate(item.get("departures", [])):
            vessel_slug = departure.get("vessel_slug")
            try:
                vessel = vessel_by_slug[vessel_slug]
            except KeyError as error:
                raise CommandError(f"{slug} 团期关联了未知船只：{vessel_slug}") from error
            departure_defaults = {
                "end_date": departure.get("end_date"),
                "label": departure.get("label", ""),
                "consultation_status": departure.get("consultation_status", "咨询获取最新方案"),
                "sort_order": index,
            }
            Departure.objects.update_or_create(
                product=product,
                vessel=vessel,
                start_date=departure.get("start_date"),
                defaults=departure_defaults,
            )

        if replace_source_data:
            product.itinerary_days.all().delete()
        for index, segment in enumerate(item.get("itinerary_segments", [])):
            source_range = segment.get("source_range", "")
            for day_number in expanded_days(source_range):
                itinerary_defaults = {
                    "source_range": source_range,
                    "title": segment.get("title", "探索之旅"),
                    "description": segment.get("description", "具体行程以当日天气与探险队安排为准。"),
                    "accommodation": segment.get("accommodation", ""),
                    "meals": segment.get("meals", ""),
                    "sort_order": index * 100 + day_number,
                }
                ItineraryDay.objects.update_or_create(
                    product=product,
                    day_number=day_number,
                    defaults=itinerary_defaults,
                )
