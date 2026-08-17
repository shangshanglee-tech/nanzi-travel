import json
from pathlib import Path

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from catalog.models import Vessel


class Command(BaseCommand):
    help = "导入船只的首页卡片图和卡片底色"

    default_source = Path(__file__).resolve().parents[2] / "data" / "card-visuals" / "vessel-card-visuals.json"

    def add_arguments(self, parser):
        parser.add_argument(
            "source",
            type=Path,
            nargs="?",
            default=self.default_source,
            help="包含 vessels[].slug、card_image、card_tone 的 JSON 文件",
        )

    def handle(self, *args, **options):
        source = options["source"]
        try:
            payload = json.loads(source.read_text(encoding="utf-8"))
        except FileNotFoundError as error:
            raise CommandError(f"找不到船只卡片视觉文件：{source}") from error
        except json.JSONDecodeError as error:
            raise CommandError(f"船只卡片视觉文件格式错误：{error}") from error

        items = payload.get("vessels")
        if not isinstance(items, list) or not items:
            raise CommandError("内容文件必须包含非空的 vessels 列表")

        with transaction.atomic():
            for item in items:
                self.import_visual(source.parent, item)

        self.stdout.write(self.style.SUCCESS(f"船只卡片视觉导入完成：{len(items)} 艘"))

    def import_visual(self, source_directory, item):
        slug = item.get("slug")
        image_name = item.get("card_image")
        card_tone = item.get("card_tone", "")
        if not slug or not image_name or not card_tone:
            raise CommandError("每艘船必须包含 slug、card_image 和 card_tone")

        image_path = source_directory / image_name
        if image_path.parent != source_directory or not image_path.is_file():
            raise CommandError(f"{slug} 的卡片图不存在或路径不安全：{image_name}")

        try:
            vessel = Vessel.objects.get(slug=slug)
        except Vessel.DoesNotExist as error:
            raise CommandError(f"找不到船只：{slug}") from error

        vessel.card_tone = card_tone
        if vessel.card_image:
            vessel.card_image.delete(save=False)
        vessel.card_image.save(image_path.name, ContentFile(image_path.read_bytes()), save=False)
        try:
            vessel.full_clean()
        except Exception as error:
            raise CommandError(f"{slug} 的卡片图或底色无效") from error
        vessel.save(update_fields=("card_image", "card_tone", "updated_at"))
