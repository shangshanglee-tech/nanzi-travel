import json
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from catalog.models import Vessel


CONTENT_TYPE_EXTENSIONS = {
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
}


class Command(BaseCommand):
    help = "下载官方图片并写入指定船只的封面图"

    default_source = Path(__file__).resolve().parents[2] / "data" / "hx-vessel-hero-images.json"

    def add_arguments(self, parser):
        parser.add_argument(
            "source",
            type=Path,
            nargs="?",
            default=self.default_source,
            help="包含 vessels[].slug 与 image_url 的 JSON 文件；默认使用随程序部署的 HX 图片清单",
        )

    def handle(self, *args, **options):
        source = options["source"]
        try:
            payload = json.loads(source.read_text(encoding="utf-8"))
        except FileNotFoundError as error:
            raise CommandError(f"找不到船只封面图文件：{source}") from error
        except json.JSONDecodeError as error:
            raise CommandError(f"船只封面图文件格式错误：{error}") from error

        items = payload.get("vessels")
        if not isinstance(items, list) or not items:
            raise CommandError("内容文件必须包含非空的 vessels 列表")

        with transaction.atomic():
            for item in items:
                self.import_hero(item)

        self.stdout.write(self.style.SUCCESS(f"船只封面图导入完成：{len(items)} 艘"))

    def import_hero(self, item):
        slug = item.get("slug")
        image_url = item.get("image_url")
        if not slug or not image_url:
            raise CommandError("每艘船必须包含 slug 和 image_url")
        if urlparse(image_url).scheme != "https":
            raise CommandError(f"{slug} 的封面图必须使用 HTTPS 地址")
        try:
            vessel = Vessel.objects.get(slug=slug)
        except Vessel.DoesNotExist as error:
            raise CommandError(f"找不到船只：{slug}") from error

        request = Request(image_url, headers={"User-Agent": "NanziTravel/1.0"})
        try:
            with urlopen(request, timeout=30) as response:
                content_type = response.headers.get("Content-Type", "").split(";", 1)[0].lower()
                extension = CONTENT_TYPE_EXTENSIONS.get(content_type)
                if not extension:
                    raise CommandError(f"{slug} 的封面图不是支持的图片格式：{content_type or '未知'}")
                image_bytes = response.read()
        except CommandError:
            raise
        except OSError as error:
            raise CommandError(f"下载 {slug} 封面图失败：{error}") from error

        if not image_bytes:
            raise CommandError(f"{slug} 的封面图内容为空")
        vessel.hero_image.save(f"{slug}.{extension}", ContentFile(image_bytes), save=True)
