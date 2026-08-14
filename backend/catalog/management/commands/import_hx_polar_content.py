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
            vessel_by_slug = self.import_vessels(vessels)
            for item in products:
                self.import_product(item, vessel_by_slug)

        self.stdout.write(self.style.SUCCESS(f"极地内容导入完成：船只 {len(vessels)}，路线 {len(products)}"))

    def import_vessels(self, items):
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
            vessel, _ = Vessel.objects.update_or_create(slug=slug, defaults=defaults)
            vessel.cabins.all().delete()
            CabinType.objects.bulk_create([
                CabinType(
                    vessel=vessel,
                    name=cabin["name"],
                    category=cabin.get("category", ""),
                    size_sqm=cabin.get("size_sqm"),
                    bed_layout=cabin.get("bed_layout", ""),
                    view_type=cabin.get("view_type", ""),
                    summary=cabin.get("summary", ""),
                    highlights=cabin.get("highlights", []),
                    source_url=cabin.get("source_url", ""),
                    sort_order=index,
                )
                for index, cabin in enumerate(item.get("cabins", []))
            ])
            vessels[slug] = vessel
        return vessels

    def import_product(self, item, vessel_by_slug):
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
        product.vessels.set(vessels)

        for field in ("summary", "subtitle", "season", "departure_city", "highlights", "tags", "suitable_for", "notices"):
            if field in item:
                setattr(product, field, item[field])
        product.save()

        product.departures.all().delete()
        departures = []
        for index, departure in enumerate(item.get("departures", [])):
            vessel_slug = departure.get("vessel_slug")
            try:
                vessel = vessel_by_slug[vessel_slug]
            except KeyError as error:
                raise CommandError(f"{slug} 团期关联了未知船只：{vessel_slug}") from error
            departures.append(Departure(
                product=product,
                vessel=vessel,
                start_date=departure.get("start_date"),
                end_date=departure.get("end_date"),
                label=departure.get("label", ""),
                consultation_status=departure.get("consultation_status", "咨询获取最新方案"),
                sort_order=index,
            ))
        Departure.objects.bulk_create(departures)

        product.itinerary_days.all().delete()
        days = []
        for index, segment in enumerate(item.get("itinerary_segments", [])):
            source_range = segment.get("source_range", "")
            for day_number in expanded_days(source_range):
                days.append(ItineraryDay(
                    product=product,
                    day_number=day_number,
                    source_range=source_range,
                    title=segment.get("title", "探索之旅"),
                    description=segment.get("description", "具体行程以当日天气与探险队安排为准。"),
                    accommodation=segment.get("accommodation", ""),
                    meals=segment.get("meals", ""),
                    sort_order=index * 100 + day_number,
                ))
        ItineraryDay.objects.bulk_create(days)
