import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from catalog.models import (
    CabinDisplayGroup,
    CabinType,
    Vessel,
    VesselContentStatus,
    VesselExperience,
)


class Command(BaseCommand):
    help = "导入单艘船的可编辑内容；按自然键更新，不删除人工数据。"

    def add_arguments(self, parser):
        parser.add_argument("source", type=Path)
        parser.add_argument("--publish", action="store_true", help="导入成功后发布船只内容。")

    def handle(self, *args, **options):
        source = options["source"]
        try:
            payload = json.loads(source.read_text(encoding="utf-8"))
        except FileNotFoundError as error:
            raise CommandError(f"找不到船只内容文件：{source}") from error
        except json.JSONDecodeError as error:
            raise CommandError(f"船只内容文件格式错误：{error}") from error

        item = payload.get("vessel")
        if not isinstance(item, dict) or not item.get("slug") or not item.get("name"):
            raise CommandError("内容文件必须包含 vessel.slug 和 vessel.name")

        with transaction.atomic():
            vessel = self.import_vessel(item)
            cabins = self.import_cabins(vessel, payload.get("cabins", []))
            self.import_experiences(vessel, payload.get("experiences", []))
            self.import_groups(vessel, payload.get("cabin_groups", []), cabins)
            if options["publish"]:
                vessel.content_status = VesselContentStatus.PUBLISHED
                vessel.published_at = timezone.now()
                vessel.save(update_fields=["content_status", "published_at", "updated_at"])

        self.stdout.write(
            self.style.SUCCESS(
                f"船只内容导入完成：{vessel.name}，体验 {vessel.experiences.count()}，舱位 {len(cabins)}"
            )
        )

    def import_vessel(self, item):
        allowed = (
            "official_name", "summary", "operator_name", "is_hybrid", "has_science_center", "has_wifi",
            "has_stabilization_system", "restaurant_count", "bar_count", "has_fitness_center",
            "heated_pool_count", "has_infinity_pool", "has_sauna", "has_executive_lounge",
            "intro_zh", "capacity", "year_built", "year_refurbished", "sort_order", "card_tone",
        )
        defaults = {"name": item["name"]}
        for field in allowed:
            if field in item:
                defaults[field] = item[field]
        vessel, _ = Vessel.objects.update_or_create(slug=item["slug"], defaults=defaults)
        return vessel

    def import_experiences(self, vessel, items):
        if not isinstance(items, list):
            raise CommandError("experiences 必须是列表")
        for index, item in enumerate(items):
            kind = item.get("kind")
            title_zh = item.get("title_zh")
            if not kind or not title_zh:
                raise CommandError("每个体验模块必须包含 kind 和 title_zh")
            defaults = {
                key: item.get(key, default)
                for key, default in (
                    ("title_en", ""), ("body_zh", ""), ("body_en", ""), ("is_visible", True),
                    ("source_url", ""), ("sort_order", index),
                )
            }
            VesselExperience.objects.update_or_create(
                vessel=vessel, kind=kind, defaults={"title_zh": title_zh, **defaults}
            )

    def import_cabins(self, vessel, items):
        if not isinstance(items, list):
            raise CommandError("cabins 必须是列表")
        cabins = {}
        for index, item in enumerate(items):
            code = item.get("official_code")
            name = item.get("name")
            if not code or not name:
                raise CommandError("每个舱位必须包含 official_code 和 name")
            defaults = {
                key: item.get(key, default)
                for key, default in (
                    ("official_name", ""), ("category", ""), ("size_sqm", None), ("bed_layout", ""),
                    ("view_type", ""), ("summary", ""), ("description_zh", ""), ("description_en", ""),
                    ("max_guests", None), ("deck", ""), ("amenities", []), ("display_tags", []),
                    ("is_accessible", False), ("is_visible", True), ("highlights", []),
                    ("source_url", ""), ("sort_order", index),
                )
            }
            cabin, _ = CabinType.objects.update_or_create(
                vessel=vessel, official_code=code, defaults={"name": name, **defaults}
            )
            cabins[code] = cabin
        return cabins

    def import_groups(self, vessel, items, cabins):
        if not isinstance(items, list):
            raise CommandError("cabin_groups 必须是列表")
        for index, item in enumerate(items):
            slug = item.get("slug")
            title_zh = item.get("title_zh")
            if not slug or not title_zh:
                raise CommandError("每个舱位分组必须包含 slug 和 title_zh")
            codes = item.get("cabin_codes", [])
            missing = [code for code in codes if code not in cabins]
            if missing:
                raise CommandError(f"舱位分组 {slug} 引用了不存在的代码：{', '.join(missing)}")
            group, _ = CabinDisplayGroup.objects.update_or_create(
                vessel=vessel,
                slug=slug,
                defaults={
                    "title_zh": title_zh,
                    "title_en": item.get("title_en", ""),
                    "is_visible": item.get("is_visible", True),
                    "sort_order": item.get("sort_order", index),
                },
            )
            group.cabins.set([cabins[code] for code in codes])
