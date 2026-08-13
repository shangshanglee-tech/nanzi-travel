import json
import re
import shutil
import tempfile
from pathlib import Path

from django.conf import settings
from django.core.management import BaseCommand, CommandError, call_command


DESTINATION = {"name": "南极", "slug": "antarctica"}
SHIP_NAMES = {
    "fram": "MS Fram",
    "roald-amundsen": "MS Roald Amundsen",
    "fridtjof-nansen": "MS Fridtjof Nansen",
}


def normalize_day_number(value, fallback):
    match = re.search(r"\d+", str(value))
    return int(match.group()) if match else fallback


def departure_record(date_value, sort_order):
    return {
        "start_date": date_value,
        "end_date": None,
        "label": f"{date_value} 出发",
        "consultation_status": "咨询获取最新方案",
        "sort_order": sort_order,
    }


class Command(BaseCommand):
    help = "导入已授权的 HX 南极产品内容"

    def add_arguments(self, parser):
        parser.add_argument("source", type=Path)
        parser.add_argument("--heroes-dir", type=Path)
        parser.add_argument("--status", choices=("draft", "review", "published"), default="draft")

    def handle(self, *args, **options):
        source = options["source"]
        heroes_dir = options["heroes_dir"] or source.parent / "hx-heroes"
        try:
            payload = json.loads(source.read_text(encoding="utf-8"))
        except FileNotFoundError as error:
            raise CommandError(f"找不到 HX 导入文件：{source}") from error
        except json.JSONDecodeError as error:
            raise CommandError(f"HX 导入文件格式错误：{error}") from error

        products = payload.get("products")
        if not isinstance(products, list) or len(products) != 11:
            raise CommandError("HX 导入文件必须包含 11 条产品")

        normalized = {"products": [self.normalize_product(item, heroes_dir, index) for index, item in enumerate(products)]}
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as output:
            json.dump(normalized, output, ensure_ascii=False)
            temporary_path = Path(output.name)
        try:
            call_command("import_products", temporary_path, status=options["status"])
        finally:
            temporary_path.unlink(missing_ok=True)

    def normalize_product(self, item, heroes_dir, sort_order):
        slug = item.get("id")
        title = item.get("title")
        if not slug or not title:
            raise CommandError("HX 产品必须包含 id 和 title")
        hero_name = self.copy_hero(slug, heroes_dir)
        vessel = " / ".join(SHIP_NAMES.get(ship_id, ship_id) for ship_id in item.get("shipIds", []))
        departures = [departure_record(value, index) for index, value in enumerate(item.get("departures", []))]
        itinerary = [
            {
                "day_number": normalize_day_number(segment.get("day"), index + 1),
                "title": segment.get("title") or f"行程第 {index + 1} 段",
                "description": segment.get("description") or "具体行程以出发前确认内容为准。",
                "sort_order": index,
            }
            for index, segment in enumerate(item.get("itinerary", []))
        ]
        if not departures or not itinerary:
            raise CommandError(f"{slug} 缺少团期或行程")
        return {
            "slug": slug,
            "title": title,
            "subtitle": item.get("routeSummary", ""),
            "destination": DESTINATION,
            "summary": item.get("summary", ""),
            "season": "2026–2028 南极航季",
            "duration_days": item.get("durationDays"),
            "hero_image": hero_name,
            "vessel": vessel,
            "departure_city": "以具体团期为准",
            "tags": [item.get("group", "南极探险"), "HX Expeditions"],
            "highlights": item.get("highlights", []),
            "included": [],
            "excluded": [],
            "suitable_for": ["希望深度体验南极自然与野生动物的旅行者"],
            "notices": ["具体行程、船只安排和团期以咨询确认的方案为准。"],
            "departures": departures,
            "itinerary": itinerary,
            "images": [],
            "sort_order": sort_order,
        }

    def copy_hero(self, slug, heroes_dir):
        source = heroes_dir / slug / "hero.webp"
        if not source.is_file():
            raise CommandError(f"{slug} 缺少封面图：{source}")
        relative_name = Path("products/heroes") / f"hx-{slug}.webp"
        target = Path(settings.MEDIA_ROOT) / relative_name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        return relative_name.as_posix()
